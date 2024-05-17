#!/usr/bin/env bash

# the first parameter must be YES to proceed
if [ "$1" != "YES" ]; then
  echo "You must pass YES as the first parameter to proceed"
  exit 1
fi

echo "Stopping Kafka broker…"
kafka-server-stop.sh
echo "Cleaning Kafka storage and configs…"
rm -r ~/kafka-data ~/config/kafka.properties