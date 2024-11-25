
package com.example.fahrradmiete;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/items")
public class ItemController {

    private final ItemRepository itemRepository;

    public ItemController(ItemRepository itemRepository) {
        this.itemRepository = itemRepository;
    }

    // Für die Admin-Übersicht: Gibt ALLE Items zurück
    @GetMapping("/all")
    public ResponseEntity<List<Item>> getAllItems() {
        return ResponseEntity.ok(itemRepository.findAll());
    }

    // Bestehender Endpunkt für verfügbare Items
    @GetMapping
    public ResponseEntity<List<Item>> getAvailableItems() {
        return ResponseEntity.ok(itemRepository.findByBatteryStatusGreaterThanEqualAndStatus(80, "available"));
    }

    @PostMapping("/book")
    public ResponseEntity<String> bookItem(@RequestBody BookingRequest bookingRequest) {
        Item item = itemRepository.findById(bookingRequest.getItemId()).orElse(null);
        if (item != null && item.getStatus().equals("available")) {
            item.setStatus("booked");
            itemRepository.save(item);
            return ResponseEntity.ok("Item booked successfully");
        }
        return ResponseEntity.badRequest().body("Item is not available");
    }
    @PostMapping
    public Item createItem(@RequestBody Item item) {
        return itemRepository.save(item);
    }
}
