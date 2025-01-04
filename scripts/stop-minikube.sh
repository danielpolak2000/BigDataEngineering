#!/bin/bash

# Define colors
INFO_COLOR="\033[1;34m"
ERROR_COLOR="\033[1;31m"
NC="\033[0m" # No color

# Stop Minikube
echo -e "${INFO_COLOR}info | Stopping Minikube...${NC}"
if minikube stop; then
    echo -e "${INFO_COLOR}info | > Minikube stopped successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to stop Minikube. Please check your setup.${NC}"
    exit 1
fi