# Backend Frameworks Benchmark (Experimental Testbed)

A research project aimed at analyzing the architectural overhead and HTTP stack performance in modern backend frameworks. The experimental testbed is built using Docker containers with strict resource limits (e.g., 1 vCPU, 512MB RAM), allowing for a fair enforcement of saturation and testing server behavior under stress conditions.

## Evaluated Technologies
All applications are based on unified, lightweight base images (Debian Slim) and expose a standardized REST API:
* Node.js (Fastify)
* Go (Fiber)
* Python (FastAPI)
* Java (Spring Boot)
* C# / .NET 8 (ASP.NET Core)

## Repository Structure
* `docker-compose.yml` - Main orchestration file that brings up all servers and applies cgroups resource limits.
* `k6-scripts/` - A collection of scripts for the Grafana k6 load testing tool, implementing the 3 main research scenarios:
  * `scenario1_concurrency.js` - Concurrency and C10k problem test (Tail Latency).
  * `scenario2_payload.js` - JSON deserialization overhead and Garbage Collector stress test.
  * `scenario3_burst.js` - Sudden traffic spike behavior test (Burst/Spike Recovery).
* The remaining folders contain the source code and Dockerfile for each respective framework.

## How to run the tests

**1. Start the testbed environment**
From the root directory, start all containers in the background:
```bash
docker-compose up -d --build
```
The containers will listen on ports 3001 through 3005.

**2. Monitor resources (Optional)**
To track real-time RAM and CPU usage by individual frameworks:
```bash
docker stats
```

**3. Run a test scenario**
Select a scenario and use the k6 tool to generate load against a specific port (framework):
```bash
k6 run k6-scripts/scenario1_concurrency.js
```

**4. Stop the environment**
```bash
docker-compose down
```