#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

zookeeper-server-stop.sh "$DIR"/config/zk1.properties
zookeeper-server-stop.sh "$DIR"/config/zk2.properties
zookeeper-server-stop.sh "$DIR"/config/zk3.properties
echo "Zookeeper stopped."
kafka-server-stop.sh "$DIR"/config/kafka1.properties
kafka-server-stop.sh "$DIR"/config/kafka2.properties
kafka-server-stop.sh "$DIR"/config/kafka3.properties
echo "Kafka stopped."