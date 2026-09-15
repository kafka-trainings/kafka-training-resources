#!/usr/bin/env bash
set -euo pipefail

VERSION="1.0.0.CR1"
RELEASE="kcctl-${VERSION}-linux-x86_64"
TARGET="$HOME/kafka/bin"

# download-and-install-kafka.sh only appends this to .bashrc, so it is not in
# PATH yet when both scripts run in the same session.
export PATH="$TARGET:$PATH"

mkdir -p "$TARGET"

cd /tmp
wget "https://github.com/kcctl/kcctl/releases/download/v${VERSION}/${RELEASE}.tar.gz"
tar xfz "${RELEASE}.tar.gz"
cp "${RELEASE}/bin/kcctl" "$TARGET"
rm -rf "${RELEASE}" "${RELEASE}.tar.gz"

kcctl config set-context local --cluster http://localhost:8090
