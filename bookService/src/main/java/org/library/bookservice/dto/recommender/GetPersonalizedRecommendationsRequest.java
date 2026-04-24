package org.library.bookservice.dto.recommender;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Request DTO for getting personalized recommendations
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GetPersonalizedRecommendationsRequest {
    private List<Integer> userSeedBooks;
    private Integer topK;
}
