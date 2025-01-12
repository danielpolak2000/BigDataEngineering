import pandas as pd
import yfinance as yf
from kafka import KafkaProducer
import json
from datetime import datetime, timedelta, timezone
import os

# Kafka-Konfiguration
KAFKA_BROKER = os.environ.get(
    "KAFKA_BROKER", "kafka-cluster-kafka-bootstrap:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "crypto-data")

# Kafka Producer initialisieren
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Symbol und Zeitauflösung für Yahoo Finance
symbol = "Bitcoin"
interval = "1m"  # 1-Minuten-Auflösung

# Funktion zum Abrufen des neuesten Timestamps


def get_latest_timestamp():
    # Placeholder: Hier sollte der letzte Timestamp aus InfluxDB oder Kafka kommen
    # Für jetzt setzen wir einen Standardzeitpunkt:
    print("⚠️ Keine Datenquelle für Timestamp. Starte mit Daten von vor 1 Tag.")
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
        data = yf.download(symbol, start=start_date,
                           end=next_end_date, interval=interval)

        if data.empty:
            print(
                f"⚠️ Keine Daten von {start_date} bis {next_end_date} erhalten.")
        else:
            # Daten in Kafka senden
            for index, row in data.iterrows():
                record = {
                    "timestamp": index.isoformat(),
                    "symbol": symbol,
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"],
                    "source": "yahoo_finance"
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
