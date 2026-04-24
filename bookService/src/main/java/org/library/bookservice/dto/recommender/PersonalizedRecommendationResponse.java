package org.library.bookservice.dto.recommender;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * DTO for personalized recommendation response from recommenderService
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PersonalizedRecommendationResponse {
    private Integer bookId;
    private Float score;
    private ExplanationDetails explanation;
    private List<Integer> seedBookIds;
}
