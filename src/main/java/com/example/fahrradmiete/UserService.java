
package com.example.fahrradmiete;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private static final Logger logger = LoggerFactory.getLogger(UserService.class);
    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public boolean register(User user) {
        logger.info("Registering user with personalNumber: {}", user.getPersonalNumber());

        if (userRepository.existsByPersonalNumber(user.getPersonalNumber())) {
            logger.warn("User with personalNumber {} already exists", user.getPersonalNumber());
            return false;
        }

        user.setPassword(new BCryptPasswordEncoder().encode(user.getPassword()));
        userRepository.save(user);
        logger.info("User registered successfully with personalNumber: {}", user.getPersonalNumber());
        return true;
    }
}
