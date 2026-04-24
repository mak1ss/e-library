package org.library.reviewService.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.mongodb.core.mapping.Field;

/**
 * Embedded document for review relevance scoring result.
 * Stores the score computed by the Python recommender service.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReviewScoringResult {
    
    /**
     * Relevance score (0.0 to 1.0).
     * Higher values indicate the review is more semantically relevant to the book.
     */
    @Field("score")
    private Double score;
    
    /**
     * Model version used for scoring (e.g., "all-MiniLM-L6-v2-v1.0").
     * Allows retroactive re-scoring when model is updated.
     */
    @Field("model_version")
    private String modelVersion;
    
    /**
     * Raw cosine similarity before normalization [-1, 1].
     * Useful for debugging and ML monitoring.
     */
    @Field("raw_cosine_similarity")
    private Double rawCosineSimilarity;
    
    /**
     * Confidence in the score (0.0 to 1.0).
     * (|cosine_sim| × 0.7) + (embedding_quality × 0.3).
     * Helps upstream decide fallback behavior if confidence is low.
     */
    @Field("confidence")
    private Double confidence;
    
    /**
     * Error code if scoring failed (e.g., "NULL_REVIEW_TEXT", "INVALID_EMBEDDING").
     * NULL if successful.
     */
    @Field("error_code")
    private String errorCode;
    
    /**
     * Error message if scoring failed.
     * NULL if successful.
     */
    @Field("error_message")
    private String errorMessage;
    
    /**
     * Unix timestamp when score was computed (milliseconds).
     */
    @Field("timestamp")
    private Long timestamp;
    
    /**
     * Processing latency in milliseconds.
     * Used for SLA monitoring and performance tracking.
     */
    @Field("processing_time_ms")
    private Long processingTimeMs;
    
    /**
     * Whether scoring was successful (no error).
     */
    public boolean isSuccessful() {
        return errorCode == null && errorMessage == null && score != null;
    }
}
