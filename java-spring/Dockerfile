FROM maven:3.9-eclipse-temurin-21 AS builder
WORKDIR /app

COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app

COPY --from=builder /app/target/*.jar app.jar

EXPOSE 3000

# Run JRE optimized for 2 CPU cores, 1.5GB Heap, and Spring Boot 3.2+ Virtual Threads (Project Loom)
CMD ["java", "-XX:ActiveProcessorCount=2", "-Xmx1500m", "-jar", "app.jar", "--server.port=3000", "--spring.threads.virtual.enabled=true"]