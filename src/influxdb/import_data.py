import pandas as pd
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta, timezone

# InfluxDB-Konfigurationen
token = "rFU9szMFNSBCx1Z1jH3QIEBMLx-3L5XdOhDD-VVuRghCGMoRkgeHWnoBBTkt719rThPJg0B-OGHpyU9Rfjp8Fw=="
org = "marketdata-org"
bucket = "marketdata"
url = "http://localhost:8086"  # Die URL des InfluxDB-Servers

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

csv_file = "bitcoin-historical-data.csv"
data = pd.read_csv(csv_file)

# Konvertiere Timestamps und schreibe in InfluxDB
data['Timestamp'] = pd.to_datetime(
    data['Timestamp'], unit='s').dt.tz_localize("UTC")
data.set_index("Timestamp", inplace=True)

points = []
for index, row in data.iterrows():
    point = Point("market_data") \
        .tag("source", "csv_import") \
        .field("open", row["Open"]) \
        .field("high", row["High"]) \
        .field("low", row["Low"]) \
        .field("close", row["Close"]) \
        .field("volume", row["Volume"]) \
        .time(index, WritePrecision.NS)
    points.append(point)

# Batch-Schreiben in die Datenbank
write_api.write(bucket=bucket, org=org, record=points)
print(f"{len(points)} Datenpunkte erfolgreich in die InfluxDB importiert.")
client.close()
