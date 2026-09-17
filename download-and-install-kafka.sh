#!/usr/bin/env bash
set -euo pipefail

SCALA_VERSION="2.13"
KAFKA_VERSION="4.3.1"
FULL_VERSION="${SCALA_VERSION}-${KAFKA_VERSION}"
ARCHIVE="kafka_${FULL_VERSION}.tgz"

# Connect scans every jar in plugin.path on its own, which takes over a minute
# for all of ~/kafka/libs. The only plugin in there is the FileStream
# connector, so worker.properties points at this directory instead.
link_connect_plugins() {
    mkdir -p "$HOME/kafka/plugins"
    ln -sf "$HOME/kafka/libs/connect-file-${KAFKA_VERSION}.jar" "$HOME/kafka/plugins/"
}

# Same guard as download-and-install-JDBC-connector.sh. Without it a second run
# would not rename but move the new directory *into* the existing ~/kafka.
if [ -d "$HOME/kafka" ]; then
    echo "Kafka is already installed in ~/kafka"
    echo "Remove it first if you want to install $KAFKA_VERSION."
    link_connect_plugins
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
link_connect_plugins
export PATH="$HOME/kafka/bin:$PATH"

# Only once, so removing ~/kafka and running again does not stack up lines.
BASHRC_LINE="export PATH=$HOME/kafka/bin:\$PATH"
grep -qxF "$BASHRC_LINE" ~/.bashrc 2>/dev/null || echo "$BASHRC_LINE" >> ~/.bashrc
