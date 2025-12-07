package org.library.reviewService.service;

import lombok.AllArgsConstructor;
import org.library.reviewService.dto.reviewMetrics.ReviewMetricsResponse;
import org.library.reviewService.integration.producer.BookRatingUpdatedProducer;
import org.library.reviewService.model.ReviewMetrics;
import org.library.reviewService.repository.BaseRepository;
import org.library.reviewService.repository.ReviewMetricsRepository;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.Optional;

@Service
@AllArgsConstructor
public class ReviewMetricsService extends AbstractService<ReviewMetrics> {

    private final ReviewMetricsRepository reviewMetricsRepository;
    private final MongoOperations mongoOperations;
    private final BookRatingUpdatedProducer producer;

    @Override
    protected BaseRepository<ReviewMetrics> getRepository() {
        return reviewMetricsRepository;
    }

    @Override
    protected MongoOperations getMongoOperations() {
        return mongoOperations;
    }

    @Override
    protected Class<ReviewMetrics> getEntityClass() {
        return ReviewMetrics.class;
    }

    public Optional<ReviewMetrics> getByBookId(Integer bookId) {
         return getOne(new Query(Criteria.where("bookId").is(bookId)));
    }

    public void addReviewMetrics(Integer bookId, Integer reviewRating) {
        ReviewMetrics metrics = getByBookId(bookId).orElse(new ReviewMetrics());
        if(metrics.getBookId() == null) {
            metrics.setBookId(bookId);
            metrics.setTotalReviews(1);
        } else {
            metrics.setTotalReviews(metrics.getTotalReviews() + 1);
        }
        metrics.getReviewCountsRating().putIfAbsent(reviewRating.toString(), 0);
        metrics.getReviewCountsRating().compute(reviewRating.toString(), (k, v) -> v + 1);
        metrics.setAverageRating(calculateAverageRating(metrics));

        update(metrics);
        producer.sendBookRatingUpdatedEvent(metrics);
    }

    public void updateMetricsAfterEdit(Integer bookId, Integer oldRating, Integer newRating) {
        if (oldRating.equals(newRating)) return;

        ReviewMetrics metrics = getByBookId(bookId).orElseThrow(
            () -> new IllegalStateException("Metrics not found for book " + bookId));

        Map<String, Integer> counts = metrics.getReviewCountsRating();

        String oldKey = oldRating.toString();
        if (counts.containsKey(oldKey)) {
            int currentCount = counts.get(oldKey);
            if (currentCount > 0) {
                counts.put(oldKey, currentCount - 1);
            }
        }

        String newKey = newRating.toString();
        counts.putIfAbsent(newKey, 0);
        counts.put(newKey, counts.get(newKey) + 1);

        metrics.setAverageRating(calculateAverageRating(metrics));

        update(metrics);
        producer.sendBookRatingUpdatedEvent(metrics);
    }

    public void removeReviewMetrics(Integer bookId, Integer rating) {
        getByBookId(bookId).ifPresent(metrics -> {
            if (metrics.getTotalReviews() > 0) {
                metrics.setTotalReviews(metrics.getTotalReviews() - 1);
            }

            String key = rating.toString();
            if (metrics.getReviewCountsRating().containsKey(key)) {
                int count = metrics.getReviewCountsRating().get(key);
                if (count > 0) {
                    metrics.getReviewCountsRating().put(key, count - 1);
                }
            }

            metrics.setAverageRating(calculateAverageRating(metrics));

            update(metrics);
            producer.sendBookRatingUpdatedEvent(metrics);
        });
    }

    private Double calculateAverageRating(ReviewMetrics metrics) {
        double ratingsSum = 0;
        for(Map.Entry<String, Integer> pair : metrics.getReviewCountsRating().entrySet()) {
            ratingsSum += pair.getValue() * Integer.parseInt(pair.getKey());
        }
        return ratingsSum / metrics.getTotalReviews();
    }

    public static ReviewMetricsResponse mapToResponse(ReviewMetrics reviewMetrics) {
        return ReviewMetricsResponse.builder()
                .id(reviewMetrics.getId())
                .bookId(reviewMetrics.getBookId())
                .totalReviews(reviewMetrics.getTotalReviews())
                .averageRating(reviewMetrics.getAverageRating())
                .reviewCountsRating(reviewMetrics.getReviewCountsRating())
                .build();
    }
}
