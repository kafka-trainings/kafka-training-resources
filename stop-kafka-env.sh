#!/usr/bin/env bash
set -e

kafka-server-stop.sh /home/user/training/config/kafka1.properties
kafka-server-stop.sh /home/user/training/config/kafka2.properties
kafka-server-stop.sh /home/user/training/config/kafka3.properties
echo "Kafka stopped."