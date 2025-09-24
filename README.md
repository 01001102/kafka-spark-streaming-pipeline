# Kafka Spark Streaming Pipeline

Pipeline de processamento de dados em tempo real utilizando Apache Kafka e Spark Streaming para análise de dados IoT e atividade de usuários.

## Arquitetura

```
IoT Sensors → Kafka → Spark Streaming → PostgreSQL → Grafana
User Events → Kafka → Spark Streaming → PostgreSQL → Grafana
```

## Características Principais

- **Processamento em Tempo Real**: Stream processing contínuo de dados
- **Múltiplas Fontes de Dados**: Integração de sensores IoT e eventos de usuários
- **Agregações Temporais**: Janelas de tempo com watermarks para análises
- **Detecção de Anomalias**: Sistema de alertas em tempo real
- **Visualização de Dados**: Dashboards interativos com Grafana
- **Escalabilidade Horizontal**: Arquitetura distribuída com Kafka e Spark

## Stack Tecnológica

- **Apache Kafka**: Message broker para streaming de dados
- **Apache Spark**: Engine de processamento distribuído
- **PostgreSQL**: Banco de dados para armazenamento persistente
- **Grafana**: Plataforma de visualização e monitoramento
- **Docker**: Containerização e orquestração de serviços
- **Python**: Linguagem para produtores e consumidores

## Componentes do Sistema

### Geradores de Dados
- **IoT Data Generator**: Simulação de sensores industriais (temperatura, umidade, pressão atmosférica)
- **User Activity Generator**: Simulação de eventos de usuários web (autenticação, navegação, transações)

### Engine de Processamento
- **Transformações em Tempo Real**: Enriquecimento e limpeza de dados
- **Agregações por Janela**: Cálculo de métricas estatísticas temporais
- **Sistema de Alertas**: Detecção automática de anomalias e condições críticas
- **Enriquecimento de Dados**: Categorização e conversões de unidades

### Camada de Persistência
- **PostgreSQL**: Armazenamento de dados processados e métricas agregadas
- **Checkpointing**: Garantia de processamento exactly-once com tolerância a falhas

## Guia de Execução

### 1. Inicialização da Infraestrutura
```bash
# Inicializar todos os serviços containerizados
docker-compose up -d

# Monitorar logs de inicialização
docker-compose logs -f
```

### 2. Configuração do Ambiente
```bash
# Executar script de configuração inicial
chmod +x setup.sh
./setup.sh

# Instalar dependências Python
pip install -r requirements.txt
```

### 3. Execução do Pipeline
```bash
# Terminal 1: Iniciar gerador de dados
python producers/iot_data_generator.py

# Terminal 2: Iniciar processador Spark
python consumers/spark_streaming_processor.py
```

## Monitoramento e Observabilidade

### Interfaces de Monitoramento
- **Spark Master UI**: http://localhost:8080
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **PostgreSQL**: localhost:5432 (postgres/postgres)

### Métricas e KPIs
- Métricas agregadas de temperatura por localização
- Alertas de condições críticas de temperatura
- Monitoramento de status de bateria dos dispositivos
- Análise de comportamento de usuários por navegador
- Métricas de duração e qualidade de sessões

## Configurações do Sistema

### Tópicos Kafka
- `iot_sensors`: Stream de dados de sensores IoT
- `user_activity`: Stream de eventos de atividade de usuários

### Parâmetros Spark Streaming
- **Intervalo de Batch**: 5 segundos
- **Watermark**: 10 minutos para dados atrasados
- **Tamanho da Janela**: 5 minutos para agregações
- **Checkpointing**: Habilitado para tolerância a falhas

### Critérios de Alerta
- **Temperatura Crítica**: Acima de 30°C
- **Bateria Baixa**: Abaixo de 20%
- **Sessão Prolongada**: Superior a 5 minutos

## Casos de Uso

1. **Monitoramento Industrial**: Supervisão de sensores em tempo real
2. **Analytics Comportamental**: Análise de padrões de usuários
3. **Detecção Proativa**: Sistema de alertas para anomalias
4. **Business Intelligence**: Dashboards executivos com KPIs

## Validação e Testes

```bash
# Verificar tópicos Kafka disponíveis
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Validar dados armazenados no PostgreSQL
docker exec -it postgres psql -U postgres -d streaming_data -c "SELECT COUNT(*) FROM sensor_data;"

# Monitorar logs do Spark Master
docker logs spark-master

# Verificar status dos containers
docker-compose ps
```

## Roadmap de Desenvolvimento

- [ ] Implementação de Schema Registry para versionamento
- [ ] Integração com Kafka Connect para fontes externas
- [ ] Configuração de alertas avançados no Grafana
- [ ] Desenvolvimento de modelos ML para detecção de anomalias
- [ ] Implementação de testes unitários e de integração
- [ ] Otimização de performance e tuning de parâmetros

## Tecnologias e Conceitos Demonstrados

- **Stream Processing**: Processamento de dados em tempo real
- **Event-Driven Architecture**: Arquitetura orientada a eventos
- **Real-time Analytics**: Análises e agregações temporais
- **Data Engineering**: Pipeline ETL para big data
- **Containerization**: Orquestração com Docker Compose
- **Observability**: Monitoramento e visualização de métricas

## Licença

Este projeto é disponibilizado sob a licença MIT.

---

**Desenvolvido por Ivan de França**  
*Engenheiro de Dados 