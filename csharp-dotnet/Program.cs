using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
var app = builder.Build();

app.MapGet("/io", () => Results.Ok(new { status = "ok" }));

app.MapPost("/json", ([FromHeader(Name = "Authorization")] string? authorization, [FromBody] List<Item> items) =>
{
    if (authorization != "Bearer secret-token")
    {
        return Results.Unauthorized();
    }

    var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
    
    var processed = items.Select(item => new ProcessedItem
    {
        Id = item.Id,
        Name = item.Name,
        ProcessedAt = now
    }).ToList();

    return Results.Ok(processed);
});

app.Run("http://0.0.0.0:3000");

class Item
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
}

class ProcessedItem : Item
{
    public long ProcessedAt { get; set; }
}