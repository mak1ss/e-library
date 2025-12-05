package org.library.reviewService.service;

import lombok.AllArgsConstructor;
import org.library.reviewService.client.BookServiceClient;
import org.library.reviewService.exception.AccessDeniedException;
import org.library.reviewService.model.Review;
import org.library.reviewService.repository.BaseRepository;
import org.library.reviewService.repository.ReviewRepository;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;

import java.util.NoSuchElementException;
import java.util.Optional;

@Service
@AllArgsConstructor
public class ReviewService extends AbstractService<Review> {

    private final ReviewRepository reviewRepository;
    private final ReviewMetricsService metricsService;
    private final MongoOperations mongoOperations;
    private final BookServiceClient bookClient;

    @Override
    protected BaseRepository<Review> getRepository() {
        return reviewRepository;
    }

    @Override
    protected MongoOperations getMongoOperations() {
        return mongoOperations;
    }

    @Override
    protected Class<Review> getEntityClass() {
        return Review.class;
    }

    @Override
    protected void beforeCreate(Review entity) {
        try {
            bookClient.getById(entity.getBookId());
        } catch (NoSuchElementException e) {
            throw new IllegalArgumentException("No book was found with id " + entity.getBookId());
        }

        Query query = new Query(Criteria.where("userId").is(entity.getUserId())
            .and("bookId").is(entity.getBookId()));

        Optional<Review> optionalReview = getOne(query, false);

        if (optionalReview.isPresent()) {
            throw new DuplicateKeyException("User has already reviewed this book. Use update instead.");
        }
    }

    @Override
    protected void beforeUpdate(Review entity) {
        checkAuthority(entity);
    }

    @Override
    protected void beforeDelete(Review entity) {
        checkAuthority(entity);
    }

    private void checkAuthority(Review entity) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        var authorities = authentication.getAuthorities();
        var jwt = (Jwt) authentication.getPrincipal();
        String subject = jwt.getSubject();

        boolean isAdmin = authorities.stream().anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
        boolean isUserOwnerOfReview = entity.getUserId().equals(subject);

        if (isAdmin || isUserOwnerOfReview) {
            return;
        }

        throw new AccessDeniedException("User has no rights to access this resource");
    }

    @Override
    public Review update(Review entity) {
        Review oldReview = reviewRepository.findById(entity.getId())
            .orElseThrow(() -> new NoSuchElementException("Review not found"));

        Integer oldRating = oldReview.getRating();
        Integer newRating = entity.getRating();

        Review saved = super.update(entity);

        metricsService.updateMetricsAfterEdit(saved.getBookId(), oldRating, newRating);

        return saved;
    }

    @Override
    protected void afterCreate(Review entity) {
        metricsService.addReviewMetrics(entity.getBookId(), entity.getRating());
    }

    @Override
    protected void afterDelete(Review entity) {
        metricsService.removeReviewMetrics(entity.getBookId(), entity.getRating());
    }
}
