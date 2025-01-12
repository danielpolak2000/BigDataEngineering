# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kaggle API Key kopieren
COPY kaggle.json /root/.kaggle/kaggle.json
RUN chmod 600 /root/.kaggle/kaggle.json

# Download und Entpacken der CSV-Daten
RUN kaggle datasets download -d mczielinski/bitcoin-historical-data -p /app && \
    unzip /app/bitcoin-historical-data.zip -d /app && \
    rm /app/bitcoin-historical-data.zip

# Python-Skripte kopieren
COPY data_collector.py .
COPY yfinance_loader.py .
COPY entrypoint.sh .

# Entrypoint-Skript ausführbar machen
RUN chmod +x entrypoint.sh

# Set the entry point for the container
ENTRYPOINT ["./entrypoint.sh"]