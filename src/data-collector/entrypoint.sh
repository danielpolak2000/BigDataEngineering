#!/bin/bash

# 1. CSV-Daten einmalig in InfluxDB importieren
echo "🚀 Starte den CSV-Datenimport..."
python data_collector.py

# 2. Danach Yahoo Finance API für Live-Daten nutzen
echo "📡 Starte das Live-Update mit der Yahoo Finance API..."
while true; do
  python yfinance_loader.py
  echo "🔄 Nächster Live-Update in 60 Sekunden..."
  sleep 60
done