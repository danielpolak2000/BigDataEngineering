import pandas as pd
import yfinance as yf
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta, timezone
import os

# InfluxDB-Konfigurationen
# token = os.getenv("INFLUXDB_TOKEN")
# org = os.getenv("INFLUXDB_ORG")
# bucket = os.getenv("INFLUXDB_BUCKET")
# url = os.getenv("INFLUXDB_URL")

token = "rFU9szMFNSBCx1Z1jH3QIEBMLx-3L5XdOhDD-VVuRghCGMoRkgeHWnoBBTkt719rThPJg0B-OGHpyU9Rfjp8Fw=="
org = "marketdata-org"
bucket = "marketdata"
url = "http://localhost:8086"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

# Symbol und Zeitauflösung für Yahoo Finance
symbol = "BTC-USD"
interval = "1m"  # 1-Minuten-Auflösung

# Abrufen des neuesten Timestamps


def get_latest_timestamp():
    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "market_data")
      |> filter(fn: (r) => r._field == "close")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 1)
    '''
    tables = query_api.query(query)
    if tables and tables[0].records:
        latest_timestamp = tables[0].records[0].get_time()
        print(f"Neuester Datenpunkt in der DB: {latest_timestamp}")
        return latest_timestamp
    else:
        print(
            "Keine Datenpunkte in der DB gefunden. Verwende einen Standardstartzeitpunkt.")
        return datetime.now(timezone.utc) - timedelta(days=1)


# Berechne die Zeitintervalle mit UTC-Zeitzone
latest_timestamp = get_latest_timestamp()
start_date = latest_timestamp + timedelta(minutes=1)
end_date = datetime.now(timezone.utc)  # Nutze timezone-aware datetime
delta = timedelta(days=7)  # Maximal 7 Tage pro Abruf

all_data = []

while start_date < end_date:
    next_end_date = min(start_date + delta, end_date)
    print(f"Lade Daten von {start_date} bis {next_end_date}")
    try:
        data = yf.download(symbol, start=start_date,
                           end=next_end_date, interval=interval)
        all_data.append(data)
    except Exception as e:
        print(f"Fehler beim Abrufen der Daten: {e}")
    start_date = next_end_date

# Zusammenführen aller abgerufenen Daten
if all_data:
    data = pd.concat(all_data)
    data.index = pd.to_datetime(data.index)
    data.columns = data.columns.droplevel(1)

    # Daten in InfluxDB schreiben
    points = []
    for index, row in data.iterrows():
        try:
            point = Point("market_data") \
                .tag("source", "yahoo_finance") \
                .field("open", row["Open"]) \
                .field("high", row["High"]) \
                .field("low", row["Low"]) \
                .field("close", row["Close"]) \
                .field("volume", row["Volume"]) \
                .time(index, WritePrecision.NS)
            points.append(point)
        except ValueError as e:
            print(f"Fehler beim Konvertieren der Daten: {e}")
            continue

    # Batch-Schreiben aller gesammelten Punkte
    if points:
        write_api.write(bucket=bucket, org=org, record=points)
        print(f"{len(points)} Datenpunkte erfolgreich geschrieben.")

print("Datenimport von Yahoo Finance abgeschlossen.")
client.close()
