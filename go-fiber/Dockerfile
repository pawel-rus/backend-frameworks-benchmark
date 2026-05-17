FROM golang:1.22-bookworm AS builder
WORKDIR /app

COPY go.mod main.go ./

RUN go get github.com/gofiber/fiber/v2
RUN go mod tidy

RUN go build -o main .

FROM debian:bookworm-slim
WORKDIR /app

COPY --from=builder /app/main .

EXPOSE 3000

ENV GOMAXPROCS=1

CMD ["./main"]