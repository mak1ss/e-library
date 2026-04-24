"""
Kafka consumer service for processing review scoring requests.

Listens to review-scoring-requests topic, scores reviews using semantic similarity,
and publishes results to review-scoring-results topic via Kafka producer.
"""

import asyncio
import json
import logging
import os
from typing import Optional
from confluent_kafka import DeserializingConsumer, SerializingProducer, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer
import config
from core_scoring_strategies import (
    BookMetadataAggregator,
    ReviewTextPreprocessor,
    BookEdgeCaseHandler,
    ReviewEdgeCaseHandler,
    RelevanceScoringFunction,
)
from utils.logger import logger


class ReviewScoringConsumer:
    """
    Kafka consumer for asynchronous review scoring requests.
    
    Uses modern DeserializingConsumer with:
    - StringDeserializer for keys (no Avro magic byte expected)
    - AvroDeserializer for values (expects Avro magic byte)
    
    Workflow:
    1. Listen for ReviewScoringRequest events on review-scoring-requests topic
    2. Preprocess review text and book metadata
    3. Generate semantic embeddings for both
    4. Compute cosine similarity and normalize to [0, 1]
    5. Publish ReviewScoringResult to review-scoring-results topic
    6. On error: publish to dead-letter queue topic
    """

    def __init__(self, sentence_transformer_model=None):
        """
        Initialize the consumer with scoring strategy components.
        
        Args:
            sentence_transformer_model: Optional pre-loaded model instance
                                       (for testing/initialization)
        """
        self.logger = logger
        self.consumer = None
        self.producer = None
        self.schema_registry_client = None
        
        # Initialize scoring strategy components
        self.book_aggregator = BookMetadataAggregator()
        self.review_preprocessor = ReviewTextPreprocessor()
        self.book_edge_case_handler = BookEdgeCaseHandler()
        self.review_edge_case_handler = ReviewEdgeCaseHandler()
        self.scoring_function = RelevanceScoringFunction(
            model_name=sentence_transformer_model or config.SENTENCE_TRANSFORMER_MODEL
        )
        
        self.logger.info(f"ReviewScoringConsumer initialized with model: {config.SENTENCE_TRANSFORMER_MODEL}")

    async def start(self):
        """Start the Kafka consumer and producer."""
        try:
            # Initialize schema registry client for schema retrieval by ID
            self.schema_registry_client = SchemaRegistryClient({
                'url': config.KAFKA_SCHEMA_REGISTRY_URL
            })
            
            # Create Avro deserializer for values (messages have Avro magic byte)
            avro_deserializer = AvroDeserializer(
                schema_registry_client=self.schema_registry_client
            )
            
            # Create StringDeserializer for keys (plain string, no magic byte)
            string_deserializer = StringDeserializer('utf_8')
            
            # Create modern DeserializingConsumer
            # Key: StringDeserializer (key is just review ID as string)
            # Value: AvroDeserializer (message body is Avro-encoded)
            self.consumer = DeserializingConsumer({
                'bootstrap.servers': ','.join(config.KAFKA_BOOTSTRAP_SERVERS),
                'group.id': config.KAFKA_CONSUMER_GROUP,
                'auto.offset.reset': 'latest',
                'enable.auto.commit': True,
                'max.poll.interval.ms': 300000,  # 5 minutes for processing
                'isolation.level': 'read_committed',
                'key.deserializer': string_deserializer,
                'value.deserializer': avro_deserializer,
            })
            
            # Create modern SerializingProducer for results
            string_serializer = StringSerializer('utf_8')
            
            # Load ReviewScoringResult schema for value serialization
            schema_path = os.path.join(os.path.dirname(__file__), '..', 'kafka_schemas', 'review_scoring_result_v1.avsc')
            with open(schema_path, 'r') as f:
                result_schema_dict = json.load(f)
            
            # Create Avro serializer with the ReviewScoringResult schema
            avro_serializer = AvroSerializer(
                schema_registry_client=self.schema_registry_client,
                schema_str=json.dumps(result_schema_dict)
            )
            
            self.producer = SerializingProducer({
                'bootstrap.servers': ','.join(config.KAFKA_BOOTSTRAP_SERVERS),
                'key.serializer': string_serializer,
                'value.serializer': avro_serializer,
            })
            
            # Subscribe to request topic
            self.consumer.subscribe([config.KAFKA_REVIEW_SCORING_REQUEST_TOPIC])
            
            self.logger.info(f"ReviewScoringConsumer started. Listening to topic: {config.KAFKA_REVIEW_SCORING_REQUEST_TOPIC}")
            
            # Start message processing loop
            await self._process_messages()
            
        except Exception as e:
            self.logger.error(f"Failed to start ReviewScoringConsumer: {e}", exc_info=True)
            raise
        """
        Subscribe to topic with retry logic.
        Handles the case where topic doesn't exist yet (will be created when first message is published).
        
        Args:
            topic: Topic name to subscribe to
            max_retries: Maximum number of retry attempts (30 * 1s = 30 seconds timeout)
            retry_delay: Delay between retries in seconds
        """
        for attempt in range(max_retries):
            try:
                self.consumer.subscribe([topic])
                self.logger.info(f"Successfully subscribed to topic: {topic}")
                return
            except Exception as e:
                error_str = str(e)
                # Check if it's the expected "topic doesn't exist yet" error
                if "UNKNOWN_TOPIC_OR_PART" in error_str or "not available" in error_str:
                    self.logger.warning(
                        f"Topic '{topic}' not yet available (attempt {attempt + 1}/{max_retries}). "
                        f"It will be created when the first message is published. Retrying in {retry_delay}s..."
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    # Different error - fail fast
                    self.logger.error(f"Failed to subscribe to topic '{topic}': {e}")
                    raise
        
        raise Exception(f"Failed to subscribe to topic '{topic}' after {max_retries} retries")

    async def _process_messages(self):
        """Main message processing loop."""
        try:
            while True:
                try:
                    # Run blocking poll in thread pool to avoid blocking event loop
                    # timeout=1 second to keep loop responsive
                    msg = await asyncio.get_event_loop().run_in_executor(
                        None, self.consumer.poll, 1
                    )
                    
                    if msg is None:
                        await asyncio.sleep(0.1)
                        continue
                    
                    if msg.error():
                        if msg.error().code() != -191:  # -191 = partition EOF (expected)
                            self.logger.error(f"Kafka consumer error: {msg.error()}")
                        continue
                    
                    await self._handle_scoring_request(msg.value())
                    
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}", exc_info=True)
                    # Wait before retrying to avoid tight loop on persistent errors
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            self.logger.info("ReviewScoringConsumer shutting down...")
        finally:
            # Run blocking close operations in thread pool
            try:
                await asyncio.get_event_loop().run_in_executor(None, self._cleanup)
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}", exc_info=True)

    def _cleanup(self):
        """Synchronous cleanup method to be run in thread pool."""
        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.flush()

    async def _handle_scoring_request(self, request):
        """
        Process a single ReviewScoringRequest.
        
        Args:
            request: Deserialized ReviewScoringRequest Avro message
        """
        review_id = request.get('reviewId')
        book_id = request.get('bookId')
        correlation_id = request.get('correlationId')
        
        try:
            self.logger.info(f"Processing scoring request for review={review_id} "
                           f"book={book_id} correlation={correlation_id}")
            
            # Extract and preprocess review text
            review_text = request.get('reviewText', '')
            preprocessed_review = self.review_preprocessor.preprocess(review_text)
            
            # Check for review edge cases
            is_valid_review, msg_review, case_review = self.review_edge_case_handler.validate_and_log(
                review_id, review_text, preprocessed_review
            )
            if not is_valid_review:
                self.logger.warning(f"Review validation failed: {msg_review}")
                await self._publish_error_result(
                    review_id, case_review.value, msg_review, correlation_id
                )
                return
            
            # Extract and handle book metadata
            book_metadata_json = request.get('bookMetadata', '{}')
            try:
                book_metadata = json.loads(book_metadata_json)
            except json.JSONDecodeError:
                book_metadata = {}
            
            # Get aggregated book metadata string for edge case validation
            aggregated_metadata = self.book_aggregator.aggregate_from_dict(book_metadata)
            
            # Extract title from metadata for validation (provide reasonable default)
            book_title = book_metadata.get('title', 'Unknown Book')
            book_description = book_metadata.get('description')
            
            # Check for book metadata edge cases
            is_valid_book, msg_book, case_book = self.book_edge_case_handler.validate_and_log(
                book_id, book_title, book_description, aggregated_metadata
            )
            if not is_valid_book:
                self.logger.warning(f"Book metadata validation failed: {msg_book}")
                await self._publish_error_result(
                    review_id, case_book.value, msg_book, correlation_id
                )
                return
            
            # Compute relevance score (generates embeddings and scores)
            timestamp_start = __import__('time').time()
            
            score_result = self.scoring_function.compute_relevance_score(
                review_text=preprocessed_review,
                book_metadata=book_metadata
            )
            
            processing_time_ms = int((__import__('time').time() - timestamp_start) * 1000)
            
            # Check if scoring was successful
            if not score_result.is_valid():
                self.logger.error(f"Scoring failed for review {review_id}: {score_result.error_message}")
                await self._publish_error_result(
                    review_id, score_result.error_code, 
                    score_result.error_message, correlation_id
                )
                return
            
            # Publish successful result
            await self._publish_result(
                review_id, score_result, processing_time_ms, correlation_id
            )
            
        except Exception as e:
            self.logger.error(f"Error scoring review {review_id}: {e}", exc_info=True)
            await self._publish_error_result(
                review_id, "INTERNAL_ERROR", str(e), correlation_id
            )

    async def _publish_result(self, review_id: str, score_result, 
                             processing_time_ms: int, correlation_id: str):
        """
        Publish a successful scoring result.
        
        Args:
            review_id: Review identifier
            score_result: RelevanceScore dataclass with scoring results
            processing_time_ms: Time taken to score
            correlation_id: Correlation ID for tracing
        """
        try:
            # Explicitly ensure all string fields are Python str type (not bytes or other types)
            result = {
                'reviewId': str(review_id),
                'score': float(score_result.score) if score_result.score is not None else None,
                'modelVersion': str(f"{config.SENTENCE_TRANSFORMER_MODEL}@{config.SENTENCE_TRANSFORMER_MODEL_VERSION}"),
                'rawCosineSimilarity': float(score_result.raw_cosine) if score_result.raw_cosine is not None else None,
                'confidence': float(score_result.confidence) if score_result.confidence is not None else None,
                'errorCode': None,  # Explicitly None for optional field
                'errorMessage': None,  # Explicitly None for optional field
                'timestamp': int(__import__('time').time() * 1000),
                'processingTimeMs': int(processing_time_ms),
            }
            
            # Use SerializingProducer to publish Avro-encoded message
            self.producer.produce(
                topic=config.KAFKA_REVIEW_SCORING_RESULT_TOPIC,
                key=str(review_id),
                value=result
            )
            
            # Flush to ensure message is sent (with timeout)
            self.producer.flush(timeout=5)
            
            self.logger.info(f"Published scoring result for review={review_id} "
                           f"score={result['score']:.3f} correlation={correlation_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish result for review {review_id}: {e}", exc_info=True)
            # Publish to DLQ as fallback
            await self._publish_to_dlq(review_id, f"Failed to publish result: {e}", correlation_id)

    async def _publish_error_result(self, review_id: str, error_code: str, 
                                   error_message: str, correlation_id: str):
        """
        Publish an error result when scoring fails.
        
        Args:
            review_id: Review identifier
            error_code: Standardized error code
            error_message: Human-readable error description
            correlation_id: Correlation ID for tracing
        """
        try:
            # Explicitly ensure all string fields are Python str type (not bytes or other types)
            result = {
                'reviewId': str(review_id),
                'score': None,  # Explicitly None for optional field
                'modelVersion': str(f"{config.SENTENCE_TRANSFORMER_MODEL}@{config.SENTENCE_TRANSFORMER_MODEL_VERSION}"),
                'rawCosineSimilarity': None,  # Explicitly None for optional field
                'confidence': None,  # Explicitly None for optional field
                'errorCode': str(error_code) if error_code else None,
                'errorMessage': str(error_message) if error_message else None,
                'timestamp': int(__import__('time').time() * 1000),
                'processingTimeMs': 0,
            }
            
            # Use SerializingProducer to publish Avro-encoded message
            self.producer.produce(
                topic=config.KAFKA_REVIEW_SCORING_RESULT_TOPIC,
                key=str(review_id),
                value=result
            )
            
            # Flush to ensure message is sent
            self.producer.flush(timeout=5)
            
            self.logger.warning(f"Published error result for review={review_id} "
                              f"error={error_code} correlation={correlation_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish error result for review {review_id}: {e}", exc_info=True)
            await self._publish_to_dlq(review_id, f"Failed to publish error: {e}", correlation_id)

    async def _publish_to_dlq(self, review_id: str, message: str, correlation_id: str):
        """
        Publish to dead-letter queue when normal processing fails.
        Publishes as JSON strings since DLQ doesn't need Avro schema.
        
        Args:
            review_id: Review identifier
            message: Error message
            correlation_id: Correlation ID for tracing
        """
        try:
            dlq_message = {
                'reviewId': str(review_id),
                'errorMessage': str(message),
                'correlationId': str(correlation_id) if correlation_id else None,
                'timestamp': int(__import__('time').time() * 1000),
            }
            
            # Use low-level Producer for DLQ (just bytes, no schema)
            dlq_producer = Producer({
                'bootstrap.servers': ','.join(config.KAFKA_BOOTSTRAP_SERVERS)
            })
            
            dlq_producer.produce(
                topic=config.KAFKA_REVIEW_SCORING_DLQ_TOPIC,
                key=str(review_id).encode('utf-8'),
                value=json.dumps(dlq_message).encode('utf-8')
            )
            
            dlq_producer.flush()
            
            self.logger.error(f"Published to DLQ for review={review_id} correlation={correlation_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish to DLQ for review {review_id}: {e}", exc_info=True)

    async def stop(self):
        """Gracefully stop the consumer and producer."""
        try:
            if self.consumer:
                self.consumer.close()
            if self.producer:
                self.producer.flush()
            self.logger.info("ReviewScoringConsumer stopped")
        except Exception as e:
            self.logger.error(f"Error stopping consumer: {e}", exc_info=True)


# Global consumer instance
_review_scoring_consumer: Optional[ReviewScoringConsumer] = None


async def start_review_scoring_consumer():
    """Initialize and start the review scoring consumer."""
    global _review_scoring_consumer
    try:
        _review_scoring_consumer = ReviewScoringConsumer()
        await _review_scoring_consumer.start()
    except Exception as e:
        logger.error(f"Failed to start review scoring consumer: {e}", exc_info=True)
        raise


async def stop_review_scoring_consumer():
    """Gracefully stop the review scoring consumer."""
    global _review_scoring_consumer
    if _review_scoring_consumer:
        await _review_scoring_consumer.stop()
