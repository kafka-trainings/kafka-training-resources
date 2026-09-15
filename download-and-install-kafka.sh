#!/usr/bin/env bash
set -euo pipefail

SCALA_VERSION="2.13"
KAFKA_VERSION="4.3.1"
FULL_VERSION="${SCALA_VERSION}-${KAFKA_VERSION}"
ARCHIVE="kafka_${FULL_VERSION}.tgz"

# dlcdn carries only current releases and is much faster; archive.apache.org
# keeps every version but is slow. Try the mirror, fall back to the archive so
# this keeps working once this version ages out of dlcdn.
wget "https://dlcdn.apache.org/kafka/${KAFKA_VERSION}/${ARCHIVE}" \
  || wget "https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/${ARCHIVE}"

tar xfz "${ARCHIVE}"
rm "${ARCHIVE}"
mv "kafka_${FULL_VERSION}" ~/kafka
export PATH=~/kafka/bin:"$PATH"
echo "export PATH=~/kafka/bin:$PATH" >> ~/.bashrc
