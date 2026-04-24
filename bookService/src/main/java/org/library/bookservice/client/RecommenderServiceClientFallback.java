package org.library.bookservice.client;

import org.library.bookservice.dto.recommender.*;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.List;

/**
 * Fallback implementation for RecommenderServiceClient (circuit breaker pattern)
 */
@Component
public class RecommenderServiceClientFallback implements RecommenderServiceClient {
    
    @Override
    public ResponseEntity<List<SimilarBookResponse>> getSimilarBooks(GetSimilarBooksRequest request) {
        // Return empty list when recommender service is down
        return ResponseEntity.ok(Collections.emptyList());
    }
    
    @Override
    public ResponseEntity<List<PersonalizedRecommendationResponse>> getPersonalizedRecommendations(
        GetPersonalizedRecommendationsRequest request) {
        // Return empty list when recommender service is down
        return ResponseEntity.ok(Collections.emptyList());
    }
    
    @Override
    public ResponseEntity<HealthCheckResponse> getHealth() {
        // Service unavailable
        return ResponseEntity.status(503).body(null);
    }
}
