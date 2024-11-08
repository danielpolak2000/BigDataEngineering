#!/bin/bash

COLOR='\033[0;35m' # Purple
NC='\033[0m' # No color

echo -e "${COLOR}>>> Creating Kafka namespace${NC}"
kubectl create namespace kafka

echo -e "${COLOR}>>> Adding Strimzi cluster operator${NC}"
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

echo -e "${COLOR}>>> Waiting for the operator to be ready${NC}"
kubectl wait pod -l name=strimzi-cluster-operator --for=condition=Ready --timeout=300s -n kafka

echo -e "${COLOR}>>> Creating Kafka cluster${NC}"
kubectl create -f charts/crypto-tracker/templates/kafka-cluster.yaml -n kafka

echo -e "${COLOR}>>> Waiting for the Kafka cluster to be ready${NC}"
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=300s -n kafka

echo -e "${COLOR}>>> Creating Kafka topic${NC}"
kubectl apply -f charts/crypto-tracker/templates/kafka-topic.yaml -n kafka

echo -e "${COLOR}>>> Creating Kafka user${NC}"
kubectl apply -f charts/crypto-tracker/templates/kafka-user.yaml -n kafka