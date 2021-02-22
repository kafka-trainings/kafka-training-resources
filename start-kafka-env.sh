#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


zookeeper-server-start.sh -daemon "$DIR"/config/zk1.properties
zookeeper-server-start.sh -daemon "$DIR"/config/zk2.properties
zookeeper-server-start.sh -daemon "$DIR"/config/zk3.properties
echo "Zookeeper started. Waiting 5s to finish booting"
sleep 5
echo -n "Testing Connection…"
zookeeper-shell.sh localhost:2181 ls / > /dev/null
echo -e "\tOK"

export KAFKA_OPTS=" -javaagent:$DIR/javaagent.jar=8081:$DIR/config/kafka-javaagent.yaml"
kafka-server-start.sh -daemon "$DIR"/config/kafka1.properties
export KAFKA_OPTS=" -javaagent:$DIR/javaagent.jar=8082:$DIR/config/kafka-javaagent.yaml"
kafka-server-start.sh -daemon "$DIR"/config/kafka2.properties
export KAFKA_OPTS=" -javaagent:$DIR/javaagent.jar=8083:$DIR/config/kafka-javaagent.yaml"
kafka-server-start.sh -daemon "$DIR"/config/kafka3.properties
unset KAFKA_OPTS
echo "Kafka started. Waiting 15s to finish booting"
sleep 15
echo -n "Testing Connection…"
kafka-broker-api-versions.sh --bootstrap-server localhost:9092 > /dev/null
echo -e "\tOK"
echo "Happy Hacking!"