"""
Kafka consumer for incremental recommendation matrix updates.

Subscribes to:
  - review-matrix-updates   (ReviewMatrixUpdate Avro events from reviewService)
  - book-metadata-changes   (BookMetadataChangedEvent Avro events from bookService)

Routes messages to MatrixUpdateService which holds ml_loader.lock internally.
CPU-bound mutations are offloaded to a thread-pool executor via run_in_executor
to avoid blocking the asyncio event loop.
"""

import asyncio
from typing import Optional

from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer

import config
from services.matrix_update_service import MatrixUpdateService
from utils.logger import logger


class MatrixUpdateConsumer:

    def __init__(self, matrix_update_service: MatrixUpdateService):
        self.matrix_update_service = matrix_update_service
        self.consumer: Optional[DeserializingConsumer] = None
        self._running = False

    async def start(self) -> None:
        schema_registry_client = SchemaRegistryClient({'url': config.KAFKA_SCHEMA_REGISTRY_URL})
        avro_deserializer = AvroDeserializer(schema_registry_client=schema_registry_client)
        string_deserializer = StringDeserializer('utf_8')

        self.consumer = DeserializingConsumer({
            'bootstrap.servers': ','.join(config.KAFKA_BOOTSTRAP_SERVERS),
            'group.id': config.KAFKA_MATRIX_UPDATE_CONSUMER_GROUP,
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True,
            'key.deserializer': string_deserializer,
            'value.deserializer': avro_deserializer,
        })

        self.consumer.subscribe([
            config.KAFKA_REVIEW_MATRIX_UPDATE_TOPIC,
            config.KAFKA_BOOK_METADATA_CHANGED_TOPIC,
        ])

        logger.info(f"MatrixUpdateConsumer started. Subscribed to: "
                    f"[{config.KAFKA_REVIEW_MATRIX_UPDATE_TOPIC}, "
                    f"{config.KAFKA_BOOK_METADATA_CHANGED_TOPIC}]")

        self._running = True
        await self._process_messages()

    async def _process_messages(self) -> None:
        try:
            while self._running:
                try:
                    msg = await asyncio.get_event_loop().run_in_executor(
                        None, self.consumer.poll, 1
                    )
                    if msg is None:
                        await asyncio.sleep(0.1)
                        continue
                    if msg.error():
                        if msg.error().code() != -191:  # -191 = partition EOF
                            logger.error(f"MatrixUpdateConsumer Kafka error: {msg.error()}")
                        continue

                    topic = msg.topic()
                    value = msg.value()

                    if topic == config.KAFKA_REVIEW_MATRIX_UPDATE_TOPIC:
                        await self._handle_review_update(value)
                    elif topic == config.KAFKA_BOOK_METADATA_CHANGED_TOPIC:
                        await self._handle_book_metadata(value)
                    else:
                        logger.warning(f"MatrixUpdateConsumer: unexpected topic {topic}")

                except Exception as e:
                    logger.error(f"MatrixUpdateConsumer error processing message: {e}",
                                 exc_info=True)
                    await asyncio.sleep(1)
        finally:
            if self.consumer:
                self.consumer.close()

    async def _handle_review_update(self, value: dict) -> None:
        try:
            event_type = value.get('eventType')
            book_id = int(value.get('bookId', 0))
            rating = int(value.get('rating', 0))
            old_rating = value.get('oldRating')
            other_reviews = value.get('userOtherReviews', [])

            logger.info(
                f"MatrixUpdateConsumer: received review event "
                f"type={event_type} bookId={book_id} rating={rating} "
                f"pairs={len(other_reviews)}"
                + (f" oldRating={old_rating}" if old_rating is not None else "")
            )

            loop = asyncio.get_event_loop()
            if event_type == 'CREATE':
                await loop.run_in_executor(
                    None, self.matrix_update_service.apply_review_create,
                    book_id, rating, other_reviews
                )
                logger.info(f"MatrixUpdateConsumer: applied CREATE for bookId={book_id}")
            elif event_type == 'DELETE':
                await loop.run_in_executor(
                    None, self.matrix_update_service.apply_review_delete,
                    book_id, rating, other_reviews
                )
                logger.info(f"MatrixUpdateConsumer: applied DELETE for bookId={book_id}")
            elif event_type == 'UPDATE':
                if old_rating is None:
                    logger.warning(f"MatrixUpdateConsumer: UPDATE event for bookId={book_id} missing oldRating, skipping")
                    return
                await loop.run_in_executor(
                    None, self.matrix_update_service.apply_review_update,
                    book_id, rating, int(old_rating), other_reviews
                )
                logger.info(
                    f"MatrixUpdateConsumer: applied UPDATE for bookId={book_id} "
                    f"oldRating={old_rating} newRating={rating}"
                )
            else:
                logger.warning(f"MatrixUpdateConsumer: unknown eventType={event_type}")
        except Exception as e:
            logger.error(f"MatrixUpdateConsumer: error handling review event: {e}", exc_info=True)

    async def _handle_book_metadata(self, value: dict) -> None:
        try:
            event_type = value.get('eventType')
            book_id = int(value.get('bookId', 0))
            title = value.get('title') or ''
            author_name = value.get('authorName') or ''
            genres = list(value.get('genres') or [])
            category = value.get('category') or ''
            description = value.get('description') or ''

            logger.info(
                f"MatrixUpdateConsumer: received book metadata event "
                f"type={event_type} bookId={book_id} title='{title}'"
            )

            loop = asyncio.get_event_loop()
            if event_type == 'CREATED':
                await loop.run_in_executor(
                    None, self.matrix_update_service.apply_book_created,
                    book_id, title, author_name, genres, category, description
                )
                logger.info(f"MatrixUpdateConsumer: applied CREATED for bookId={book_id}")
            elif event_type == 'UPDATED':
                await loop.run_in_executor(
                    None, self.matrix_update_service.apply_book_updated,
                    book_id, title, author_name, genres, category, description
                )
                logger.info(f"MatrixUpdateConsumer: applied UPDATED for bookId={book_id}")
            else:
                logger.warning(f"MatrixUpdateConsumer: unknown eventType={event_type}")
        except Exception as e:
            logger.error(f"MatrixUpdateConsumer: error handling book metadata event: {e}", exc_info=True)

    async def stop(self) -> None:
        self._running = False
        if self.consumer:
            self.consumer.close()
        logger.info("MatrixUpdateConsumer stopped")


_matrix_update_consumer: Optional[MatrixUpdateConsumer] = None


async def start_matrix_update_consumer(matrix_update_service: MatrixUpdateService) -> None:
    global _matrix_update_consumer
    try:
        _matrix_update_consumer = MatrixUpdateConsumer(matrix_update_service)
        await _matrix_update_consumer.start()
    except Exception as e:
        logger.error(f"Failed to start matrix update consumer: {e}", exc_info=True)
        raise


async def stop_matrix_update_consumer() -> None:
    global _matrix_update_consumer
    if _matrix_update_consumer:
        await _matrix_update_consumer.stop()
