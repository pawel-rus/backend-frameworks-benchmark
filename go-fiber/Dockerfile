FROM golang:1.22-bookworm AS builder
WORKDIR /app

RUN go mod init benchmark-go && go get github.com/gofiber/fiber/v2

COPY main.go .
RUN go build -o main .

FROM debian:bookworm-slim
WORKDIR /app

COPY --from=builder /app/main .

EXPOSE 3000

ENV GOMAXPROCS=1

CMD ["./main"]