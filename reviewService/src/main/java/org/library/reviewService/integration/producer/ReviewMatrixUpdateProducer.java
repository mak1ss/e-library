package org.library.reviewService.integration.producer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.reviewService.event.ReviewEventType;
import org.library.reviewService.event.ReviewMatrixUpdate;
import org.library.reviewService.event.UserReviewEntry;
import org.library.reviewService.model.Review;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Component
@RequiredArgsConstructor
public class ReviewMatrixUpdateProducer {

    private final KafkaTemplate<String, ReviewMatrixUpdate> kafkaTemplate;

    @Value("${kafka.topics.review-matrix-update:review-matrix-updates}")
    private String topic;

    public void publishCreate(Review review, List<Review> otherUserReviews) {
        publish(ReviewEventType.CREATE, review.getUserId(), review.getBookId(),
                review.getRating(), null, otherUserReviews);
    }

    public void publishUpdate(Review review, Integer oldRating, List<Review> otherUserReviews) {
        publish(ReviewEventType.UPDATE, review.getUserId(), review.getBookId(),
                review.getRating(), oldRating, otherUserReviews);
    }

    public void publishDelete(Review review, List<Review> otherUserReviews) {
        publish(ReviewEventType.DELETE, review.getUserId(), review.getBookId(),
                review.getRating(), null, otherUserReviews);
    }

    private void publish(ReviewEventType eventType, String userId, Integer bookId,
                         Integer rating, Integer oldRating, List<Review> otherReviews) {
        try {
            List<UserReviewEntry> entries = otherReviews.stream()
                    .map(r -> UserReviewEntry.newBuilder()
                            .setBookId(r.getBookId())
                            .setRating(r.getRating())
                            .build())
                    .collect(Collectors.toList());

            ReviewMatrixUpdate event = ReviewMatrixUpdate.newBuilder()
                    .setEventType(eventType)
                    .setUserId(userId)
                    .setBookId(bookId)
                    .setRating(rating)
                    .setOldRating(oldRating)
                    .setUserOtherReviews(entries)
                    .setTimestamp(System.currentTimeMillis())
                    .build();

            kafkaTemplate.send(topic, userId, event);
            log.info("Published ReviewMatrixUpdate type={} userId={} bookId={} pairs={}",
                    eventType, userId, bookId, entries.size());
        } catch (Exception e) {
            log.error("Failed to publish ReviewMatrixUpdate userId={} bookId={}: {}",
                    userId, bookId, e.getMessage());
        }
    }
}
