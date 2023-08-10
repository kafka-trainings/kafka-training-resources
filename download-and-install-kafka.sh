#!/usr/bin/env bash
SCALA_VERSION="2.13"
KAFKA_VERSION="3.4.0"
FULL_VERSION="${SCALA_VERSION}-${KAFKA_VERSION}"
wget "https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${FULL_VERSION}.tgz"
tar xfz kafka_${FULL_VERSION}.tgz
rm kafka_${FULL_VERSION}.tgz
mv kafka_${FULL_VERSION} ~/kafka
export PATH=~/kafka/bin:"$PATH"
echo "export PATH=~/kafka/bin:$PATH" >> ~/.bashrc