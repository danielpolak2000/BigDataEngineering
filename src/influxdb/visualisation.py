import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd

# Streamlit-Seite konfigurieren
st.set_page_config(page_title="InfluxDB Visualisierung", layout="wide")

# Titel und Beschreibung
st.title("Bitcoin-Daten Visualisierung")
st.write("Interaktive Visualisierung der Bitcoin-Daten aus der InfluxDB.")

# InfluxDB Konfigurationsparameter
bucket = "marketdata"  # Dein Bucket-Name
org = "tesmarketdata-orgt"  # Deine Organisation
token = "rFU9szMFNSBCx1Z1jH3QIEBMLx-3L5XdOhDD-VVuRghCGMoRkgeHWnoBBTkt719rThPJg0B-OGHpyU9Rfjp8Fw=="  # Dein Token
url = "http://localhost:8086"  # Deine InfluxDB-URL

# Verbindung herstellen
try:
    client = InfluxDBClient(url=url, token=token, org=org)
    st.success("Erfolgreich mit der InfluxDB verbunden!")
except Exception as e:
    st.error(f"Fehler beim Verbinden mit der InfluxDB: {e}")
    st.stop()

# Daten aus der InfluxDB abrufen
query = f"""
from(bucket: "{bucket}")
|> range(start: -30d)  // Daten der letzten 30 Tage
|> filter(fn: (r) => r["_measurement"] == "bitcoin_data")
"""

try:
    query_api = client.query_api()
    result = query_api.query(org=org, query=query)
    
    # Daten in ein Pandas-DataFrame umwandeln
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
kurs_pivot = kurs_df.pivot_table(values="value", index=kurs_df.index, columns="field")
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
client.close()
