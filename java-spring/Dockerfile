FROM maven:3.9-eclipse-temurin-21 AS builder
WORKDIR /app

COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app

COPY --from=builder /app/target/*.jar app.jar

EXPOSE 3000

CMD ["java", "-XX:ActiveProcessorCount=1", "-Xmx400m", "-jar", "app.jar", "--server.port=3000"]