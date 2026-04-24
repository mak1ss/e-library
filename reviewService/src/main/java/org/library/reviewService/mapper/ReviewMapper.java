package org.library.reviewService.mapper;

import lombok.AllArgsConstructor;
import org.library.reviewService.dto.review.ReviewRequest;
import org.library.reviewService.dto.review.ReviewResponse;
import org.library.reviewService.exception.AccessDeniedException;
import org.library.reviewService.model.Review;
import org.library.reviewService.repository.ReviewRepository;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@AllArgsConstructor
public class ReviewMapper implements IMapper<Review, ReviewRequest, ReviewResponse> {

    private static final String SUB = "sub";
    private static final String GIVEN_NAME = "given_name";
    private static final String FAMILY_NAME = "family_name";
    private static final String PICTURE = "picture";
    private final ReviewRepository reviewRepository;

    @Override
    public Review requestToEntity(Optional<String> id, ReviewRequest request) {
        Review entity = new Review();

        entity.setId(id.orElse(null));
        entity.setBookId(request.getBookId());

        if(id.isPresent()) {
            Review existing = reviewRepository.findById(id.get())
                .orElseThrow(() -> new IllegalArgumentException("Unknown review id"));
            entity.setCreatedAt(existing.getCreatedAt());

            entity.setUserId(existing.getUserId());
            entity.setFirstName(existing.getFirstName());
            entity.setLastName(existing.getLastName());
            entity.setAvatarUrl(existing.getAvatarUrl());
        } else {
            entity.setCreatedAt(LocalDateTime.now());
            populateUserData(entity);
        }

        entity.setRating(request.getRating());
        entity.setText(request.getText());

        return entity;
    }

    @Override
    public ReviewResponse entityToResponse(Review entity) {
        return ReviewResponse.builder()
                .id(entity.getId())
                .userId(entity.getUserId())
                .firstName(entity.getFirstName())
                .lastName(entity.getLastName())
                .avatarUrl(entity.getAvatarUrl())
                .bookId(entity.getBookId())
                .createdAt(entity.getCreatedAt())
                .rating(entity.getRating())
                .text(entity.getText())
                .relevanceScore(
                    entity.getScoringResult() != null && entity.getScoringResult().isSuccessful()
                        ? entity.getScoringResult().getScore()
                        : null
                )
                .build();
    }

    @Override
    public List<ReviewResponse> entityToResponseList(List<Review> entityList) {
        return entityList.stream().map(this::entityToResponse).toList();
    }

    private void populateUserData(Review entity) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication != null && authentication.getPrincipal() instanceof Jwt jwt) {
            entity.setUserId(jwt.getClaimAsString(SUB));
            entity.setFirstName(jwt.getClaimAsString(GIVEN_NAME));
            entity.setLastName(jwt.getClaimAsString(FAMILY_NAME));

            if (jwt.hasClaim(PICTURE)) {
                entity.setAvatarUrl(jwt.getClaimAsString(PICTURE));
            }
        } else {
            throw new AccessDeniedException("User must be authenticated to create reviews");
        }
    }
}
