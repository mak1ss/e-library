package org.library.reviewService.mapper;

import lombok.AllArgsConstructor;
import org.library.reviewService.dto.review.ReviewRequest;
import org.library.reviewService.dto.review.ReviewResponse;
import org.library.reviewService.model.Review;
import org.library.reviewService.repository.ReviewRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@AllArgsConstructor
public class ReviewMapper implements IMapper<Review, ReviewRequest, ReviewResponse> {

    private final ReviewRepository reviewRepository;

    @Override
    public Review requestToEntity(Optional<String> id, ReviewRequest request) {
        Review entity = new Review();

        entity.setId(id.orElse(null));
        entity.setUserId(request.getUserId());
        entity.setBookId(request.getBookId());

        if(id.isPresent()) {
            entity.setCreatedAt(reviewRepository.findById(id.get()).orElseThrow(() -> new IllegalArgumentException("Unknown review id")).getCreatedAt());
        } else {
            entity.setCreatedAt(LocalDateTime.now());
        }

        entity.setRating(request.getRating());
        entity.setText(request.getText());

        return entity;
    }

    @Override
    public ReviewResponse entityToResponse(Review entity) {
        return ReviewResponse.builder()
                .userId(entity.getUserId())
                .bookId(entity.getBookId())
                .rating(entity.getRating())
                .text(entity.getText())
                .build();
    }

    @Override
    public List<ReviewResponse> entityToResponseList(List<Review> entityList) {
        return entityList.stream().map(this::entityToResponse).toList();
    }
}
