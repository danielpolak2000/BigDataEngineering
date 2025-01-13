#!/bin/bash

# Define colors for output
INFO_COLOR="\033[1;34m"
ERROR_COLOR="\033[1;31m"
NC="\033[0m" # No color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required dependencies
echo -e "${INFO_COLOR}info | Checking dependencies...${NC}"

dependencies=(docker)
for dep in "${dependencies[@]}"; do
    if ! command_exists $dep; then
        echo -e "${ERROR_COLOR}error | > $dep is not installed or not in PATH. Please install it before running this script.${NC}"
        exit 1
    fi
done
echo -e "${INFO_COLOR}info | > All required dependencies are installed.${NC}"

# Ensure Minikube cluster is running
echo -e "${INFO_COLOR}info | Ensuring Minikube cluster is up...${NC}"
if ! minikube status >/dev/null 2>&1; then
    echo -e "${ERROR_COLOR}error | > Minikube cluster is not running. Start it before executing this script.${NC}"
    exit 1
fi
echo -e "${INFO_COLOR}info | > Minikube cluster is up and running.${NC}"

# Set Docker environment for building images inside Minikube
echo -e "${INFO_COLOR}info | Setting up Docker environment for Minikube...${NC}"
if eval "$(minikube -p minikube docker-env)"; then
    echo -e "${INFO_COLOR}info | > Docker environment set for Minikube.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to set Docker environment for Minikube.${NC}"
    exit 1
fi

echo -e "${INFO_COLOR}info | Building application images...${NC}"
cd ./src/data-collector
if ! docker build -t crypto-tracker/data-collector:latest -f Dockerfile .; then
    echo -e "${ERROR_COLOR}error | > Failed to build data-collector image.${NC}"
    exit 1
fi

cd ../dashboard
if ! docker build -t crypto-tracker/dashboard:latest -f Dockerfile .; then
    echo -e "${ERROR_COLOR}error | > Failed to build dashboard image.${NC}"
    exit 1
fi

echo -e "${INFO_COLOR}info | Application images have been built sucessfully.${NC}"