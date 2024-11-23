#!/bin/bash

set -e

kubectl -n crypto-tracker run kafka-producer -it --image=quay.io/strimzi/kafka:0.44.0-kafka-3.8.0 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server kafka-cluster-kafka-bootstrap:9092 --topic crypto-data