from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json


class StreamingProcessor:
    """
    Processador de streaming em tempo real usando Apache Spark.
    
    Esta classe é responsável por processar dados de streaming do Kafka,
    aplicar transformações, agregações e escrever os resultados em
    diferentes destinos como PostgreSQL e console.
    
    Attributes:
        spark (SparkSession): Sessão Spark configurada para streaming.
    """
    
    def __init__(self):
        """
        Inicializa o processador de streaming Spark.
        
        Configura a sessão Spark com os pacotes necessários para
        integração com Kafka e PostgreSQL.
        """
        self.spark = SparkSession.builder \
            .appName("KafkaSparkStreaming") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.postgresql:postgresql:42.6.0") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
    
    def create_kafka_stream(self, topic, bootstrap_servers="kafka:29092"):
        """
        Cria um stream de dados do Kafka.
        
        Estabelece conexão com o cluster Kafka e cria um DataFrame
        de streaming para o tópico especificado.
        
        Args:
            topic (str): Nome do tópico Kafka para consumir dados.
            bootstrap_servers (str): Endereço dos servidores Kafka.
                                   Padrão: "kafka:29092"
        
        Returns:
            DataFrame: DataFrame de streaming conectado ao tópico Kafka.
        """
        return self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", bootstrap_servers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .load()
    
    def process_sensor_data(self):
        """
        Processa dados de sensores IoT do Kafka.
        
        Lê dados do tópico 'iot_sensors', aplica transformações como
        conversão de temperatura, categorização de alertas e status da bateria.
        
        Returns:
            DataFrame: DataFrame processado com dados enriquecidos dos sensores.
        """

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
        

        kafka_stream = self.create_kafka_stream("iot_sensors")
        

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
        """
        Processa dados de atividade de usuários do Kafka.
        
        Lê dados do tópico 'user_activity' e aplica transformações
        como categorização de sessões por duração.
        
        Returns:
            DataFrame: DataFrame processado com dados de atividade categorizados.
        """
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
        """
        Escreve dados processados no PostgreSQL.
        
        Configura um sink de streaming para escrever dados em uma
        tabela PostgreSQL com checkpoint para garantir exactly-once processing.
        
        Args:
            df (DataFrame): DataFrame de streaming para escrever.
            table_name (str): Nome da tabela PostgreSQL de destino.
            checkpoint_location (str): Caminho para armazenar checkpoints.
        
        Returns:
            StreamingQuery: Query de streaming ativa.
        """
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
        """
        Escreve dados no console para debug e monitoramento.
        
        Configura um sink de console para visualizar os dados
        processados em tempo real durante desenvolvimento.
        
        Args:
            df (DataFrame): DataFrame de streaming para exibir.
            query_name (str): Nome identificador da query.
        
        Returns:
            StreamingQuery: Query de streaming ativa.
        """
        return df.writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", False) \
            .queryName(query_name) \
            .start()
    
    def create_aggregations(self, sensor_df):
        """
        Cria agregações em tempo real dos dados de sensores.
        
        Aplica janelas de tempo com watermark para calcular métricas
        agregadas como temperatura média, máxima e mínima por localização.
        
        Args:
            sensor_df (DataFrame): DataFrame com dados de sensores processados.
        
        Returns:
            DataFrame: DataFrame com agregações por janela de tempo.
        """

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
        """
        Inicia o processamento completo dos streams de dados.
        
        Orquestra todo o pipeline de streaming: criação de streams,
        processamento, agregações e escrita nos destinos configurados.
        
        Raises:
            KeyboardInterrupt: Capturado para parada graceful do processamento.
        """
        print("Iniciando processamento de streams...")
        

        sensor_stream = self.process_sensor_data()
        

        user_stream = self.process_user_activity()
        

        sensor_aggregations = self.create_aggregations(sensor_stream)
        

        sensor_query = self.write_to_console(sensor_stream, "sensor_data")
        user_query = self.write_to_console(user_stream, "user_activity")
        agg_query = self.write_to_console(sensor_aggregations, "sensor_aggregations")
        

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