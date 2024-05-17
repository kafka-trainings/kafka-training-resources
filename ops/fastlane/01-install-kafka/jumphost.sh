#!/usr/bin/env bash

# check
echo "Updating known hosts…"
# Do the keyscan only if the key is not already in the known_hosts file
if ! grep -q "$IP.1" ~/.ssh/known_hosts; then
  ssh-keyscan -H "$IP".1 >> ~/.ssh/known_hosts
fi
if ! grep -q "$IP.2" ~/.ssh/known_hosts; then
  ssh-keyscan -H "$IP".2 >> ~/.ssh/known_hosts
fi
if ! grep -q "$IP.3" ~/.ssh/known_hosts; then
  ssh-keyscan -H "$IP".3 >> ~/.ssh/known_hosts
fi

echo "Updating git repos on the brokers…"
ssh "$IP".1 "cd /home/user/training/ && git pull"
ssh "$IP".2 "cd /home/user/training/ && git pull"
ssh "$IP".3 "cd /home/user/training/ && git pull"

# Check if cluster_id is already defined in file ~/CLUSTER_ID
# If not generate it
if [ -f ~/CLUSTER_ID ]; then
  echo "Cluster ID already exists…"
  CLUSTER_ID=$(cat ~/CLUSTER_ID)
else
echo "Generating cluster ID…"
  CLUSTER_ID=$(kafka-storage.sh random-uuid)
  echo $CLUSTER_ID > ~/CLUSTER_ID
fi
echo "Cluster ID: $CLUSTER_ID"

echo "Configuring Kafka on the brokers…"
ssh "$IP".1 "/home/user/training/ops/fastlane/01-install-kafka/broker.sh $CLUSTER_ID"
ssh "$IP".2 "/home/user/training/ops/fastlane/01-install-kafka/broker.sh $CLUSTER_ID"
ssh "$IP".3 "/home/user/training/ops/fastlane/01-install-kafka/broker.sh $CLUSTER_ID"

echo "Kafka started. Waiting 15s to finish booting"
sleep 20
echo -n "Testing Connection…"
kafka-broker-api-versions.sh --bootstrap-server $IP.1:9092 >/dev/null
echo -e "\tOK"
echo "Happy Hacking!"