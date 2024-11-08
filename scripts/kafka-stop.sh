#!/bin/bash

COLOR='\033[0;35m' # Purple
NC='\033[0m' # No color

echo -e "${COLOR}>>> Deleting Kafka cluster${NC}"
kubectl -n kafka delete $(kubectl get strimzi -o name -n kafka)

#echo -e "${COLOR}>>> Deleting Persistent Volume Claim${NC}"
#kubectl delete pvc -l strimzi.io/name=kafka-cluster-kafka -n kafka

echo -e "${COLOR}>>> Deleting Strimzi cluster operator${NC}"
kubectl -n kafka delete -f 'https://strimzi.io/install/latest?namespace=kafka'

echo -e "${COLOR}>>> Deleting Kafka namespace${NC}"
kubectl delete namespace kafka