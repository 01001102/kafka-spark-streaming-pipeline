from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

class StreamingProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("KafkaSparkStreaming") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.postgresql:postgresql:42.6.0") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
    
    def create_kafka_stream(self, topic, bootstrap_servers="kafka:29092"):
        """Cria stream do Kafka"""
        return self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", bootstrap_servers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .load()
    
    def process_sensor_data(self):
        """Processa dados de sensores IoT"""
        # Schema dos dados de sensores
        sensor_schema = StructType([
            StructField("device_id", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("location", StringType(), True),
            StructField("temperature", DoubleType(), True),
            StructField("humidity", DoubleType(), True),
            StructField("pressure", DoubleType(), True),
            StructField("battery_level", DoubleType(), True),
            StructField("signal_strength", IntegerType(), True),
            StructField("event_id", StringType(), True)
        ])
        
        # Lê stream do Kafka
        kafka_stream = self.create_kafka_stream("iot_sensors")
        
        # Parse JSON e aplica transformações
        parsed_stream = kafka_stream \
            .select(from_json(col("value").cast("string"), sensor_schema).alias("data")) \
            .select("data.*") \
            .withColumn("processed_time", current_timestamp()) \
            .withColumn("temperature_celsius", col("temperature")) \
            .withColumn("temperature_fahrenheit", col("temperature") * 9/5 + 32) \
            .withColumn("alert_high_temp", when(col("temperature") > 30, "HIGH").otherwise("NORMAL")) \
            .withColumn("battery_status", 
                       when(col("battery_level") < 20, "LOW")
                       .when(col("battery_level") < 50, "MEDIUM")
                       .otherwise("HIGH"))
        
        return parsed_stream
    
    def process_user_activity(self):
        """Processa dados de atividade de usuários"""
        user_schema = StructType([
            StructField("user_id", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("action", StringType(), True),
            StructField("page_url", StringType(), True),
            StructField("browser", StringType(), True),
            StructField("session_duration", IntegerType(), True),
            StructField("ip_address", StringType(), True),
            StructField("event_id", StringType(), True)
        ])
        
        kafka_stream = self.create_kafka_stream("user_activity")
        
        parsed_stream = kafka_stream \
            .select(from_json(col("value").cast("string"), user_schema).alias("data")) \
            .select("data.*") \
            .withColumn("processed_time", current_timestamp()) \
            .withColumn("session_category",
                       when(col("session_duration") < 60, "SHORT")
                       .when(col("session_duration") < 300, "MEDIUM")
                       .otherwise("LONG"))
        
        return parsed_stream
    
    def write_to_postgres(self, df, table_name, checkpoint_location):
        """Escreve dados no PostgreSQL"""
        return df.writeStream \
            .outputMode("append") \
            .foreachBatch(lambda batch_df, batch_id: 
                         batch_df.write
                         .format("jdbc")
                         .option("url", "jdbc:postgresql://postgres:5432/streaming_data")
                         .option("dbtable", table_name)
                         .option("user", "postgres")
                         .option("password", "postgres")
                         .option("driver", "org.postgresql.Driver")
                         .mode("append")
                         .save()) \
            .option("checkpointLocation", checkpoint_location) \
            .start()
    
    def write_to_console(self, df, query_name):
        """Escreve dados no console para debug"""
        return df.writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", False) \
            .queryName(query_name) \
            .start()
    
    def create_aggregations(self, sensor_df):
        """Cria agregações em tempo real"""
        # Agregação por janela de tempo
        windowed_aggregation = sensor_df \
            .withWatermark("processed_time", "10 minutes") \
            .groupBy(
                window(col("processed_time"), "5 minutes"),
                col("location"),
                col("device_id")
            ) \
            .agg(
                avg("temperature").alias("avg_temperature"),
                max("temperature").alias("max_temperature"),
                min("temperature").alias("min_temperature"),
                avg("humidity").alias("avg_humidity"),
                count("*").alias("event_count")
            )
        
        return windowed_aggregation
    
    def start_processing(self):
        """Inicia o processamento dos streams"""
        print("Iniciando processamento de streams...")
        
        # Processa dados de sensores
        sensor_stream = self.process_sensor_data()
        
        # Processa dados de usuários
        user_stream = self.process_user_activity()
        
        # Cria agregações
        sensor_aggregations = self.create_aggregations(sensor_stream)
        
        # Inicia queries de escrita
        sensor_query = self.write_to_console(sensor_stream, "sensor_data")
        user_query = self.write_to_console(user_stream, "user_activity")
        agg_query = self.write_to_console(sensor_aggregations, "sensor_aggregations")
        
        # Aguarda término
        try:
            sensor_query.awaitTermination()
            user_query.awaitTermination()
            agg_query.awaitTermination()
        except KeyboardInterrupt:
            print("Parando processamento...")
            sensor_query.stop()
            user_query.stop()
            agg_query.stop()

if __name__ == "__main__":
    processor = StreamingProcessor()
    processor.start_processing()