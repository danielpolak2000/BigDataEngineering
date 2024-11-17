#!/bin/bash

# Exit on error
set -e

# Define colors
COLOR='\033[0;35m' # Purple
NC='\033[0m' # No color

# Create namespace for Kafka
echo -e "${COLOR}>>> Creating namespace 'kafka'...${NC}"
kubectl create namespace kafka || echo "Namespace 'kafka' already exists"

# Deploy Strimzi Kafka Operator
echo -e "${COLOR}>>> Deploying Strimzi Kafka Operator...${NC}"
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka

# Wait for Strimzi Operator to be ready
echo -e "${COLOR}>>> Waiting for Strimzi Operator to be ready...${NC}"
kubectl rollout status deployment/strimzi-cluster-operator -n kafka

#echo -e "${COLOR}>>> Waiting for the operator to be ready${NC}"
#kubectl wait pod -l name=strimzi-cluster-operator --for=condition=Ready --timeout=300s -n kafka

# Deploy the Kafka cluster
echo -e "${COLOR}>>> Deploying Kafka cluster...${NC}"
kubectl apply -f charts/crypto-tracker/templates/kafka-cluster.yaml -n kafka

#echo -e "${COLOR}>>> Creating Kafka cluster${NC}"
#kubectl create -f charts/crypto-tracker/templates/kafka-cluster.yaml -n kafka

# Wait for Kafka cluster to be ready
echo -e "${COLOR}>>> Waiting for Kafka cluster to be ready...${NC}"
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=300s -n kafka

echo -e "${COLOR}>>> Kafka cluster is set up and ready${NC}"