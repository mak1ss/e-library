package org.library.reviewService.integration.producer;


import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.reviewService.event.ReviewScoringRequest;
import org.library.reviewService.model.Review;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;
import java.util.UUID;

/**
 * Kafka producer for publishing review scoring requests to the recommender service.
 * Publishes ReviewScoringRequest events when a new review is created, triggering
 * asynchronous semantic relevance scoring via the sentence transformer model.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class ReviewScoringRequestProducer {

    private final KafkaTemplate<String, ReviewScoringRequest> kafkaTemplate;

    @Value("${kafka.topics.review-scoring-request:review-scoring-request}")
    private String reviewScoringRequestTopic;

    /**
     * Publishes a review scoring request event when a new review is created.
     * The recommender service will consume this event, compute semantic relevance,
     * and publish a ReviewScoringResult back to the review-scoring-result topic.
     *
     * @param review The newly created review entity
     * @param bookMetadata Aggregated metadata about the book (title, description, genres)
     */
    public void publishReviewScoringRequest(Review review, String bookMetadata) {
        try {
            ReviewScoringRequest request = ReviewScoringRequest.newBuilder()
                    .setReviewId(review.getId())
                    .setBookId(review.getBookId())
                    .setReviewText(review.getText())
                    .setBookMetadata(bookMetadata)
                    .setUserId(review.getUserId())
                    .setTimestamp(System.currentTimeMillis())
                    .setCorrelationId(UUID.randomUUID().toString())
                    .build();

            kafkaTemplate.send(reviewScoringRequestTopic, review.getId(), request);
            
            log.info("Published review scoring request for review={} book={} correlationId={}",
                    review.getId(), review.getBookId(), request.getCorrelationId());
        } catch (Exception e) {
            log.error("Failed to publish review scoring request for review={}: {}",
                    review.getId(), e.getMessage(), e);
            // Do not throw - allow review creation to proceed even if event publishing fails
            // The review will remain unscored, and error handling/retry logic will manage recovery
        }
    }
}
