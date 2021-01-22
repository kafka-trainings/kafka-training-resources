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
kafka-server-start.sh -daemon "$DIR"/config/kafka1.properties
kafka-server-start.sh -daemon "$DIR"/config/kafka2.properties
kafka-server-start.sh -daemon "$DIR"/config/kafka3.properties
echo "Kafka started. Waiting 15s to finish booting"
sleep 15
echo -n "Testing Connection…"
kafka-broker-api-versions.sh --bootstrap-server localhost:9092 > /dev/null
echo -e "\tOK"
echo "Happy Hacking!"