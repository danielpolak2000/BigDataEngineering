from kafka import KafkaProducer
import time
import json
import os
import random

# Kafka configuration
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka-cluster-kafka-bootstrap.kafka:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "crypto-data")

# Publish data to Kafka
def publish_to_kafka(producer: KafkaProducer, topic: str, data):
    for record in data:
        try:
            producer.send(topic, value=record)
            print(f"Published record to {topic}: {record}")
        except Exception as e:
            print(f"Error publishing to Kafka: {e}")

# Main function
def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    # Continuously fetch and publish real-time data
    while True:
        price = 40000 + random.uniform(-500, 500)  # Add random variation to the price
        fetched_data = {
            "name": "Bitcoin",
            "symbol": "BTC",
            "timestamp": time.time(),
            "price": price
        }
        publish_to_kafka(producer, KAFKA_TOPIC, fetched_data)
        time.sleep(10)  # Wait before fetching data again

if __name__ == "__main__":
    main()
