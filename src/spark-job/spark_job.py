from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType
from influxdb import InfluxDBClient
import os

# Kafka Configuration
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka-cluster-kafka-bootstrap.kafka:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "crypto-data")

# InfluxDB Configuration
INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST", "influxdb")
INFLUXDB_PORT = os.environ.get("INFLUXDB_PORT", 8086)
INFLUXDB_DATABASE = os.environ.get("INFLUXDB_DATABASE", "crypto_data")

# Define the schema for the incoming Kafka messages
schema = StructType([
    StructField("currency", StringType(), True),
    StructField("price", FloatType(), True),
    StructField("volume", IntegerType(), True)
])

def write_to_influxdb(batch_df, batch_id):
    """
    Function to write Spark DataFrame to InfluxDB
    """
    influxdb_client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
    influxdb_client.switch_database(INFLUXDB_DATABASE)

    points = []
    for row in batch_df.collect():
        point = {
            "measurement": "crypto_data",
            "tags": {
                "currency": row.currency
            },
            "fields": {
                "price": row.price,
                "volume": row.volume
            },
            "time": row.timestamp
        }
        points.append(point)

    if points:
        influxdb_client.write_points(points)
        print(f"Written {len(points)} points to InfluxDB.")

# Spark Session
spark = SparkSession \
    .builder \
    .appName("CryptoSparkJob") \
    .master("local[*]") \
    .getOrCreate()

# Read data from Kafka
crypto_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

# Decode Kafka message value as JSON
crypto_data = crypto_stream \
    .select(from_json(col("value").cast("string"), schema).alias("data")) \
    .select("data.*")

# Write processed data to InfluxDB
query = crypto_data.writeStream \
    .foreachBatch(write_to_influxdb) \
    .outputMode("update") \
    .start()

query.awaitTermination()
