package org.library.reviewService.service;

import lombok.AllArgsConstructor;
import org.library.reviewService.model.ReviewMetrics;
import org.library.reviewService.repository.BaseRepository;
import org.library.reviewService.repository.ReviewMetricsRepository;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
public class ReviewMetricsService extends AbstractService<ReviewMetrics> {

    private final ReviewMetricsRepository reviewMetricsRepository;

    private final MongoOperations mongoOperations;

    @Override
    protected BaseRepository<ReviewMetrics> getRepository() {
        return reviewMetricsRepository;
    }

    @Override
    protected MongoOperations getMongoOperations() {
        return mongoOperations;
    }

    @Override
    protected Class<ReviewMetrics> getEntityClass() {
        return ReviewMetrics.class;
    }
}
