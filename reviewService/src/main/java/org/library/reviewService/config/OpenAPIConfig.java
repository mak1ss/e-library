package org.library.reviewService.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;

import io.swagger.v3.oas.models.servers.Server;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenAPIConfig {

    @Value("${server.port}")
    private String port;

    @Bean
    public OpenAPI configureOpenAPI() {
        Server server = new Server().url("http://localhost:" + port);
        return new OpenAPI()
                .servers(List.of(server))
                .info(new Info().title("Review API")
                        .description("API for Review Service")
                        .version("0.1")
                        .license(new License().name("Apache 2.0")));
    }

}
