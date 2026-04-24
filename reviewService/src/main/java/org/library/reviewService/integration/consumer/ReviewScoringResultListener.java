package org.library.reviewService.integration.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.reviewService.event.ReviewScoringResult;
import org.library.reviewService.model.Review;
import org.library.reviewService.repository.ReviewRepository;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Kafka consumer listener for review scoring results.
 * Listens to review-scoring-results topic and updates MongoDB with the computed scores.
 * Provides visibility into asynchronous scoring completion and handles errors gracefully.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class ReviewScoringResultListener {

    private final ReviewRepository reviewRepository;

    /**
     * Listens for ReviewScoringResult events from the recommender service.
     * Updates the MongoDB review document with the scoring result, including:
     * - Final relevance score [0.0, 1.0]
     * - Model version used
     * - Confidence score
     * - Processing time
     * - Error information (if scoring failed)
     *
     * @param result The ReviewScoringResult event from Kafka
     */
    @KafkaListener(
            topics = "${kafka.topics.review-scoring-result:review-scoring-results}",
            groupId = "${spring.kafka.consumer.group-id:review-service-group}",
            containerFactory = "kafkaListenerContainerFactory"
    )
    public void onScoringResult(ReviewScoringResult result) {
        try {
            if (result == null || result.getReviewId() == null) {
                log.warn("Received null or invalid ReviewScoringResult");
                return;
            }

            // Convert Avro Utf8 to String for review ID
            String reviewId = result.getReviewId().toString();

            log.info("Received scoring result for review={} score={} errorCode={}",
                    reviewId,
                    result.getScore(),
                    result.getErrorCode());

            // Find and update the review document
            reviewRepository.findById(reviewId).ifPresentOrElse(
                    review -> updateReviewWithScoringResult(review, result),
                    () -> log.error("Review not found for id={}", reviewId)
            );

        } catch (Exception e) {
            log.error("Error processing scoring result for review={}: {}",
                    result != null ? result.getReviewId() : "unknown",
                    e.getMessage(), e);
        }
    }

    /**
     * Updates a Review document with the scoring result.
     * Creates a ReviewScoringResult embedded document and saves to MongoDB.
     *
     * @param review The review entity to update
     * @param result The scoring result from Kafka
     */
    private void updateReviewWithScoringResult(Review review, ReviewScoringResult result) {
        try {
            // Convert Avro Utf8 strings to Java String using toString()
            // (Avro deserializer returns org.apache.avro.util.Utf8 for string fields)
            String modelVersion = result.getModelVersion() != null ? result.getModelVersion().toString() : null;
            String errorCode = result.getErrorCode() != null ? result.getErrorCode().toString() : null;
            String errorMessage = result.getErrorMessage() != null ? result.getErrorMessage().toString() : null;
            
            // Create ReviewScoringResult embedded document
            org.library.reviewService.model.ReviewScoringResult scoringResult =
                    org.library.reviewService.model.ReviewScoringResult.builder()
                            .score(result.getScore())
                            .modelVersion(modelVersion)
                            .rawCosineSimilarity(result.getRawCosineSimilarity())
                            .confidence(result.getConfidence())
                            .errorCode(errorCode)
                            .errorMessage(errorMessage)
                            .timestamp(result.getTimestamp())
                            .processingTimeMs(result.getProcessingTimeMs())
                            .build();

            // Update review with scoring result
            review.setScoringResult(scoringResult);

            // Save to MongoDB
            reviewRepository.save(review);

            // Log result
            if (scoringResult.isSuccessful()) {
                log.info("Successfully updated review={} with score={:.3f} confidence={:.3f} processingTimeMs={}",
                        review.getId(),
                        result.getScore(),
                        result.getConfidence(),
                        result.getProcessingTimeMs());
            } else {
                log.warn("Scoring failed for review={} errorCode={} errorMessage={}",
                        review.getId(),
                        result.getErrorCode(),
                        result.getErrorMessage());
            }

        } catch (Exception e) {
            log.error("Error updating review {} with scoring result: {}",
                    review.getId(), e.getMessage(), e);
        }
    }
}
