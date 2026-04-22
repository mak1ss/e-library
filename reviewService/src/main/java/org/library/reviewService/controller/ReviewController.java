package org.library.reviewService.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import lombok.AllArgsConstructor;
import org.library.reviewService.dto.PageResponse;
import org.library.reviewService.dto.review.ReviewRequest;
import org.library.reviewService.dto.review.ReviewResponse;
import org.library.reviewService.filter.model.DocumentFilterSpecificationBuilder;
import org.library.reviewService.filter.model.review.ReviewSpecificationBuilder;
import org.library.reviewService.mapper.IMapper;
import org.library.reviewService.mapper.ReviewMapper;
import org.library.reviewService.model.Review;
import org.library.reviewService.service.AbstractService;
import org.library.reviewService.service.ReviewService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/reviews")
@AllArgsConstructor
@SecurityRequirement(name = "standardFlow")
@SecurityRequirement(name = "clientCredentialsFlow")
public class ReviewController extends AbstractController<Review, ReviewRequest, ReviewResponse> {

    private final ReviewService reviewService;
    private final ReviewMapper reviewMapper;
    private final ReviewSpecificationBuilder specificationBuilder;

    @Override
    protected AbstractService<Review> getService() {
        return reviewService;
    }

    @Override
    protected IMapper<Review, ReviewRequest, ReviewResponse> getMapper() {
        return reviewMapper;
    }

    @Override
    protected DocumentFilterSpecificationBuilder getSpecificationBuilder() {
        return specificationBuilder;
    }

    /**
     * Get all reviews for a specific user
     * Returns reviews without pagination limits (for recommendations)
     */
    @GetMapping("/user")
    @Operation(summary = "Get user's reviews", description = "Get all reviews created by a specific user")
    public ResponseEntity<PageResponse<ReviewResponse>> getUserReviews(
            @RequestParam String userId) {
        
        try {
            // Get all reviews for the user
            List<Review> reviews = reviewService.getUserReviews(userId);

            // Convert to DTOs
            List<ReviewResponse> reviewResponses = reviews.stream()
                    .map(getMapper()::entityToResponse)
                    .collect(Collectors.toList());

            // Return as PageResponse for consistency
            PageResponse<ReviewResponse> response = PageResponse.<ReviewResponse>builder()
                    .size(reviewResponses.size())
                    .total((long) reviewResponses.size())
                    .pageNumber(0)
                    .items(reviewResponses)
                    .build();

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
}
