package com.example.fahrradmiete;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/register", "/api/login", "/api/locations/**", "/api/items/**", "/api/return/**").permitAll() // Öffentliche Endpunkte
                        .anyRequest().authenticated() // Andere Endpunkte erfordern Authentifizierung
                )
                .csrf(AbstractHttpConfigurer::disable) // CSRF deaktivieren
                .cors(AbstractHttpConfigurer::disable); // CORS deaktivieren oder konfigurieren (je nach Bedarf)

        return http.build();
    }
}
