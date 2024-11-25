
package com.example.fahrradmiete;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/return")
public class ReturnController {

    private final ItemRepository itemRepository;

    public ReturnController(ItemRepository itemRepository) {
        this.itemRepository = itemRepository;
    }

    @PostMapping
    public ResponseEntity<String> returnItem(@RequestBody ReturnRequest returnRequest) {
        Item item = itemRepository.findById(returnRequest.getLocationId()).orElse(null);

        if (item == null) {
            return ResponseEntity.badRequest().body("Ungültiger Standort!");
        }

        item.setStatus("available");
        item.setLocation("Rückgabe abgeschlossen"); // Optional: Standort setzen
        itemRepository.save(item);

        return ResponseEntity.ok("Rückgabe erfolgreich!");
    }

    static class ReturnRequest {
        private Long locationId;

        public Long getLocationId() {
            return locationId;
        }

        public void setLocationId(Long locationId) {
            this.locationId = locationId;
        }
    }
}
