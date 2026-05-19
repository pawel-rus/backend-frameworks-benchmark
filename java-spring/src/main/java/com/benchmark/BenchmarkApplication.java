package com.benchmark;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@SpringBootApplication
@RestController
public class BenchmarkApplication {

    public static void main(String[] args) {
        SpringApplication.run(BenchmarkApplication.class, args);
    }

    /**
     * Endpoint for scenario 1
     * @return HttpStatus wrapped in ResponseEntity
     */
    @GetMapping("/io")
    public ResponseEntity<String> minimalRouting() {
        return new ResponseEntity<>("OKAY", HttpStatus.OK);
    }

    /**
     * Scenario 2
     * JSON serialization/deserialization benchmark
     */
    @PostMapping("/json")
    public ResponseEntity<List<Item>> processJson(
            @RequestBody List<Item> items
    ) {

        List<Item> processed = items.stream()
                .map(item -> new Item(
                        item.id(),
                        item.name().toUpperCase(),
                        item.quantity() + 1
                ))
                .collect(Collectors.toList());

        return ResponseEntity.ok(processed);
    }

    /**
     * Endpoint for scenario 3
     *
     * @param authorization representing authorization field from RequestHeader
     * @return HttpStatus wrapped in ResponseEntity
     */
    @PostMapping("/exceptions")
    public ResponseEntity<String> processJson(
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        
        if (authorization == null || !authorization.equals("Bearer secret-token")) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Unauthorized access to endpoint. Either no, or invalid bearer token provided");
        }

        return new ResponseEntity<>("OKAY", HttpStatus.OK);
    }

    /**
     * DTO for scenario 2
     * @param id
     * @param name
     * @param quantity
     */
    public record Item(long id, String name, int quantity){}

    /**
     * Global exception handler for scenario 3
     * Catches ResponseStatusException and wraps it into BAD_REQUEST HTTP response
     *
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> handleException(Exception ex) {

        Map<String, String> error = new HashMap<>();
        error.put("error", ex.getMessage());

        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(error);
    }
}