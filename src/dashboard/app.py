import pandas as pd
from influxdb_client import InfluxDBClient
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# InfluxDB 2.x Konfiguration
INFLUXDB_URL = os.environ.get("INFLUXDB_HOST", "influxdb")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG", "organization")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET", "bucket")

# InfluxDB-Client initialisieren
influxdb_client = InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = influxdb_client.query_api()

# Auto-Refresh alle 10 Sekunden
st_autorefresh(interval=10000, key="data_refresh")

# Streamlit-Seite konfigurieren
st.set_page_config(page_title="InfluxDB Visualisierung", layout="wide")

# Titel und Beschreibung
st.title("Bitcoin-Daten Visualisierung")
st.write("Interaktive Visualisierung der Bitcoin-Daten aus der InfluxDB.")

# Flux-Query für InfluxDB 2.x
query = f"""
from(bucket: "{INFLUXDB_BUCKET}")
  |> range(start: -1h)  // Daten der letzten Stunde
  |> filter(fn: (r) => r["_measurement"] == "crypto_data")
"""

try:
    # Daten abfragen
    result = query_api.query(org=INFLUXDB_ORG, query=query)

    # Daten in ein DataFrame umwandeln
    data = []
    for table in result:
        for record in table.records:
            data.append({
                "time": record.get_time(),
                "field": record.get_field(),
                "value": record.get_value()
            })
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Fehler beim Abrufen der Daten: {e}")
    st.stop()

# Prüfen, ob Daten vorhanden sind
if df.empty:
    st.warning("Keine Daten verfügbar.")
    st.stop()

# Daten für die Visualisierung aufbereiten
df["time"] = pd.to_datetime(df["time"])
df.set_index("time", inplace=True)

# Visualisierung: Kursentwicklung
st.subheader("Kursentwicklung")
kurs_df = df[df["field"].isin(["Open", "High", "Low", "Close"])]
kurs_pivot = kurs_df.pivot_table(
    values="value", index=kurs_df.index, columns="field")
st.line_chart(kurs_pivot)

# Visualisierung: Handelsvolumen
st.subheader("Handelsvolumen")
volumen_df = df[df["field"] == "Volume"]
volumen_pivot = volumen_df.pivot_table(values="value", index=volumen_df.index)
st.bar_chart(volumen_pivot)

# Rohdaten anzeigen
st.subheader("Rohdaten")
st.dataframe(df)

# Verbindung schließen
influxdb_client.close()
