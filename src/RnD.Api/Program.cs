using Microsoft.AspNetCore.Builder;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapGet("/health", () => Results.Ok(new { status = "RnD API OK" }));

app.MapGet("/rnd/logs/sample", () => new[] {
    new { id = Guid.NewGuid(), title = "Test config", createdAt = DateTime.UtcNow }
});

app.Run();
