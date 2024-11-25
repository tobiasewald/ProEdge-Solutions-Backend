
package com.example.fahrradmiete;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ItemRepository extends JpaRepository<Item, Long> {
    List<Item> findByBatteryStatusGreaterThanEqualAndStatus(int batteryStatus, String status);
}
