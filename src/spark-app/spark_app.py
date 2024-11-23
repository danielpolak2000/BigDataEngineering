from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
import os

# Kafka Configuration
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka-cluster-kafka-bootstrap:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "crypto-data")

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

# Define how to process rows from each batch (placeholder function)
def process_row_partition(partition):
    for row in partition:
        print(f"Processing row: {row}")

# Write data using a foreachBatch function
query = value_df.writeStream \
    .foreachBatch(lambda df, _: df.foreachPartition(process_row_partition)) \
    .start()

# Wait for termination
query.awaitTermination()