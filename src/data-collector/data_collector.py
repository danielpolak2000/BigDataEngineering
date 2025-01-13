from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from kafka import KafkaProducer
import pandas as pd
import json
import os

# InfluxDB Konfiguration
INFLUXDB_URL = os.environ.get(
    "INFLUXDB_URL", "http://crypto-tracker-influxdb2.crypto-tracker.svc:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG", "crypto-tracker-org")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET", "crypto-tracker-bucket")

# Kafka Konfiguration
KAFKA_BROKER = os.environ.get(
    "KAFKA_BROKER", "kafka-cluster-kafka-bootstrap.kafka:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "crypto-data")

# InfluxDB-Client initialisieren
influx_client = InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = influx_client.query_api()

# Kafka-Producer initialisieren
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Funktion zum Prüfen, ob der InfluxDB-Bucket leer ist


def is_bucket_empty():
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -100y)
      |> limit(n: 1)
    '''
    result = query_api.query(org=INFLUXDB_ORG, query=query)
    if result and result[0].records:
        print("Bucket ist **nicht leer**. CSV-Import wird übersprungen.")
        return False  # Es gibt bereits Daten
    else:
        print("Bucket ist **leer**. CSV-Import wird gestartet.")
        return True  # Bucket ist leer

# CSV-Daten importieren


def import_csv():
    csv_file = "/app/bitcoin-historical-data.csv"
    data = pd.read_csv(csv_file)

    # Timestamps konvertieren
    data['Timestamp'] = pd.to_datetime(
        data['Timestamp'], unit='s').dt.tz_localize("UTC")
    data.set_index("Timestamp", inplace=True)

    # CSV-Daten an Kafka senden
    for index, row in data.iterrows():
        record = {
            "timestamp": index.isoformat(),
            "coin": "BTC",
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": row["Volume"]
        }
        producer.send(KAFKA_TOPIC, value=record)
        print(f"Datensatz gesendet: {record}")

# Hauptfunktion


def main():
    if is_bucket_empty():
        import_csv()
    else:
        print("CSV-Import nicht erforderlich. Daten sind bereits vorhanden.")


if __name__ == "__main__":
    main()
