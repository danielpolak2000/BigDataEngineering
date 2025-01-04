from flask import Flask, render_template, jsonify
from influxdb import InfluxDBClient
import os

# Configuration
INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST", "influxdb")
INFLUXDB_PORT = os.environ.get("INFLUXDB_PORT", 8086)
INFLUXDB_DATABASE = os.environ.get("INFLUXDB_DATABASE", "crypto_data")

# Initialize Flask app
app = Flask(__name__)

# Initialize InfluxDB client
influxdb_client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
influxdb_client.switch_database(INFLUXDB_DATABASE)

@app.route("/")
def index():
    """
    Dashboard home page displaying the latest cryptocurrency data.
    """
    query = 'SELECT * FROM crypto_data ORDER BY time DESC LIMIT 10'
    result = influxdb_client.query(query)
    points = list(result.get_points())
    return render_template("index.html", data=points)

@app.route("/api/data")
def get_data():
    """
    API endpoint to fetch the latest cryptocurrency data.
    """
    query = 'SELECT * FROM crypto_data ORDER BY time DESC LIMIT 10'
    result = influxdb_client.query(query)
    return jsonify(list(result.get_points()))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
