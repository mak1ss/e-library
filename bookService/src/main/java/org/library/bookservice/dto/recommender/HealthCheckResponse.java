package org.library.bookservice.dto.recommender;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Health check response from recommenderService
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class HealthCheckResponse {
    private String status;
    private Boolean modelsLoaded;
    private Map<String, Object> modelMetadata;
}
