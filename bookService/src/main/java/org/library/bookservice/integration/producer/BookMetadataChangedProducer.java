package org.library.bookservice.integration.producer;

import event.BookMetadataChangedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.bookservice.model.Book;
import org.library.bookservice.model.Genre;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Component
@RequiredArgsConstructor
public class BookMetadataChangedProducer {

    private final KafkaTemplate<String, BookMetadataChangedEvent> kafkaTemplate;

    @Value("${kafka.topics.book-metadata-changed:book-metadata-changes}")
    private String topic;

    public void publishCreated(Book book) {
        publish("CREATED", book);
    }

    public void publishUpdated(Book book) {
        publish("UPDATED", book);
    }

    private void publish(String eventType, Book book) {
        try {
            String authorName = book.getAuthor() != null ? book.getAuthor().getName() : null;
            List<CharSequence> genres = book.getGenres() != null
                    ? book.getGenres().stream().map(Genre::getName).collect(Collectors.toList())
                    : Collections.emptyList();
            String category = book.getCategory() != null ? book.getCategory().getName() : null;

            BookMetadataChangedEvent event = BookMetadataChangedEvent.newBuilder()
                    .setEventType(eventType)
                    .setBookId(book.getId())
                    .setTitle(book.getTitle())
                    .setAuthorName(authorName)
                    .setGenres(genres)
                    .setCategory(category)
                    .setDescription(book.getDescription())
                    .setTimestamp(System.currentTimeMillis())
                    .build();

            kafkaTemplate.send(topic, String.valueOf(book.getId()), event);
            log.info("Published BookMetadataChangedEvent type={} bookId={}", eventType, book.getId());
        } catch (Exception e) {
            log.error("Failed to publish BookMetadataChangedEvent bookId={}: {}", book.getId(), e.getMessage());
        }
    }
}
