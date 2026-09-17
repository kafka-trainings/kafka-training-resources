#!/usr/bin/env bash
# Installs the Debezium PostgreSQL connector into the Connect plugin path.
# Start or restart Kafka Connect afterwards so it picks the plugin up.
set -euo pipefail

VERSION="3.5.0.Final"
TARGET="$HOME/training/java/debezium-connector-postgres"
MARKER="$TARGET/.version"

if [ -f "$MARKER" ] && [ "$(cat "$MARKER")" = "$VERSION" ]; then
    echo "Debezium $VERSION is already installed in $TARGET"
    exit 0
fi

ARCHIVE="/tmp/debezium-connector-postgres-${VERSION}-plugin.tar.gz"
wget -O "$ARCHIVE" "https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/${VERSION}/debezium-connector-postgres-${VERSION}-plugin.tar.gz"
# Two versions in one plugin directory give undefined class loading.
rm -rf "$TARGET"
mkdir -p "$(dirname "$TARGET")"
tar xfz "$ARCHIVE" -C "$(dirname "$TARGET")"
rm "$ARCHIVE"
echo "$VERSION" > "$MARKER"
echo "Debezium $VERSION installed in $TARGET"
