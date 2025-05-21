package org.library.reviewService.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;

import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.OAuthFlow;
import io.swagger.v3.oas.models.security.OAuthFlows;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenAPIConfig {

    @Value("${server.port}")
    private String port;

    @Value("${spring.security.oauth2.resourceserver.jwt.token-uri}")
    private String keycloakTokenUrl;

    private String passwordSecurityScheme = "passwordFlow";

    private String clientCredentialsSecurityScheme = "clientCredentialsFlow";

    @Bean
    public OpenAPI configureOpenAPI() {
        Server server = new Server().url("http://localhost:" + port);
        return new OpenAPI()
                .servers(List.of(server))
                .info(new Info().title("Review API")
                        .description("API for Review Service")
                        .version("0.1")
                        .license(new License().name("Apache 2.0")))
                .components(new Components()
                        .addSecuritySchemes(passwordSecurityScheme, passwordFlowScheme())
                        .addSecuritySchemes(clientCredentialsSecurityScheme, clientCredentialsScheme()))
                .addSecurityItem(new SecurityRequirement()
                        .addList(passwordSecurityScheme)
                        .addList(clientCredentialsSecurityScheme));
    }

    private SecurityScheme passwordFlowScheme() {
        return new SecurityScheme()
                .type(SecurityScheme.Type.OAUTH2)
                .description("Resource Owner Password Flow")
                .flows(new OAuthFlows()
                        .password(new OAuthFlow()
                                .tokenUrl(keycloakTokenUrl)));
    }

    private SecurityScheme clientCredentialsScheme() {
        return new SecurityScheme()
                .type(SecurityScheme.Type.OAUTH2)
                .description("Client Credentials Flow")
                .flows(new OAuthFlows()
                        .clientCredentials(new OAuthFlow()
                                .tokenUrl(keycloakTokenUrl)));
    }
}
