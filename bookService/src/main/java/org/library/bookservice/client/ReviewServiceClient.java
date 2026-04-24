package org.library.bookservice.client;

import org.library.bookservice.dto.PageResponse;
import org.library.bookservice.dto.review.ReviewResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * OpenFeign client for reviewService
 */
@FeignClient(
    name = "review-service",
    url = "${review-service.url}"
)
public interface ReviewServiceClient {
    
    /**
     * Get all reviews for a specific user (for recommendations)
     * Returns all reviews without pagination limits
     */
    @GetMapping("/api/reviews/user")
    ResponseEntity<PageResponse<ReviewResponse>> getUserReviewedBooks(
            @RequestParam String userId
    );
    
    /**
     * Search reviews by userId to get user's review history (for recommendations)
     */
    @GetMapping("/api/reviews")
    ResponseEntity<PageResponse<ReviewResponse>> searchReviews(
            @RequestParam(defaultValue = "0") Integer page,
            @RequestParam(defaultValue = "50") Integer size,
            @RequestParam(defaultValue = "createdAt,desc") String sort,
            @RequestParam String search
    );
}
