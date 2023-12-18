#!/usr/bin/env bash
set -e

cd /tmp
wget https://github.com/kcctl/kcctl/releases/download/v1.0.0.CR1/kcctl-1.0.0.CR1-linux-x86_64.tar.gz
tar xfz kcctl-1.0.0.CR1-linux-x86_64.tar.gz
cp kcctl-1.0.0.CR1-linux-x86_64/bin/kcctl ~/kafka/bin
kcctl config set-context local --cluster http://localhost:8090