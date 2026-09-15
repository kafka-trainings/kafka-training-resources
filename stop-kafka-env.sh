#!/usr/bin/env bash
set -e

# --node-id is what actually selects a broker. Passing the config file does
# nothing: kafka-server-stop.sh ignores it and stops every broker on the host.
kafka-server-stop.sh --node-id=1
kafka-server-stop.sh --node-id=2
kafka-server-stop.sh --node-id=3
echo "Kafka stopped."
