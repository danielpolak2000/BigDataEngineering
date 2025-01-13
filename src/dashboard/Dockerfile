# Basis-Image mit Python 3.9
FROM python:3.9-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY app.py .

# Port 5000 freigeben
EXPOSE 5000

# Streamlit-App auf Port 5000 starten
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]