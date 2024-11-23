FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir yfinance influxdb-client kaggle

COPY import_data.py .
COPY yfinance_client.py .
COPY kaggle.json /root/.kaggle/kaggle.json

RUN chmod 600 /root/.kaggle/kaggle.json
RUN kaggle datasets download -d <mczielinski/bitcoin-historical-data> -p /app && \
    unzip /app/bitcoin-historical-data.zip -d /app && \
    rm /app/bitcoin-historical-data.zip

CMD ["bash", "-c", "python import_data.py && watch -n 60 python yfinance_client.py"]