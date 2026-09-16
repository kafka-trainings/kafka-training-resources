#!/usr/bin/env bash
# Runs Kafka Connect as a systemd user service, so no root is needed.
set -euo pipefail

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
UNIT_DIR="$HOME/.config/systemd/user"
mkdir -p "$UNIT_DIR"

echo "Writing the Kafka Connect service file"
cat > "$UNIT_DIR/kafka-connect.service" <<UNIT
[Unit]
Description=Kafka Connect

[Service]
Type=simple
ExecStart=$HOME/kafka/bin/connect-distributed.sh $HOME/training/config/worker.properties
Restart=on-failure
WorkingDirectory=$HOME

[Install]
WantedBy=default.target
UNIT

echo "Starting Kafka Connect…"
systemctl --user daemon-reload
systemctl --user enable --now kafka-connect

echo "Waiting for the REST API on port 8090"
for _ in $(seq 60); do
  if curl -sf http://localhost:8090/ > /dev/null; then
    curl -s http://localhost:8090/ | jq
    echo "Happy Hacking!"
    exit 0
  fi
  sleep 2
done
echo "Kafka Connect did not come up. Check: journalctl --user -u kafka-connect" >&2
exit 1
