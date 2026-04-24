package org.library.bookservice.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.security.oauth2.server.resource.authentication.JwtGrantedAuthoritiesConverter;
import org.springframework.security.web.SecurityFilterChain;

import java.util.stream.Stream;

@Configuration
public class SecurityConfig {

    private final String[] freeResourceUrls = {
            "/swagger-ui.html/**",
            "/swagger-ui/**",
            "/api-docs/**",
            "/v3/api-docs/**",
            "/swagger-resources/**"
    };

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http.oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));

        http
                .authorizeHttpRequests(authorize -> authorize
                        .requestMatchers(freeResourceUrls).permitAll()
                        .requestMatchers("/actuator/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/books/**").permitAll()
                        .requestMatchers("/api/books/**").hasRole("ADMIN")
                        .requestMatchers(HttpMethod.GET, "/api/book/images/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/authors/**").permitAll()
                        .requestMatchers("/api/authors/**").hasRole("ADMIN")
                        .requestMatchers(HttpMethod.GET, "/api/publishers/**").permitAll()
                        .requestMatchers("/api/publishers/**").hasRole("ADMIN")
                        .requestMatchers(HttpMethod.GET, "/api/genres/**").permitAll()
                        .requestMatchers("/api/genres/**").hasRole("ADMIN")
                        .requestMatchers(HttpMethod.GET, "/api/categories/**").permitAll()
                        .requestMatchers("/api/categories/**").hasRole("ADMIN")
                        .anyRequest().authenticated());

        return http.build();
    }

    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        var converter = new JwtAuthenticationConverter();
        var jwtGrantedAuthoritiesConverter = new JwtGrantedAuthoritiesConverter();
        converter.setPrincipalClaimName("preferred_username");
        converter.setJwtGrantedAuthoritiesConverter(jwt -> {
            var authorities = jwtGrantedAuthoritiesConverter.convert(jwt);
            var roles = jwt.getClaimAsStringList("user_roles");

            return Stream.concat(authorities.stream(), roles.stream()
                            .filter(role -> role.startsWith("ROLE_"))
                            .map(SimpleGrantedAuthority::new)
                            .map(GrantedAuthority.class::cast))
                    .toList();
        });

        return converter;
    }
}
