#!/bin/bash

echo "🚀 Configurando Kafka + Spark Streaming Pipeline"

# Criar tópicos Kafka
echo "📡 Criando tópicos Kafka..."
docker exec kafka kafka-topics --create --topic iot_sensors --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
docker exec kafka kafka-topics --create --topic user_activity --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Criar tabelas PostgreSQL
echo "🗄️ Criando tabelas PostgreSQL..."
docker exec -i postgres psql -U postgres -d streaming_data << EOF
CREATE TABLE IF NOT EXISTS sensor_data (
    device_id VARCHAR(50),
    timestamp TIMESTAMP,
    location VARCHAR(100),
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    battery_level DOUBLE PRECISION,
    signal_strength INTEGER,
    event_id VARCHAR(100),
    processed_time TIMESTAMP,
    temperature_fahrenheit DOUBLE PRECISION,
    alert_high_temp VARCHAR(10),
    battery_status VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS user_activity (
    user_id VARCHAR(50),
    timestamp TIMESTAMP,
    action VARCHAR(50),
    page_url VARCHAR(200),
    browser VARCHAR(50),
    session_duration INTEGER,
    ip_address VARCHAR(15),
    event_id VARCHAR(100),
    processed_time TIMESTAMP,
    session_category VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS sensor_aggregations (
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    location VARCHAR(100),
    device_id VARCHAR(50),
    avg_temperature DOUBLE PRECISION,
    max_temperature DOUBLE PRECISION,
    min_temperature DOUBLE PRECISION,
    avg_humidity DOUBLE PRECISION,
    event_count BIGINT
);
EOF

echo "✅ Setup completo!"
echo ""
echo "🔗 URLs de acesso:"
echo "  - Kafka UI: http://localhost:9092"
echo "  - Spark Master: http://localhost:8080"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "🚀 Para iniciar:"
echo "  1. python producers/iot_data_generator.py"
echo "  2. python consumers/spark_streaming_processor.py"