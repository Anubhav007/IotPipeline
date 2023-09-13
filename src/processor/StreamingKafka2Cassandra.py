from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StructField, DoubleType, IntegerType, StringType, TimestampType
from pyspark.sql.functions import from_json, window, col, avg, min, max, median, to_timestamp

# Create a spark session
spark = SparkSession \
    .builder \
    .appName("IoTDataProcessor") \
    .config("spark.cassandra.connection.host","172.18.0.5")\
    .config("spark.cassandra.connection.port","9042")\
    .config("spark.cassandra.auth.username","cassandra")\
    .config("spark.cassandra.auth.password","cassandra")\
    .config("spark.driver.host", "localhost")\
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Define the schema of the iot_data. Be careful, the schema should match the schema of the Kafka topic iot_data
sensorDataSchema = StructType([
                StructField("device_id",StringType(),False),
                StructField("device_type",StringType(),False),
                StructField("timestamp",TimestampType(),False),
                StructField("value",IntegerType(),False)
            ])

# Read the iot data from kafka topic as a streaming dataframe
sensorDf = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "kafka:9092") \
  .option("subscribe", "iot_data") \
  .option("delimeter",",") \
  .option("startingOffsets", "earliest") \
  .load() 

sensorDf.printSchema()

sensorDf = sensorDf.selectExpr("CAST(value AS STRING)").select(from_json(col("value"), sensorDataSchema).alias("data")).select("data.*")

# Define window and slide duration
windowDuration = "60 seconds"
slideDuration = "30 seconds"

def writeToCassandra(writeDF, _):
  writeDF.write \
    .format("org.apache.spark.sql.cassandra")\
    .mode('append')\
    .options(table="iot_results", keyspace="test")\
    .save()

# Group sensor data by device_id and window
sensorDf = sensorDf.groupBy(
    col("device_id"),
    window(col("timestamp"), windowDuration, slideDuration)
)

# Compute aggregates
sensorDf = sensorDf.agg(
    avg(col("value")).alias("avg_value"),
    min(col("value")).alias("min_value"),
    max(col("value")).alias("max_value"),
    median(col("value")).alias("max_value")
)

# Group by Window would create a column having start and end timestamp in the same structField, we need to split them into two columns namely window_start_timestamp and window_end_timestamp
sensorDf = sensorDf.withColumn("window_start_timestamp", to_timestamp(col("window").getItem('start'), "yyyy-MM-dd HH:mm:ss")).withColumn("window_end_timestamp", to_timestamp(col("window").getItem('end'), "yyyy-MM-dd HH:mm:ss")).drop("window")

sensorDf = sensorDf.select('device_id', 'device_type', 'window_start_timestamp', 'window_end_timestamp', 'avg_value', 'median_value', 'max_value', 'min_value')

# (Optional) You can print the streaming aggregates on the console using the following command
# sensorDf.writeStream \
#   .outputMode("update") \
#   .format("console") \
#   .option("truncate", False) \
#   .start() \
#   .awaitTermination()

# Write streaming dataframe to cassandra sink
sensorDf.writeStream \
    .foreachBatch(writeToCassandra) \
    .outputMode("update") \
    .start()\
    .awaitTermination()
sensorDf.show()
