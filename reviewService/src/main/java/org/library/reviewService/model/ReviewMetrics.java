package org.library.reviewService.model;

import lombok.Data;
import org.library.reviewService.model.base.Identifiable;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.Map;

@Data
@Document("review_metrics")
public class ReviewMetrics implements Identifiable {

    @Id
    private String id;

    private Integer bookId;

    private Integer totalReviews;

    private Double averageRating;

    private Map<String, Integer> reviewCountsRating;
}
