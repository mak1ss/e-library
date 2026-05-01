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
    private List<SeedBook> userSeedBooks;
    private Integer topK;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class SeedBook {
        private Integer bookId;
        private Integer rating;
    }
}
