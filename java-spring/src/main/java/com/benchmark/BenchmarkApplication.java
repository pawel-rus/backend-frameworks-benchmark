package com.benchmark;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.stream.Collectors;

@SpringBootApplication
@RestController
public class BenchmarkApplication {

    public static void main(String[] args) {
        SpringApplication.run(BenchmarkApplication.class, args);
    }

    @GetMapping("/io")
    public StatusResponse minimalRouting() {
        return new StatusResponse("ok");
    }

    @PostMapping("/json")
    public List<ProcessedItem> processJson(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @RequestBody List<Item> items) {
        
        if (authorization == null || !authorization.equals("Bearer secret-token")) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Unauthorized");
        }

        long now = System.currentTimeMillis();
        return items.stream()
                .map(item -> new ProcessedItem(item.id(), item.name(), now))
                .collect(Collectors.toList());
    }

    public record StatusResponse(String status) {}
    public record Item(int id, String name) {}
    public record ProcessedItem(int id, String name, long processedAt) {}
}