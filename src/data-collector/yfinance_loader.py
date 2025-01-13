import pandas as pd
import yfinance as yf
from kafka import KafkaProducer
import json
from datetime import datetime, timedelta, timezone
from influxdb_client import InfluxDBClient
import os

# Kafka-Konfiguration
KAFKA_BROKER = os.environ.get(
    "KAFKA_BROKER", "kafka-cluster-kafka-bootstrap.crypto-tracker.svc:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "crypto-data")

# Kafka Producer initialisieren
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# InfluxDB Konfiguration
INFLUXDB_URL = os.environ.get(
    "INFLUXDB_URL", "http://crypto-tracker-influxdb2.crypto-tracker.svc:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG", "crypto-tracker-org")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET", "crypto-tracker-bucket")

# InfluxDB-Client initialisieren
influx_client = InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = influx_client.query_api()

interval = "1m"  # 1-Minuten-Auflösung

# Funktion zum Abrufen des neuesten Timestamps


def get_latest_timestamp():
    try:
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
          |> range(start: -30d)
          |> filter(fn: (r) => r._measurement == "market_data")
          |> filter(fn: (r) => r._field == "close")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: 1)
        '''
        tables = query_api.query(query)
        if tables and tables[0].records:
            latest_timestamp = tables[0].records[0].get_time()
            print(f"🟢 Neuester Datenpunkt in InfluxDB: {latest_timestamp}")
            return latest_timestamp
        else:
            print("⚠️ Keine Daten in InfluxDB gefunden. Starte mit Daten von vor 1 Tag.")
            return datetime.now(timezone.utc) - timedelta(days=1)
    except Exception as e:
        print(f"❌ Fehler beim Abrufen des Timestamps: {e}")
        return datetime.now(timezone.utc) - timedelta(days=1)


# Zeitintervalle berechnen
latest_timestamp = get_latest_timestamp()
start_date = latest_timestamp + timedelta(minutes=1)
end_date = datetime.now(timezone.utc)  # Aktuelle Zeit
delta = timedelta(days=7)  # Maximal 7 Tage pro Abruf

# Daten stückweise laden und an Kafka senden
while start_date < end_date:
    next_end_date = min(start_date + delta, end_date)
    print(f"📡 Lade Daten von {start_date} bis {next_end_date}")

    try:
        # Daten von Yahoo Finance laden
        data = yf.download("BTC-USD", start=start_date,
                           end=next_end_date, interval=interval)

        if data.empty:
            print(
                f"⚠️ Keine Daten von {start_date} bis {next_end_date} erhalten.")
        else:
            # Daten in Kafka senden
            for index, row in data.iterrows():
                record = {
                    "timestamp": index.isoformat(),
                    "coin": "BTC-USD",
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"]
                }
                try:
                    producer.send(KAFKA_TOPIC, value=record)
                    print(f"✅ Gesendet: {record}")
                except Exception as e:
                    print(f"❌ Fehler beim Senden an Kafka: {e}")

    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Daten: {e}")

    # Intervall fortsetzen
    start_date = next_end_date

print("✅ Yahoo Finance Datenimport abgeschlossen.")
producer.close()
