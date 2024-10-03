package org.library.reviewService.controller;

import lombok.AllArgsConstructor;
import org.library.reviewService.dto.review.ReviewRequest;
import org.library.reviewService.dto.review.ReviewResponse;
import org.library.reviewService.filter.model.DocumentFilterSpecificationBuilder;
import org.library.reviewService.filter.model.review.ReviewSpecificationBuilder;
import org.library.reviewService.mapper.IMapper;
import org.library.reviewService.mapper.ReviewMapper;
import org.library.reviewService.model.Review;
import org.library.reviewService.service.AbstractService;
import org.library.reviewService.service.ReviewService;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/review")
@AllArgsConstructor
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
}
