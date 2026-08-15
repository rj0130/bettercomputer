using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapGet("/health", () => Results.Ok(new { status = "Inventory API OK" }));

app.MapGet("/inventory/sample", () => new[] {
    new { sku = "BC-CPU-01", qty = 12 },
    new { sku = "BC-RAM-08GB", qty = 40 }
});

app.Run();
