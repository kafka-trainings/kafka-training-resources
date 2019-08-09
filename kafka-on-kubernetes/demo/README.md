# Demo: Kafka on Kubernetes

## Init Google Cloud Platform

You can use any other Kubernetes you have access to.

* Create account on cloud.google.com
* Login using `gcloud`

Create Kubernetes Cluster

```sh
gcloud beta container clusters create \
    --zone "europe-west3-a"\
    --machine-type "n1-standard-2" \
    --num-nodes "3" \
    "kafka-on-kubernetes"
```

Connect to cluster

```sh
gcloud container clusters get-credentials \
  kafka-on-kubernetes \
  --zone europe-west3-a
```

Grant Cluster Admin permissions to your user

```sh
kubectl create clusterrolebinding cluster-admin-binding \
--clusterrole cluster-admin --user [YOUR-USER]
```

## Install Helm

```sh
kubectl apply ./tiller-rbac-config.yaml
helm init --service-account tiller
```

## Install Strimzi

```sh
kubectl create ns kafka
kubens kafka
helm install -n kafka strimzi/strimzi-kafka-operator
```

Wait until the `strimzi-cluster-operator` is up and running.

## Install Kafka

```sh
kubectl apply -f kafka.yaml
```

## Launch Toolbox pod

```sh
kubectl apply -f kafka-toolbox.yaml
kubectl exec -it kafka-toolbox /bin/bash
```

```sh
kubectl exec kafka-toolbox -- kafka-topics --list
```

→ empty

## Create topic

```sh
kubectl apply -f topic-1.yaml
```


```sh
kubectl exec kafka-toolbox -- kafka-topics --list
```

→ Not empty

## Producing and Consuming

### Produce something to topic

```sh
kubectl exec -it kafka-toolbox -- kafka-console-producer --topic topic1
```

### Consume from the same topic

```sh
kubectl exec kafka-toolbox -- kafka-console-consumer --topic topic1
```

### Consume with partitions

Open 4 terminal windows:

```sh
kubectl exec kafka-toolbox -- kafka-console-consumer --topic topic1 --partition 0
```

```sh
kubectl exec kafka-toolbox -- kafka-console-consumer --topic topic1 --partition 1
```

```sh
kubectl exec kafka-toolbox -- kafka-console-consumer --topic topic1 --partition 2
```

Produce more stuff:


```sh
kubectl exec -it kafka-toolbox -- kafka-console-producer --topic topic1
```

### Partitioning by key

If key is given, Kafka Console Producer uses the default partitioner.

```sh
kubectl exec -it kafka-toolbox -- kafka-console-producer --topic topic1 --property "parse.key=true" --property "key.separator=:"
```

## Two-way sync of Topics

```sh
kubectl exec kafka-toolbox -- \
  kafka-topics --create --topic test2 \
  --partitions 3 --replication-factor 1
```

```sh
kubectl get kafkatopics
```
