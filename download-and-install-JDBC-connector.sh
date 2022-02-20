#!/usr/bin/env bash
wget "https://d1i4a15mxbxib1.cloudfront.net/api/plugins/confluentinc/kafka-connect-jdbc/versions/10.0.1/confluentinc-kafka-connect-jdbc-10.0.1.zip"
unzip confluentinc-kafka-connect-jdbc-10.0.1.zip
rm confluentinc-kafka-connect-jdbc-10.0.1.zip
mkdir java
mv confluentinc-kafka-connect-jdbc-10.0.1/ java/