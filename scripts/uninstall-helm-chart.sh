#!/bin/bash

# Define colors for output
INFO_COLOR="\033[1;34m"
ERROR_COLOR="\033[1;31m"
NC="\033[0m" # No color

echo -e "${INFO_COLOR}info | Starting uninstallation of the Helm chart 'crypto-tracker'...${NC}"

NAMESPACE="crypto-tracker"
RELEASE_NAME="crypto-tracker"
PVC_NAME="crypto-tracker-influxdb2"
SPARK_APP_DEPLOYMENT="./charts/crypto-tracker/templates/spark-app-deployment.yaml"

echo -e "${INFO_COLOR}info | Uninstalling Helm release '${RELEASE_NAME}' from namespace '${NAMESPACE}'...${NC}"
if helm uninstall "${RELEASE_NAME}" --namespace "${NAMESPACE}"; then
    echo -e "${INFO_COLOR}info | > Helm release '${RELEASE_NAME}' uninstalled successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to uninstall Helm release '${RELEASE_NAME}'. Proceeding.${NC}"
    # Don't exit here, as we can still proceed
fi

echo -e "${INFO_COLOR}info | Pausing for 5 seconds to allow resources to clean up...${NC}"
sleep 5

# Clean up any remaining Spark pods or services
echo -e "${INFO_COLOR}info | Cleaning up remaining resources in namespace '${NAMESPACE}'...${NC}"
if kubectl delete all --all -n "${NAMESPACE}" --ignore-not-found; then
    echo -e "${INFO_COLOR}info | > Remaining resources cleaned up successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to clean up resources. Proceeding.${NC}"
    # Don't exit here, as we can still proceed
fi

echo -e "${INFO_COLOR}info | Pausing for 5 seconds to allow PVC cleanup..."
sleep 5

echo -e "${INFO_COLOR}info | Deleting PersistentVolumeClaim '${PVC_NAME}' in namespace '${NAMESPACE}'...${NC}"
if kubectl delete pvc "${PVC_NAME}" -n "${NAMESPACE}" --ignore-not-found; then
    echo -e "${INFO_COLOR}info | > PersistentVolumeClaim '${PVC_NAME}' deleted successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to delete PersistentVolumeClaim '${PVC_NAME}'. Proceeding.${NC}"
    # Don't exit here, as we can still proceed
fi

echo -e "${INFO_COLOR}info | Uninstallation process completed successfully.${NC}"