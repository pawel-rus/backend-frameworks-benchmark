package main

import (
	"strings"

	"github.com/gofiber/fiber/v2"
)

/**
 * DTO for Scenario 2
 */
type Item struct {
	ID       int    `json:"id"`
	Name     string `json:"name"`
	Quantity int    `json:"quantity"`
}

func main() {

	app := fiber.New(fiber.Config{
		DisableStartupMessage: true,
	})

	/**
	 * Scenario 1
	 * Minimal routing benchmark
	 */
	app.Get("/io", func(c *fiber.Ctx) error {
		return c.SendString("OKAY")
	})

	/**
	 * Scenario 2
	 * JSON serialization/deserialization benchmark
	 */
	app.Post("/json", func(c *fiber.Ctx) error {

		var items []Item

		if err := c.BodyParser(&items); err != nil {
			return fiber.NewError(
				fiber.StatusBadRequest,
				"Invalid JSON payload",
			)
		}

		processed := make([]Item, len(items))

		for i, item := range items {

			processed[i] = Item{
				ID:       item.ID,
				Name:     strings.ToUpper(item.Name),
				Quantity: item.Quantity + 1,
			}
		}

		return c.JSON(processed)
	})

	/**
	 * Scenario 3
	 * Exception handling benchmark
	 */
	app.Post("/exceptions", func(c *fiber.Ctx) error {

		authorization := c.Get("Authorization")

		if authorization != "Bearer secret-token" {

			return fiber.NewError(
				fiber.StatusUnauthorized,
				"Unauthorized access to endpoint. Either no, or invalid bearer token provided",
			)
		}

		return c.SendString("OKAY")
	})

	app.Listen(":3000")
}