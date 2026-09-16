#!/usr/bin/env bash
# Stops the three local brokers. Brokers that are already down are skipped.
# A node that has lost its controller quorum never finishes a clean shutdown,
# so whatever is still running after 30 seconds is killed.

for id in 1 2 3; do
  kafka-server-stop.sh --node-id="$id" > /dev/null 2>&1 || true
done

for _ in $(seq 30); do
  if ! pgrep -f 'kafka\.Kafka' > /dev/null; then
    echo "Kafka stopped."
    exit 0
  fi
  sleep 1
done

echo "Some brokers did not shut down cleanly, killing them."
pkill -9 -f 'kafka\.Kafka'
echo "Kafka stopped."
