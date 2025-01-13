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

dependencies=(curl tar docker)
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

# Read Spark version dynamically from user input or use a default value
SPARK_VERSION=${1:-3.5.3}
HADOOP_VERSION="hadoop3"

echo -e "${INFO_COLOR}info | Preparing to set up Apache Spark ${SPARK_VERSION} (${HADOOP_VERSION}).${NC}"

# Prepare temporary working directory
echo -e "${INFO_COLOR}info | Preparing temporary working directory...${NC}"
TEMP_DIR="./temp"
mkdir -p ${TEMP_DIR}

# Download the Spark release archive
SPARK_ARCHIVE_URL="https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-${HADOOP_VERSION}.tgz"
SPARK_ARCHIVE_PATH="${TEMP_DIR}/spark-${SPARK_VERSION}-bin-${HADOOP_VERSION}.tgz"

echo -e "${INFO_COLOR}info | Downloading the Spark release archive from ${SPARK_ARCHIVE_URL}...${NC}"
if curl -fSL -o ${SPARK_ARCHIVE_PATH} ${SPARK_ARCHIVE_URL}; then
    echo -e "${INFO_COLOR}info | > Download completed successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to download Spark archive. Please check the version or network connectivity.${NC}"
    exit 1
fi

# Unpack the Spark release archive
echo -e "${INFO_COLOR}info | Unpacking the Spark release archive...${NC}"
if tar -xvzf ${SPARK_ARCHIVE_PATH} -C ${TEMP_DIR}/; then
    echo -e "${INFO_COLOR}info | > Unpack completed successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to unpack Spark archive.${NC}"
    exit 1
fi

# Define JAR dependencies
DEPENDENCIES=(
    "https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.3/spark-sql-kafka-0-10_2.12-3.5.3.jar"
    "https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.3/spark-token-provider-kafka-0-10_2.12-3.5.3.jar"
    "https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.2/kafka-clients-3.5.2.jar"
    "https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar"
)

# Download JAR dependencies
echo -e "${INFO_COLOR}info | Downloading JAR dependencies...${NC}"
SPARK_DIR="${TEMP_DIR}/spark-${SPARK_VERSION}-bin-${HADOOP_VERSION}"
CUSTOM_JARS_DIR="${SPARK_DIR}/jars/custom"
mkdir -p ${CUSTOM_JARS_DIR}

for jar_url in "${DEPENDENCIES[@]}"; do
    jar_name=$(basename "${jar_url}")
    echo -e "${INFO_COLOR}info | Downloading ${jar_name}...${NC}"
    if curl -fSL -o "${CUSTOM_JARS_DIR}/${jar_name}" "${jar_url}"; then
        echo -e "${INFO_COLOR}info | > ${jar_name} downloaded successfully.${NC}"
    else
        echo -e "${ERROR_COLOR}error | > Failed to download ${jar_name}. Please check the URL or network connectivity.${NC}"
        exit 1
    fi
done
echo -e "${INFO_COLOR}info | All JAR dependencies downloaded successfully.${NC}"

# Copy the Spark app sources into the extracted Spark directory
echo -e "${INFO_COLOR}info | Copying the Spark app sources into the Spark archive directory...${NC}"
APP_DIR="./src/spark-app"
if cp -r ${APP_DIR}/* ${SPARK_DIR}/; then
    echo -e "${INFO_COLOR}info | > Spark app sources copied successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to copy Spark app sources.${NC}"
    exit 1
fi

# Set Docker environment for building images inside Minikube
echo -e "${INFO_COLOR}info | Setting up Docker environment for Minikube...${NC}"
if eval "$(minikube -p minikube docker-env)"; then
    echo -e "${INFO_COLOR}info | > Docker environment set for Minikube.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to set Docker environment for Minikube.${NC}"
    exit 1
fi

# Build Spark and PySpark Docker images using the copied Dockerfile
echo -e "${INFO_COLOR}info | Building Spark and PySpark Docker images using the copied Dockerfile...${NC}"
if ${SPARK_DIR}/bin/docker-image-tool.sh \
    -r docker.io/crypto-tracker \
    -t latest \
    -m \
    -p ${SPARK_DIR}/Dockerfile \
    build; then
    echo -e "${INFO_COLOR}info | > Docker images built successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to build Docker images. Please check the logs for details.${NC}"
    exit 1
fi

# Cleanup temporary working directory
echo -e "${INFO_COLOR}info | Cleaning up temporary working directory...${NC}"
if rm -rf ${TEMP_DIR}; then
    echo -e "${INFO_COLOR}info | > Temporary working directory cleaned up successfully.${NC}"
else
    echo -e "${ERROR_COLOR}error | > Failed to clean up temporary working directory.${NC}"
    exit 1
fi

echo -e "${INFO_COLOR}info | Apache Spark setup and Docker image build completed successfully.${NC}"