package org.library.reviewService.datagen;

import jakarta.annotation.PostConstruct;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.reviewService.model.Review;
import org.library.reviewService.repository.ReviewRepository;
import org.library.reviewService.service.ReviewMetricsService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

@Service
@AllArgsConstructor
@Slf4j
public class InitialDataGenerator {

    private final ReviewRepository reviewRepository;
    private final ReviewMetricsService reviewMetricsService;

    @PostConstruct
    public void initialize() {
        if (!reviewRepository.findAll().isEmpty()) {
            log.info("Skipped data generation. Database already contains data.");
            return;
        }
        List<Review> reviews = Arrays.asList(
                createReview(1, 1, 5, "Amazing book! Must read.", reviewMetricsService),
                createReview(2, 1, 4, "Very good, but a little slow in places.", reviewMetricsService),

                createReview(3, 2, 3, "An average read.", reviewMetricsService),
                createReview(4, 2, 4, "Interesting, but not extraordinary.", reviewMetricsService),

                createReview(5, 3, 2, "Not what I expected.", reviewMetricsService),
                createReview(6, 3, 1, "Quite disappointing.", reviewMetricsService),

                createReview(7, 4, 4, "Enjoyed the storyline.", reviewMetricsService),
                createReview(8, 4, 5, "Fantastic! Couldn't put it down.", reviewMetricsService),

                createReview(9, 5, 3, "It was okay, nothing special.", reviewMetricsService),
                createReview(10, 5, 2, "Not a fan of the writing style.", reviewMetricsService)
        );

        reviewRepository.saveAll(reviews);
        log.info("Saved {} reviews.", reviewRepository.count());
    }

    private Review createReview(Integer userId, Integer bookId, Integer rating, String text, ReviewMetricsService reviewMetricsService) {
        Review review = new Review();
        review.setUserId(userId);
        review.setBookId(bookId);
        review.setCreatedAt(LocalDateTime.now());
        review.setRating(rating);
        review.setText(text);
        review.setArchived(false);

        reviewMetricsService.updateMetrics(bookId, rating);

        return review;
    }
}
