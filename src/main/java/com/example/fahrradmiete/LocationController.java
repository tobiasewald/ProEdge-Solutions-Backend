package com.example.fahrradmiete;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import java.util.List;

@RestController
@RequestMapping("/api/locations")
public class LocationController {

    @GetMapping
    public List<Location> getAllLocations() {
        return List.of(
                new Location(1L, "Berlin"),
                new Location(2L, "Hamburg"),
                new Location(3L, "München")
        );
    }

    static class Location {
        private Long id;
        private String name;

        public Location(Long id, String name) {
            this.id = id;
            this.name = name;
        }

        public Long getId() {
            return id;
        }

        public String getName() {
            return name;
        }
    }
}
