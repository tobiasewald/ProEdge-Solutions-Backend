
package com.example.fahrradmiete;

import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
public class Booking {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    private User user;

    @ManyToOne
    private Item item;

    private LocalDateTime startDate;
    private LocalDateTime endDate;

    // Getters and Setters
}
