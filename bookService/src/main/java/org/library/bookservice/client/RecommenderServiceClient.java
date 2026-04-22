package org.library.bookservice.client;

import org.library.bookservice.dto.recommender.*;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.List;

/**
 * OpenFeign client for recommenderService
 */
@FeignClient(
    name = "recommender-service",
    url = "${recommender-service.url}",
    fallback = RecommenderServiceClientFallback.class
)
public interface RecommenderServiceClient {
    
    /**
     * Get similar books using content-based filtering
     * Called in real-time (no caching at this level)
     */
    @PostMapping("/api/v1/recommendations/similar-books")
    ResponseEntity<List<SimilarBookResponse>> getSimilarBooks(
        @RequestBody GetSimilarBooksRequest request
    );
    
    /**
     * Get personalized recommendations (pre-computed collaborative filtering)
     * Results cached in MongoDB by bookService
     */
    @PostMapping("/api/v1/recommendations/personalized")
    ResponseEntity<List<PersonalizedRecommendationResponse>> getPersonalizedRecommendations(
        @RequestBody GetPersonalizedRecommendationsRequest request
    );
    
    /**
     * Health check endpoint
     */
    @GetMapping("/api/v1/recommendations/health")
    ResponseEntity<HealthCheckResponse> getHealth();
}
