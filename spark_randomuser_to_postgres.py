from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType

spark = SparkSession.builder \
    .appName("RandomUserKafkaToPostgres") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType() \
    .add("id", StringType()) \
    .add("name", StringType()) \
    .add("gender", StringType()) \
    .add("email", StringType()) \
    .add("country", StringType())

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "randomuser-topic") \
    .option("startingOffsets", "earliest") \
    .load()

parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*") \
 .filter(col("id").isNotNull())

def write_to_postgres(batch_df, batch_id):
    if batch_df.count() == 0:
        return

    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5432/randomuser_db") \
        .option("dbtable", "users") \
        .option("user", "postgres") \
        .option("password", "post") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

query = parsed_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .option("checkpointLocation", "/tmp/randomuser_checkpoint") \
    .start()

query.awaitTermination()
