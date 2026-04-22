package org.library.bookservice.dto.recommender;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request DTO for getting similar books
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GetSimilarBooksRequest {
    private Integer bookId;
    private Integer topK;
}
