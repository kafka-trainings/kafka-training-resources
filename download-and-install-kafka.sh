#!/usr/bin/env bash
set -euo pipefail

SCALA_VERSION="2.13"
KAFKA_VERSION="4.3.1"
FULL_VERSION="${SCALA_VERSION}-${KAFKA_VERSION}"
ARCHIVE="kafka_${FULL_VERSION}.tgz"

# Same guard as download-and-install-JDBC-connector.sh. Without it a second run
# would not rename but move the new directory *into* the existing ~/kafka.
if [ -d "$HOME/kafka" ]; then
    echo "Kafka is already installed in ~/kafka"
    echo "Remove it first if you want to install $KAFKA_VERSION."
    exit 0
fi

cd "$HOME"

# dlcdn carries only current releases and is much faster; archive.apache.org
# keeps every version but is slow. Try the mirror, fall back to the archive so
# this keeps working once this version ages out of dlcdn. -O, so a leftover
# file from an aborted run is overwritten instead of being unpacked.
wget -O "${ARCHIVE}" "https://dlcdn.apache.org/kafka/${KAFKA_VERSION}/${ARCHIVE}" \
  || wget -O "${ARCHIVE}" "https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/${ARCHIVE}"

tar xfz "${ARCHIVE}"
rm "${ARCHIVE}"
mv "kafka_${FULL_VERSION}" "$HOME/kafka"
export PATH="$HOME/kafka/bin:$PATH"
echo "export PATH=$HOME/kafka/bin:\$PATH" >> ~/.bashrc
