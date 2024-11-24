from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
from influxdb_client import InfluxDBClient, Point
import os

# Kafka Configuration
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka-cluster-kafka-bootstrap.crypto-tracker.svc:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "default-topic")

# InfluxDB Configuration
INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST", "http://crypto-tracker-influxdb2.crypto-tracker.svc:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN", "default-secret-token")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG", "default-org")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET", "default-bucket")

# Define schema for Kafka messages
schema = StructType([
    StructField("timestamp", TimestampType(), True),
    StructField("coin", StringType(), True),
    StructField("open", FloatType(), True),
    StructField("high", FloatType(), True),
    StructField("low", FloatType(), True),
    StructField("close", FloatType(), True),
    StructField("volume", FloatType(), True)
])

def write_to_influxdb(partition):
    """
    Write a partition of data rows to InfluxDB.

    Args:
        partition: Iterable of rows, each row containing the schema-defined fields.
    """
    with InfluxDBClient(url=INFLUXDB_HOST, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        write_api = client.write_api()
        for row in partition:
            try:
                # Construct InfluxDB Point
                point = Point("crypto_data") \
                    .tag("coin", row.coin) \
                    .field("open", row.open) \
                    .field("high", row.high) \
                    .field("low", row.low) \
                    .field("close", row.close) \
                    .field("volume", row.volume) \
                    .time(row.timestamp)
                # Write point to InfluxDB
                write_api.write(bucket=INFLUXDB_BUCKET, record=point)
                print(f"Successfully wrote data to InfluxDB: {row}")
            except Exception as e:
                print(f"Error writing to InfluxDB: {e}")

# Initialize Spark session
spark = SparkSession.builder \
    .appName("CryptoDataProcessor") \
    .getOrCreate()

# Read data from Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

# Deserialize JSON messages
value_df = kafka_df.selectExpr("CAST(value AS STRING) as value") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

def process_and_write(df, epoch_id):
    """
    Process each micro-batch of data and write to InfluxDB.

    Args:
        df: Spark DataFrame for the micro-batch.
        epoch_id: ID of the micro-batch for Spark's structured streaming.
    """
    df.foreachPartition(write_to_influxdb)

# Write data using foreachBatch function
query = value_df.writeStream \
    .foreachBatch(process_and_write) \
    .start()

# Wait for termination
query.awaitTermination()