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

app.MapGet("/health", () => Results.Ok(new { status = "Management API OK" }));

app.MapGet("/management/projects/sample", () => new[] {
    new { id = Guid.NewGuid(), name = "Assembly Line Upgrade", status = "planning" }
});

app.Run();
