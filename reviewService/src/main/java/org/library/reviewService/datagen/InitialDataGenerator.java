package org.library.reviewService.datagen;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.reviewService.model.Review;
import org.library.reviewService.repository.ReviewRepository;
import org.library.reviewService.service.ReviewMetricsService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class InitialDataGenerator {

    private final ReviewRepository reviewRepository;
    private final ReviewMetricsService reviewMetricsService;
    private final ObjectMapper objectMapper;

    @Value("${data.seeding.folder}")
    private String seedingFolder;

    @Value("${data.seeding.reviews}")
    private String reviewsFile;

    @EventListener(ApplicationReadyEvent.class)
    @Async
    public void onApplicationReady() {
        try {
            // Add a small delay to ensure Schema Registry and other services are ready
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            log.warn("Data seeding sleep was interrupted", e);
        }

        if (reviewRepository.count() > 0) {
            log.info("Database already initialized. Skipping data seeding.");
            return;
        }

        try {
            log.info("Starting data seeding from folder: {}", seedingFolder);

            List<ReviewSeedDto> reviewDtos = loadData(reviewsFile, new TypeReference<>() {
            });
            List<Review> reviews = new ArrayList<>();

            for (ReviewSeedDto dto : reviewDtos) {
                Review review = new Review();
                review.setUserId(dto.getUserId());
                review.setFirstName(dto.getFirstName());
                review.setLastName(dto.getLastName());
                review.setAvatarUrl(dto.getAvatarUrl());
                review.setBookId(dto.getBookId());
                review.setRating(dto.getRating());
                review.setText(dto.getText());
                review.setArchived(false);

                if (dto.getCreatedAt() != null) {
                    review.setCreatedAt(LocalDateTime.parse(dto.getCreatedAt()));
                } else {
                    review.setCreatedAt(LocalDateTime.now());
                }

                reviews.add(review);
            }

            reviews.forEach(r -> {
                reviewRepository.save(r);
                reviewMetricsService.addReviewMetrics(r.getBookId(), r.getRating());
            });
            log.info("Successfully loaded {} reviews into database", reviews.size());

        } catch (IOException e) {
            log.error("Failed to seed data: {}", e.getMessage(), e);
            throw new RuntimeException("Data seeding failed", e);
        }
    }

    /**
     * Helper method to read JSON files.
     */
    private <T> List<T> loadData(String fileName, TypeReference<List<T>> typeReference) throws IOException {
        String fullPath = Paths.get(seedingFolder, fileName).toString();

        log.debug("Reading data from file: {}", fullPath);

        try (InputStream inputStream = new FileInputStream(fullPath)) {
            return objectMapper.readValue(inputStream, typeReference);
        }
    }
}