package com.example.fahrradmiete;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // Überprüfung, ob eine Personalnummer existiert
    boolean existsByPersonalNumber(String personalNumber);

    // Suche nach Benutzer über Personalnummer
    User findByPersonalNumber(String personalNumber);
}
