#!/bin/bash

if [ -z "$1" ]; then
  echo "Using: ./scenario3_run.sh [all|node|go|python|java|csharp]"
  exit 1
fi

# 1. Check if running all frameworks or just a specific one
if [ "$1" == "all" ]; then
  TARGETS=("node" "go" "python" "java" "csharp")
  echo "🚀 Starting massive test for all frameworks..."
else
  TARGETS=("$1")
fi

# 2. Main loop iterating over frameworks
for FRAMEWORK in "${TARGETS[@]}"; do

  case $FRAMEWORK in
    node) PORT=3001; SERVICE="node-fastify"; CONTAINER="benchmark-node"; NAME="Node.js (Fastify)" ;;
    go) PORT=3002; SERVICE="go-fiber"; CONTAINER="benchmark-go"; NAME="Go (Fiber)" ;;
    python) PORT=3003; SERVICE="python-fastapi"; CONTAINER="benchmark-python"; NAME="Python (FastAPI)" ;;
    java) PORT=3004; SERVICE="java-spring"; CONTAINER="benchmark-java"; NAME="Java (Spring Boot)" ;;
    csharp) PORT=3005; SERVICE="csharp-dotnet"; CONTAINER="benchmark-csharp"; NAME="C# (.NET 8)" ;;
    *) echo "Error: Unknown framework: $FRAMEWORK"; continue ;;
  esac

  echo -e "\n======================================================"
  echo " 🛠️ Running tests for: $NAME"
  echo "======================================================"

  CSV_FILE="results_${FRAMEWORK}.csv"
  echo "ERROR_RATE,RUN,AVG_CPU,RPS,AVG_LAT,P95_LAT,P99_LAT" > $CSV_FILE

  echo "-> Removing old container to prevent conflicts..."
  docker rm -f $CONTAINER 2>/dev/null

  echo "-> Building and starting service '$SERVICE'..."
  docker-compose up -d --build $SERVICE

  echo "Container ready. Waiting 15s for stabilization..."
  sleep 15

  for rate in 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
  do
      echo -e "\n------------------------------------------------------"
      echo " ---> Test ERROR_RATE = $rate (Port: $PORT) <---"
      echo "------------------------------------------------------"
      
      for run in 1 2 3 4 5; do
          echo "   * Run $run/5 for ERROR_RATE $rate..."
          
          > cpu_temp.log
          
          while true; do
              docker stats $CONTAINER --no-stream --format "{{.CPUPerc}}" | tr -d '%' >> cpu_temp.log
              sleep 1
          done &
          MONITOR_PID=$!
          
          K6_OUTPUT=$(k6 run --summary-export temp_summary.json -e PORT=$PORT -e ERROR_RATE=$rate k6-scripts/scenario3_exceptions.js 2>&1)
          
          LATENCIES=$(python3 -c "
import json
try:
    with open('temp_summary.json') as f: d = json.load(f)
    m = d['metrics']['http_req_duration']
    print(f\"{m.get('avg', 0):.3f},{m.get('p(95)', 0):.3f},{m.get('p(99)', 0):.3f}\")
except:
    print('0.0,0.0,0.0')
")
          AVG_LAT=$(echo $LATENCIES | cut -d',' -f1)
          P95_LAT=$(echo $LATENCIES | cut -d',' -f2)
          P99_LAT=$(echo $LATENCIES | cut -d',' -f3)
          
          # Extract errors (optionally filter console output to keep it clean)
          echo "$K6_OUTPUT" | grep -E "http_reqs|iterations"
          
          kill $MONITOR_PID 2>/dev/null
          wait $MONITOR_PID 2>/dev/null
          
          # Use awk, replacing commas with dots for locales with comma as decimal separator
          AVG_CPU=$(cat cpu_temp.log | tr ',' '.' | awk '{ sum += $1; n++ } END { if (n > 0) printf "%.2f", sum / n; }')
          
          RPS=$(echo "$K6_OUTPUT" | grep "http_reqs" | awk '{print $3}' | tr -d '/s' | tr ',' '.')
          
          if [ -z "$RPS" ]; then RPS="0.0"; fi
          
          echo -e "📊 [RESULT] ERROR_RATE $rate (Run $run) -> AVG CPU: $AVG_CPU %, RPS: $RPS, AVG LAT: $AVG_LAT ms, P99 LAT: $P99_LAT ms"
          
          echo "$rate,$run,$AVG_CPU,$RPS,$AVG_LAT,$P95_LAT,$P99_LAT" >> $CSV_FILE
          rm -f temp_summary.json
          
          echo "Cooling down the server (5s)..."
          sleep 5
      done
  done

  rm -f cpu_temp.log
  echo -e "\n✅ Stopping container $SERVICE..."
  docker-compose stop $SERVICE

done

# 3. GENERATE PLOTS AFTER ALL TESTS ARE COMPLETED
echo -e "\n======================================================"
echo "🎯 All tests completed! Time to generate plots."
echo "======================================================"

if command -v python3 &>/dev/null && python3 -c "import pandas, matplotlib" 2>/dev/null; then
  python3 plot_scenario3.py
else
  echo "⚠️ Missing libraries (pandas/matplotlib). To generate plots run:"
  echo "pip install pandas matplotlib"
  echo "and then run manually: python3 plot_scenario3.py"
fi