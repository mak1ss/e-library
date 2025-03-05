package org.library.reviewService.service;

import lombok.AllArgsConstructor;
import org.library.reviewService.client.BookServiceClient;
import org.library.reviewService.exception.AccessDeniedException;
import org.library.reviewService.model.Review;
import org.library.reviewService.repository.BaseRepository;
import org.library.reviewService.repository.ReviewRepository;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.stereotype.Service;

import java.util.NoSuchElementException;

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

        if(isAdmin || isUserOwnerOfReview) {
            return;
        }

        throw new AccessDeniedException("User has no rights to access this resource");
    }

    @Override
    protected void afterCreate(Review entity) {
        metricsService.updateMetrics(entity.getBookId(), entity.getRating());
    }
}
