package org.library.reviewService.model;

import lombok.Data;
import org.library.reviewService.model.base.Identifiable;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.util.Map;
import java.util.TreeMap;

@Data
@Document("review_metrics")
public class ReviewMetrics implements Identifiable {

    @Id
    private String id;

    private Integer bookId;

    private Integer totalReviews;

    @Field
    private Double averageRating;

    private Map<String, Integer> reviewCountsRating = new TreeMap<>();
}
