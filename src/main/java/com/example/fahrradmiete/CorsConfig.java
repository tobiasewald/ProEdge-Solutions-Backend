package com.example.fahrradmiete;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsConfig {

    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**") // Erlaubt alle Endpunkte
                        .allowedOrigins("*") // Erlaubt Anfragen von allen Ursprüngen
                        .allowedMethods("*") // Erlaubt alle HTTP-Methoden
                        .allowedHeaders("*") // Erlaubt alle Header
                        .allowCredentials(false); // Keine Cookies oder Authentifizierung
            }
        };
    }
}
