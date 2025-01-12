from kafka import KafkaProducer
import json
import os
import pandas as pd

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

    csv_file = "bitcoin-historical-data.csv"
    data = pd.read_csv(csv_file)

    # Konvertiere Timestamps
    data['Timestamp'] = pd.to_datetime(
        data['Timestamp'], unit='s').dt.tz_localize("UTC")
    data.set_index("Timestamp", inplace=True)

    # Continuously fetch and publish real-time data
    for index, row in data.iterrows():
        fetched_data = {
            "timestamp": data['Timestamp'],
            "coin": "BTC",
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": row["Volume"]
        }
        publish_to_kafka(producer, KAFKA_TOPIC, fetched_data)

if __name__ == "__main__":
    main()
