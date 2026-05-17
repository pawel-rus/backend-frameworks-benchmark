#!/bin/bash

if [ -z "$1" ]; then
  echo "Using: ./scenario3_run.sh [node|go|python|java|csharp]"
  exit 1
fi

FRAMEWORK=$1

case $FRAMEWORK in
  node) PORT=3001; SERVICE="node-fastify"; CONTAINER="benchmark-node"; NAME="Node.js (Fastify)" ;;
  go) PORT=3002; SERVICE="go-fiber"; CONTAINER="benchmark-go"; NAME="Go (Fiber)" ;;
  python) PORT=3003; SERVICE="python-fastapi"; CONTAINER="benchmark-python"; NAME="Python (FastAPI)" ;;
  java) PORT=3004; SERVICE="java-spring"; CONTAINER="benchmark-java"; NAME="Java (Spring Boot)" ;;
  csharp) PORT=3005; SERVICE="csharp-dotnet"; CONTAINER="benchmark-csharp"; NAME="C# (.NET 8)" ;;
  *) echo "Error: Unknown framework."; exit 1 ;;
esac

echo "======================================================"
echo " Running tests for: $NAME"
echo "======================================================"

CSV_FILE="results_${FRAMEWORK}.csv"
echo "ERROR_RATE,AVG_CPU,RPS" > $CSV_FILE

echo "-> Removing old container to prevent conflicts..."
docker rm -f $CONTAINER 2>/dev/null

echo "-> Building and starting service '$SERVICE'..."
docker-compose up -d --build $SERVICE

echo "Container ready. Waiting 15s for stabilization..."
sleep 15

for rate in 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
do
    echo -e "\n======================================================"
    echo " ---> Test ERROR_RATE = $rate (Port: $PORT) <---"
    echo "======================================================"
    
    > cpu_temp.log
    
    while true; do
        docker stats $CONTAINER --no-stream --format "{{.CPUPerc}}" | tr -d '%' >> cpu_temp.log
        sleep 1
    done &
    MONITOR_PID=$!
    
    K6_OUTPUT=$(k6 run -e PORT=$PORT -e ERROR_RATE=$rate k6-scripts/scenario3_exceptions.js 2>&1)
    echo "$K6_OUTPUT"
    
    kill $MONITOR_PID 2>/dev/null
    wait $MONITOR_PID 2>/dev/null
    
    AVG_CPU=$(awk '{ sum += $1; n++ } END { if (n > 0) printf "%.2f", sum / n; }' cpu_temp.log)
    
    RPS=$(echo "$K6_OUTPUT" | grep "http_reqs" | awk '{print $3}' | tr -d '/s')
    
    if [ -z "$RPS" ]; then RPS="0.0"; fi
    
    echo -e "\n📊 [RESULT FOR ERROR_RATE $rate] AVG CPU: $AVG_CPU %, RPS: $RPS"
    
    echo "$rate,$AVG_CPU,$RPS" >> $CSV_FILE
    
    echo "Cooling down the server (5s)..."
    sleep 5
done

rm -f cpu_temp.log
echo -e "\n Stopping container $SERVICE..."
docker-compose stop $SERVICE

echo -e "\n✅ Completed! Results saved to $CSV_FILE."