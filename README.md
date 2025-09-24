# Kafka + Spark Streaming Pipeline

Pipeline de dados em tempo real usando Apache Kafka e Spark Streaming para processamento de dados IoT e atividade de usuários.

## 🏗️ Arquitetura

```
IoT Sensors → Kafka → Spark Streaming → PostgreSQL → Grafana
User Events → Kafka → Spark Streaming → PostgreSQL → Grafana
```

## 🚀 Características

- **Streaming em Tempo Real**: Processamento contínuo de dados
- **Múltiplas Fontes**: Sensores IoT + Atividade de usuários
- **Agregações**: Janelas de tempo com watermarks
- **Alertas**: Detecção de anomalias em tempo real
- **Visualização**: Dashboards no Grafana
- **Escalabilidade**: Kafka particionado + Spark distribuído

## 🛠️ Stack Tecnológica

- **Apache Kafka**: Message broker para streaming
- **Apache Spark**: Processamento distribuído
- **PostgreSQL**: Armazenamento de dados processados
- **Grafana**: Visualização e dashboards
- **Docker**: Containerização completa
- **Python**: Produtores e consumidores

## 📦 Componentes

### Produtores de Dados
- **IoT Data Generator**: Simula sensores (temperatura, umidade, pressão)
- **User Activity Generator**: Simula atividade web (login, compras, navegação)

### Processamento Spark
- **Real-time Processing**: Transformações em tempo real
- **Windowed Aggregations**: Métricas por janelas de tempo
- **Alerting**: Detecção de temperaturas altas e bateria baixa
- **Data Enrichment**: Conversões e categorizações

### Armazenamento
- **PostgreSQL**: Dados processados e agregações
- **Checkpointing**: Garantia de exactly-once processing

## 🚀 Como Executar

### 1. Iniciar Infraestrutura
```bash
# Subir todos os serviços
docker-compose up -d

# Aguardar inicialização (2-3 minutos)
docker-compose logs -f
```

### 2. Configurar Ambiente
```bash
# Executar setup
chmod +x setup.sh
./setup.sh

# Instalar dependências Python
pip install -r requirements.txt
```

### 3. Iniciar Pipeline
```bash
# Terminal 1: Gerar dados
python producers/iot_data_generator.py

# Terminal 2: Processar com Spark
python consumers/spark_streaming_processor.py
```

## 📊 Monitoramento

### URLs de Acesso
- **Spark Master UI**: http://localhost:8080
- **Grafana**: http://localhost:3000 (admin/admin)
- **PostgreSQL**: localhost:5432 (postgres/postgres)

### Métricas Disponíveis
- Temperatura média por localização
- Alertas de temperatura alta
- Status de bateria dos sensores
- Atividade de usuários por browser
- Duração de sessões

## 🔧 Configurações

### Kafka Topics
- `iot_sensors`: Dados de sensores IoT
- `user_activity`: Atividade de usuários

### Spark Streaming
- **Batch Interval**: 5 segundos
- **Watermark**: 10 minutos
- **Window Size**: 5 minutos
- **Checkpoint**: Habilitado para fault tolerance

### Alertas Configurados
- 🌡️ **Temperatura Alta**: > 30°C
- 🔋 **Bateria Baixa**: < 20%
- ⏱️ **Sessão Longa**: > 5 minutos

## 📈 Casos de Uso

1. **Monitoramento IoT**: Sensores industriais em tempo real
2. **Analytics Web**: Comportamento de usuários
3. **Detecção de Anomalias**: Alertas automáticos
4. **Dashboards Executivos**: KPIs em tempo real

## 🧪 Testes

```bash
# Verificar tópicos Kafka
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Verificar dados no PostgreSQL
docker exec -it postgres psql -U postgres -d streaming_data -c "SELECT COUNT(*) FROM sensor_data;"

# Monitorar logs Spark
docker logs spark-master
```

## 🔄 Próximos Passos

- [ ] Implementar Schema Registry
- [ ] Adicionar Kafka Connect
- [ ] Criar alertas no Grafana
- [ ] Implementar ML para detecção de anomalias
- [ ] Adicionar testes unitários

## 📚 Tecnologias Demonstradas

- **Stream Processing**: Kafka + Spark Streaming
- **Real-time Analytics**: Agregações com janelas
- **Data Engineering**: ETL em tempo real
- **DevOps**: Docker + containerização
- **Monitoring**: Grafana + métricas

---

Desenvolvido por Ivan de França