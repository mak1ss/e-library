package org.library.bookservice.dto.recommender;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * Explanation of why a book was recommended
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExplanationDetails {
    
    /**
     * Main reason text (e.g., "Content similarity: 5 matching topics")
     */
    private String primaryReason;
    
    /**
     * Type of explanation (TF_IDF_MATCH, COLLABORATIVE_FILTER)
     */
    private String reasonType;
    
    /**
     * Top contributing factors (e.g., keywords for TF-IDF, book IDs for collaborative)
     */
    private List<String> topContributors;
    
    /**
     * Confidence score (0.0 to 1.0)
     */
    private Double confidenceScore;
    
    /**
     * Additional context details
     */
    private Map<String, Object> details;
}
