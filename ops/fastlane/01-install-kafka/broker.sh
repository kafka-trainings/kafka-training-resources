#!/usr/bin/env bash
set -e

# Cluster ID is the first argument
KAFKA_CLUSTER_ID=$1
# If the cluster ID is not provided return an error
if [ -z "$KAFKA_CLUSTER_ID" ]; then
  echo "Cluster ID is required"
  exit 1
fi

mkdir -p ~/kafka-data ~/config
cd ~/config
cp ~/kafka/config/server.properties ~/config/kafka.properties
ID=$(hostname | grep -oE '[0-9]+$')
IP=$(hostname -I | grep -o "10\.[0-9]*\.[0-9]*")

lines=(
"log.dirs=/home/user/kafka-data"
"process.roles=broker,controller"
"controller.listener.names=CONTROLLER"
"listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT"
"controller.quorum.voters=1@${IP}.1:9192,2@${IP}.2:9192,3@${IP}.3:9192"
"broker.id=${ID}"
"listeners=PLAINTEXT://${IP}.${ID}:9092,CONTROLLER://${IP}.${ID}:9192"
)
config_file=~/config/kafka.properties

add_line_if_not_exists() {
    local line="$1"
    if ! grep -Fxq "$line" "$config_file"; then
        echo "$line" >> "$config_file"
    fi
}

# Add each line to the configuration file if it doesn't already exist
for line in "${lines[@]}"; do
    add_line_if_not_exists "$line"
done


# Check if it is already formatted
if [ -f ~/kafka-data/meta.properties ]; then
  echo "Kafka storage already formatted…"
else
  echo "Formatting Kafka storage…"
  ~/kafka/bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c ~/config/kafka.properties
fi
echo "Starting Kafka broker…"
~/kafka/bin/kafka-server-start.sh -daemon ~/config/kafka.properties