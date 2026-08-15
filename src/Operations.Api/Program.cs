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

app.MapGet("/health", () => Results.Ok(new { status = "Operations API OK" }));

app.MapGet("/ops/schedule/sample", () => new[] {
    new { workOrderId = Guid.NewGuid(), assignedTo = "Alex", start = DateTime.UtcNow }
});

app.Run();
