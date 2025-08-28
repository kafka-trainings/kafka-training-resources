#!/usr/bin/env bash

# Version of the JDBC connector to install
VERSION="10.7.6"

# Check if the JDBC connector already exists
if [ -d "java/confluentinc-kafka-connect-jdbc-${VERSION}" ]; then
    echo "JDBC connector already exists in java/confluentinc-kafka-connect-jdbc-${VERSION}/"
    echo "Skipping installation..."
    exit 0
fi

# Only execute if the connector doesn't exist
wget "https://d2p6pa21dvn84.cloudfront.net/api/plugins/confluentinc/kafka-connect-jdbc/versions/${VERSION}/confluentinc-kafka-connect-jdbc-${VERSION}.zip"
unzip "confluentinc-kafka-connect-jdbc-${VERSION}.zip"
rm "confluentinc-kafka-connect-jdbc-${VERSION}.zip"
mkdir -p java
mv "confluentinc-kafka-connect-jdbc-${VERSION}/" java/