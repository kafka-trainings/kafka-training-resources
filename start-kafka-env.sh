#!/usr/bin/env bash
set -e

if [[ ! -d "/home/user/training/data/kafka1" ]]; then
  KAFKA_CLUSTER_ID="$(kafka-storage.sh random-uuid)"
  kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c /home/user/training/config/kafka1.properties
  kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c /home/user/training/config/kafka2.properties
  kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c /home/user/training/config/kafka3.properties
fi

export KAFKA_OPTS=" -javaagent:/home/user/training/javaagent.jar=8081:/home/user/training/config/kafka-javaagent.yaml"
kafka-server-start.sh -daemon /home/user/training/config/kafka1.properties
export KAFKA_OPTS=" -javaagent:/home/user/training/javaagent.jar=8082:/home/user/training/config/kafka-javaagent.yaml"
kafka-server-start.sh -daemon /home/user/training/config/kafka2.properties
export KAFKA_OPTS=" -javaagent:/home/user/training/javaagent.jar=8083:/home/user/training/config/kafka-javaagent.yaml"
kafka-server-start.sh -daemon /home/user/training/config/kafka3.properties
unset KAFKA_OPTS
echo "Kafka started. Waiting 15s to finish booting"
sleep 15
echo -n "Testing Connection…"
kafka-broker-api-versions.sh --bootstrap-server localhost:9092 >/dev/null
echo -e "\tOK"
echo "Happy Hacking!"
