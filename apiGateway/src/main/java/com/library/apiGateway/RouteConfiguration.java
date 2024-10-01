package com.library.apiGateway;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.function.RequestPredicates;
import org.springframework.web.servlet.function.RouterFunction;
import org.springframework.web.servlet.function.ServerResponse;

import static org.springframework.cloud.gateway.server.mvc.filter.BeforeFilterFunctions.stripPrefix;
import static org.springframework.cloud.gateway.server.mvc.handler.GatewayRouterFunctions.route;
import static org.springframework.cloud.gateway.server.mvc.handler.HandlerFunctions.http;

@Configuration
public class RouteConfiguration {

    @Value("${services.url.book}")
    private String BOOK_SERVICE_URL;

    @Value("${services.url.review}")
    private String REVIEW_SERVICE_URL;

    @Bean
    public RouterFunction<ServerResponse> bookServiceRoute() {
        return route("book-service")
                .route(RequestPredicates.path("/book-service/**"), http(BOOK_SERVICE_URL))
                .before(stripPrefix(1))
                .build();
    }

    @Bean RouterFunction<ServerResponse> reviewServiceRoute() {
        return route("review-service")
                .route(RequestPredicates.path("/review-service/**"), http(REVIEW_SERVICE_URL))
                .before(stripPrefix(1))
                .build();
    }
}
