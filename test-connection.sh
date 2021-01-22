#!/usr/bin/env bash
set -e
echo "Testing Zookeeper…"
echo -n "ZK 1"
zookeeper-shell.sh localhost:2181 ls / > /dev/null
echo -e "\tOK"
echo -n "ZK 2"
zookeeper-shell.sh localhost:2182 ls / > /dev/null
echo -e "\tOK"
echo -n "ZK 3"
zookeeper-shell.sh localhost:2183 ls / > /dev/null
echo -e "\tOK"
echo "Testing Kafka…"
echo -n "Kafka 1"
kafka-broker-api-versions.sh --bootstrap-server localhost:9092 > /dev/null
echo -e "\tOK"
echo -n "Kafka 2"
kafka-broker-api-versions.sh --bootstrap-server localhost:9093 > /dev/null
echo -e "\tOK"
echo -n "Kafka 3"
kafka-broker-api-versions.sh --bootstrap-server localhost:9094 > /dev/null
echo -e "\tOK"
echo "Happy Hacking!"