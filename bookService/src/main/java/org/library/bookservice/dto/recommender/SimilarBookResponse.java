package org.library.bookservice.dto.recommender;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for similar book response from recommenderService
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SimilarBookResponse {
    private Integer bookId;
    private Float similarityScore;
    private ExplanationDetails explanation;
}
