#!/bin/bash

declare -A SERVICES=(
#   ["node"]="3001"
#   ["go"]="3002"
  ["python"]="3003"
#   ["java"]="3004"
#   ["csharp"]="3005"
)

PAYLOADS=(1 5 10 25 50 75 100)

for tech in "${!SERVICES[@]}"
do

  port=${SERVICES[$tech]}

  for size in "${PAYLOADS[@]}"
  do

    echo "Running $tech with ${size}KB payload"

    RAM_OUTPUT="k6/results/${tech}_${size}kb_ram.csv"

    ./scripts/collect-docker-stats.sh \
      benchmark-$tech \
      $RAM_OUTPUT &

    STATS_PID=$!

    k6 run \
      -e BASE_URL=http://localhost:$port \
      -e PAYLOAD_KB=$size \
      --summary-export=k6/results/${tech}_${size}kb.json \
      k6/json-benchmark.js

    kill $STATS_PID

    sleep 5

  done
done