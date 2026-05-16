FROM mcr.microsoft.com/dotnet/sdk:8.0-bookworm-slim AS builder
WORKDIR /app

COPY *.csproj ./
RUN dotnet restore

COPY Program.cs ./
RUN dotnet publish -c Release -o /out

FROM mcr.microsoft.com/dotnet/aspnet:8.0-bookworm-slim
WORKDIR /app

COPY --from=builder /out .

EXPOSE 3000

CMD ["dotnet", "csharp-dotnet.dll"]