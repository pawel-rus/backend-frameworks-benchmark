package main

import (
	"time"
	"github.com/gofiber/fiber/v2"
)

type Item struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

type ProcessedItem struct {
	Item
	ProcessedAt int64 `json:"processedAt"`
}

func main() {
	app := fiber.New(fiber.Config{DisableStartupMessage: true})

	app.Get("/io", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"status": "ok"})
	})

	app.Post("/json", func(c *fiber.Ctx) error {
		auth := c.Get("Authorization")
		
		if auth != "Bearer secret-token" {
			return fiber.NewError(fiber.StatusUnauthorized, "Unauthorized")
		}

		var items []Item
		if err := c.BodyParser(&items); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Bad Request")
		}

		now := time.Now().UnixMilli()
		processed := make([]ProcessedItem, len(items))
		
		for i, item := range items {
			processed[i] = ProcessedItem{
				Item:        item,
				ProcessedAt: now,
			}
		}

		return c.JSON(processed)
	})

	app.Listen(":3000")
}