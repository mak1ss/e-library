package org.library.reviewService.dto.reviewMetrics;

import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.Map;

@Data
@EqualsAndHashCode(callSuper=false)
@Builder
public class ReviewMetricsResponse {

    private String id;

    private Integer bookId;

    private Integer totalReviews;

    private Double averageRating;

    private Map<String, Integer> reviewCountsRating;
}
