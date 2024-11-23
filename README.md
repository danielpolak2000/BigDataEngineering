## Crypto Tracker

#### Deployment

Use the following scripts to deploy the application in your Kubernetes cluster.

Ensure, that you are in the root directory of the project and run the commands from there.

1. Start the Kubernetes cluster with Minikube using the following script: `scripts/start-minikube.sh`
2. Build the required Docker images for the Spark application with this script: `scripts/build-spark-image.sh`
3. Install the Helm Chart to deploy the application components with this script: `scripts/install-helm-chart.sh`