#!/bin/bash

# Exit on error
set -e

# Define colors
COLOR='\033[0;35m' # Purple
NC='\033[0m' # No color

# Namespace for the application
NAMESPACE="crypto-tracker"

# Create namespace
echo -e "${COLOR}>>> Creating namespace '$NAMESPACE'...${NC}"
kubectl create namespace $NAMESPACE || echo "Namespace '$NAMESPACE' already exists"

# Deploy application using Helm
echo -e "${COLOR}>>> Deploying application using Helm...${NC}"
helm upgrade --install crypto-tracker ./charts/crypto-tracker -n $NAMESPACE

# Wait for all pods to be ready
echo -e "${COLOR}>>> Waiting for application pods to be ready...${NC}"
kubectl wait --for=condition=Ready pods --all --timeout=300s -n $NAMESPACE

echo -e "${COLOR}>>> Application deployed successfully${NC}"
