package org.library.reviewService.service;

import lombok.AllArgsConstructor;
import org.library.reviewService.model.Review;
import org.library.reviewService.repository.BaseRepository;
import org.library.reviewService.repository.ReviewRepository;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
public class ReviewService extends AbstractService<Review> {

    private final ReviewRepository reviewRepository;

    private final MongoOperations mongoOperations;

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
}
