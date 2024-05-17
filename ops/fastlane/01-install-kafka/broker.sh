#!/usr/bin/env bash

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

cat <<EOF >> ~/config/kafka.properties
log.dirs=/home/user/kafka-data
process.roles=broker,controller
controller.listener.names=CONTROLLER
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
controller.quorum.voters=1@$IP.1:9192,2@$IP.2:9192,3@$IP.3:9192

broker.id=$ID
listeners=PLAINTEXT://$IP.$ID:9092,CONTROLLER://$IP.$ID:9192
EOF

/home/user/kafka/bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c ~/config/kafka.properties
/home/user/kafka/bin/kafka-server-start.sh -daemon ~/config/kafka.properties