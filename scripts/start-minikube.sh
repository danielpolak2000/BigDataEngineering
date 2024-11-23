#!/bin/bash

# Define colors for output
INFO_COLOR="\033[1;34m"
ERROR_COLOR="\033[1;31m"
NC="\033[0m" # No color

# Start Minikube cluster
echo -e "${INFO_COLOR}info | Starting Minikube with 6 CPUs and 7GB of memory using Docker driver...${NC}"
if minikube start --cpus=6 --memory=7000 --driver=docker; then
    echo -e "${INFO_COLOR}info | > Minikube started successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to start Minikube.${NC}"
    exit 1
fi

# Enable necessary add-ons
echo -e "${INFO_COLOR}info | Enabling Minikube addons..."
for addon in ingress metrics-server; do
    if minikube addons enable "$addon"; then
        echo -e "${INFO_COLOR}info | > Enabled addon: $addon.${NC}"
    else
        echo -e "${ERROR_COLOR}error | > Failed to enable addon: $addon.${NC}"
        exit 1
    fi
done

# Set Docker environment for building images inside Minikube
echo -e "${INFO_COLOR}info | Setting up Docker environment for Minikube...${NC}"
if eval "$(minikube -p minikube docker-env)"; then
    echo -e "${INFO_COLOR}info | > Docker environment set for Minikube.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to set Docker environment for Minikube.${NC}"
    exit 1
fi

# Final messages
echo -e "${INFO_COLOR}info | Minikube is up and running!${NC}"
echo -e "${INFO_COLOR}info | Use 'kubectl get nodes' to verify the cluster.${NC}"