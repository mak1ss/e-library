package org.library.reviewService.service;

import lombok.AllArgsConstructor;
import org.library.reviewService.client.BookServiceClient;
import org.library.reviewService.model.Review;
import org.library.reviewService.repository.BaseRepository;
import org.library.reviewService.repository.ReviewRepository;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.stereotype.Service;

import java.util.NoSuchElementException;

@Service
@AllArgsConstructor
public class ReviewService extends AbstractService<Review> {

    private final ReviewRepository reviewRepository;
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
            var response = bookClient.getById(entity.getBookId());
        } catch (NoSuchElementException e) {
            throw new IllegalArgumentException("No book was found with id " + entity.getBookId());
        }
    }
}
