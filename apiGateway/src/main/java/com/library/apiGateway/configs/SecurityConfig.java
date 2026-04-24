package com.library.apiGateway.configs;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

@Configuration
public class SecurityConfig {

    private final String[] freeResourceUrls = {
            "/swagger-ui.html",
            "/swagger-ui/**",
            "/v3/api-docs/**",
            "/swagger-resources/**",
            "/aggregate/**",

        // Public APIs
            "/book-service/api/books/**",
            "/book-service/api/book/images/**",
            "/book-service/api/authors/**",
            "/book-service/api/publishers/**",
            "/book-service/api/genres/**",
            "/book-service/api/categories/**",
            "/review-service/api/reviews/**",
            "/review-service/api/review-metrics/**"
    };

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity httpSecurity) throws Exception {
        return httpSecurity
                .cors(cors -> cors.configurationSource(corsConfigurationSource()))
                .authorizeHttpRequests(authorize -> authorize
                        .requestMatchers(freeResourceUrls).permitAll()
                        .anyRequest().authenticated())
                .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
                .build();
    }

    /**
     * CORS configuration for API Gateway.
     * Frontend makes requests to the gateway, which proxies to internal services.
     * Swagger UI on the gateway also needs to be allowed.
     * Services do NOT need their own CORS config - this is the single point of CORS handling.
     */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        
        // Allow frontend origins
        configuration.setAllowedOriginPatterns(java.util.List.of(
                "http://localhost:4200",      // Angular dev
                "http://127.0.0.1:4200"
        ));
        
        // Allow all HTTP methods
        configuration.setAllowedMethods(java.util.List.of("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"));
        
        // Allow all headers (including Authorization for JWT)
        configuration.setAllowedHeaders(java.util.List.of("*"));
        
        // CRITICAL: Allow credentials (JWT tokens in Authorization header)
        configuration.setAllowCredentials(true);
        
        // Cache preflight for 1 hour
        configuration.setMaxAge(3600L);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}

