using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);

builder.Logging.ClearProviders();

var app = builder.Build();

/**
 * Scenario 1
 * Minimal routing benchmark
 */
app.MapGet("/io", () =>
{
    return Results.Text("OKAY");
});

/**
 * Scenario 2
 * JSON serialization/deserialization benchmark
 */
app.MapPost("/json", ([FromBody] List<Item> items) =>
{
    var processed = items.Select(item => new Item
    {
        Id = item.Id,
        Name = item.Name.ToUpper(),
        Quantity = item.Quantity + 1
    }).ToList();

    return Results.Ok(processed);
});

/**
 * Scenario 3
 * Exception handling benchmark
 */
app.MapPost("/exceptions",
    ([FromHeader(Name = "Authorization")] string? authorization) =>
{
    if (authorization != "Bearer secret-token")
    {
        return Results.Unauthorized();
    }

    return Results.Text("OKAY");
});

app.Run("http://0.0.0.0:3000");

/**
 * DTO for Scenario 2
 */
class Item
{
    public int Id { get; set; }

    public string Name { get; set; } = string.Empty;

    public int Quantity { get; set; }
}