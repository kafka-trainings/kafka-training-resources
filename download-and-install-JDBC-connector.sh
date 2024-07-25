#!/usr/bin/env bash
wget "https://d2p6pa21dvn84.cloudfront.net/api/plugins/confluentinc/kafka-connect-jdbc/versions/10.7.6/confluentinc-kafka-connect-jdbc-10.7.6.zip"
unzip confluentinc-kafka-connect-jdbc-10.7.6.zip
rm confluentinc-kafka-connect-jdbc-10.7.6.zip
mkdir java
mv confluentinc-kafka-connect-jdbc-10.7.6/ java/