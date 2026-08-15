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

app.MapGet("/health", () => Results.Ok(new { status = "Staff API OK" }));

app.MapGet("/staff/sample", () => new[] {
    new { id = Guid.NewGuid(), name = "Alex", skills = new[] { "assembly", "testing" } }
});

app.Run();
