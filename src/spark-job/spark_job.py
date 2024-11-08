from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, FloatType, LongType
import influxdb_client

# Kafka und InfluxDB Konfiguration
kafka_bootstrap_servers = "my-kafka-cluster-kafka-bootstrap.kafka:9092"
influxdb_url = "http://influxdb:8086"
database = "bitcoin_trading"

# Spark-Session
spark = SparkSession.builder.appName("BitcoinTradingBot").getOrCreate()

# Kafka-Datenquelle und Schema
schema = StructType([
    StructField("price", FloatType()),
    StructField("timestamp", LongType())
])

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", "bitcoin-kursdaten") \
    .load()

data_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

# Schreiben in InfluxDB
def write_to_influxdb(df, epoch_id):
    client = influxdb_client.InfluxDBClient(url=influxdb_url, token="my-token", org="my-org")
    write_api = client.write_api(write_options=influxdb_client.client.write_api.SYNCHRONOUS)
    points = [
        {
            "measurement": "bitcoin_price",
            "tags": {},
            "fields": {"price": row.price},
            "time": row.timestamp
        }
        for row in df.collect()
    ]
    write_api.write(bucket=database, record=points)

data_df.writeStream.foreachBatch(write_to_influxdb).start().awaitTermination()