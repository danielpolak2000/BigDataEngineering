#!/bin/bash

# Exit on error
set -e

# Define colors
COLOR='\033[0;35m' # Purple
NC='\033[0m' # No color

# Start Minikube cluster
echo -e "${COLOR}>>> Starting Minikube...${NC}"
minikube start --cpus 6 --memory 7000 --driver=docker

# Enable necessary add-ons
echo -e "${COLOR}>>> Enabling Minikube addons...${NC}"
minikube addons enable ingress
minikube addons enable metrics-server

# Set Docker environment for building images inside Minikube
eval $(minikube -p minikube docker-env)

echo -e "${COLOR}>>> Minikube is up and running${NC}"
echo -e "${COLOR}>>> Use 'kubectl get nodes' to verify the cluster${NC}"