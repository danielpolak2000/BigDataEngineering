#!/bin/bash

# Define colors for output
INFO_COLOR="\033[1;34m"
ERROR_COLOR="\033[1;31m"
NC="\033[0m" # No color

# Script to install Helm chart
echo -e "${INFO_COLOR}info | Starting Helm chart installation for crypto-tracker...${NC}"

NAMESPACE="crypto-tracker"
CHART_PATH="./charts/crypto-tracker/"
RELEASE_NAME="crypto-tracker"

echo -e "${INFO_COLOR}info | Creating namespace '${NAMESPACE}' if it doesn't already exist...${NC}"
if kubectl get namespace "${NAMESPACE}" >/dev/null 2>&1; then
    echo -e "${INFO_COLOR}info | > Namespace '${NAMESPACE}' already exists.${NC}"
else
    if kubectl create namespace "${NAMESPACE}"; then
        echo -e "${INFO_COLOR}info | > Namespace '${NAMESPACE}' created successfully.${NC}"
    else
        echo -e "${ERROR_COLOR}error | > Failed to create namespace '${NAMESPACE}'.${NC}"
        exit 1
    fi
fi

echo -e "${INFO_COLOR}info | Updating Helm dependencies for chart '${CHART_PATH}'...${NC}"
if helm dependency update "${CHART_PATH}"; then
    echo -e "${INFO_COLOR}info | > Helm dependencies updated successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to update Helm dependencies for chart '${CHART_PATH}'.${NC}"
    exit 1
fi

echo -e "${INFO_COLOR}info | Installing Helm chart '${RELEASE_NAME}' from '${CHART_PATH}'...${NC}"
if helm install "${RELEASE_NAME}" "${CHART_PATH}" --namespace "${NAMESPACE}" --create-namespace; then
    echo -e "${INFO_COLOR}info | > Helm chart '${RELEASE_NAME}' installed successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to install Helm chart '${RELEASE_NAME}'. Check Helm logs for details.${NC}"
    exit 1
fi

echo -e "${INFO_COLOR}info | Helm chart installation completed.${NC}"