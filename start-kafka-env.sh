#!/usr/bin/env bash
set -e

TRAINING="$HOME/training"

if [[ ! -d "$TRAINING/data/kafka1" ]]; then
  KAFKA_CLUSTER_ID="$(kafka-storage.sh random-uuid)"
  kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c $TRAINING/config/kafka1.properties
  kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c $TRAINING/config/kafka2.properties
  kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c $TRAINING/config/kafka3.properties
fi

export KAFKA_OPTS=" -javaagent:$TRAINING/javaagent.jar=9101:$TRAINING/config/kafka-javaagent.yaml"
kafka-server-start.sh -daemon $TRAINING/config/kafka1.properties
export KAFKA_OPTS=" -javaagent:$TRAINING/javaagent.jar=9102:$TRAINING/config/kafka-javaagent.yaml"
kafka-server-start.sh -daemon $TRAINING/config/kafka2.properties
export KAFKA_OPTS=" -javaagent:$TRAINING/javaagent.jar=9103:$TRAINING/config/kafka-javaagent.yaml"
kafka-server-start.sh -daemon $TRAINING/config/kafka3.properties
unset KAFKA_OPTS
echo "Kafka started. Waiting 15s to finish booting"
sleep 15
echo -n "Testing Connection…"
kafka-broker-api-versions.sh --bootstrap-server localhost:9092 >/dev/null
echo -e "\tOK"
echo "Happy Hacking!"
