#!/usr/bin/env bash
set -e

# Query the user to confirm the deletion
echo "Are you sure you want to delete all Kafka data and configurations? (YES/NO)"
read CONFIRM
if [ "$CONFIRM" != "YES" ]; then
  echo "Exiting without deleting data"
  exit 1
fi

echo "Cleaning up Kafka 1"
ssh "$IP".1 "/home/user/training/ops/fastlane/01-install-kafka/broker-cleanall.sh YES"
echo "Cleaning up Kafka 2"
ssh "$IP".2 "/home/user/training/ops/fastlane/01-install-kafka/broker-cleanall.sh YES"
echo "Cleaning up Kafka 3"
ssh "$IP".3 "/home/user/training/ops/fastlane/01-install-kafka/broker-cleanall.sh YES"