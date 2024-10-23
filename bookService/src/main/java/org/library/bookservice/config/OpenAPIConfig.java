package org.library.bookservice.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenAPIConfig {

    @Bean
    public OpenAPI configureOpenAPI() {
        return new OpenAPI()
                .info(new Info().title("Book API")
                        .description("API for Book Service")
                        .version("0.1")
                        .license(new License().name("Apache 2.0")));
    }
}
