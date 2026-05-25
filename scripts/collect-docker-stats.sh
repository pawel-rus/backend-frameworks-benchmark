#!/bin/bash

CONTAINER_NAME=$1
OUTPUT_FILE=$2

echo "timestamp,container,mem_usage_mb,cpu_percent" > $OUTPUT_FILE

while true
do
    docker stats --no-stream --format \
    "{{.Name}},{{.MemUsage}},{{.CPUPerc}}" \
    $CONTAINER_NAME | while IFS=',' read name mem cpu
    do

        mem_value=$(echo $mem | awk -F'/' '{print $1}')
        mem_mb=$(echo $mem_value | sed 's/MiB//')

        timestamp=$(date +%s)

        echo "$timestamp,$name,$mem_mb,$cpu" >> $OUTPUT_FILE
    done

    sleep 1
done