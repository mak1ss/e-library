package org.library.reviewService.integration.producer;


import event.BookRatingUpdatedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.reviewService.model.ReviewMetrics;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Slf4j
@RequiredArgsConstructor
@Service
public class BookRatingUpdatedProducer {

    @Value("${kafka.topics.book-rating-updated:book-rating-updated}")
    private String bookRatingUpdatedTopic;

    private final KafkaTemplate<String, BookRatingUpdatedEvent> kafkaTemplate;

    public void sendBookRatingUpdatedEvent(ReviewMetrics metrics) {
        log.info("Sending book rating update event {}: {}", metrics.getBookId(), metrics.getAverageRating());

        kafkaTemplate.send(bookRatingUpdatedTopic, new BookRatingUpdatedEvent(metrics.getBookId(),
            metrics.getAverageRating(), metrics.getTotalReviews()));;
    }
}
