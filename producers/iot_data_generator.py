import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer
import uuid


class IoTDataGenerator:
    """
    Gerador de dados simulados para sensores IoT e atividade de usuários.
    
    Esta classe é responsável por gerar dados sintéticos que simulam sensores IoT
    e atividade de usuários em tempo real, enviando os dados para tópicos Kafka.
    
    Attributes:
        producer (KafkaProducer): Instância do produtor Kafka para envio de mensagens.
    """
    
    def __init__(self, bootstrap_servers='localhost:9092'):
        """
        Inicializa o gerador de dados IoT.
        
        Args:
            bootstrap_servers (str): Endereço dos servidores Kafka bootstrap.
                                   Padrão: 'localhost:9092'
        """
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
    def generate_sensor_data(self):
        """
        Gera dados simulados de sensores IoT.
        
        Simula dados de sensores industriais incluindo temperatura, umidade,
        pressão atmosférica, nível de bateria e força do sinal.
        
        Returns:
            dict: Dicionário contendo os dados do sensor com as seguintes chaves:
                - device_id: Identificador único do dispositivo
                - timestamp: Timestamp ISO da coleta
                - location: Localização física do sensor
                - temperature: Temperatura em Celsius (18.0-35.0)
                - humidity: Umidade relativa em % (30.0-80.0)
                - pressure: Pressão atmosférica em hPa (980.0-1020.0)
                - battery_level: Nível da bateria em % (10.0-100.0)
                - signal_strength: Força do sinal em dBm (-100 a -30)
                - event_id: UUID único do evento
        """
        devices = ['sensor_001', 'sensor_002', 'sensor_003', 'sensor_004', 'sensor_005']
        locations = ['warehouse_a', 'warehouse_b', 'factory_floor', 'office_building']
        
        return {
            'device_id': random.choice(devices),
            'timestamp': datetime.now().isoformat(),
            'location': random.choice(locations),
            'temperature': round(random.uniform(18.0, 35.0), 2),
            'humidity': round(random.uniform(30.0, 80.0), 2),
            'pressure': round(random.uniform(980.0, 1020.0), 2),
            'battery_level': round(random.uniform(10.0, 100.0), 2),
            'signal_strength': random.randint(-100, -30),
            'event_id': str(uuid.uuid4())
        }
    
    def generate_user_activity(self):
        """
        Gera dados simulados de atividade de usuários.
        
        Simula eventos de usuários em uma aplicação web, incluindo ações
        como login, navegação, compras e informações de sessão.
        
        Returns:
            dict: Dicionário contendo os dados de atividade com as seguintes chaves:
                - user_id: Identificador único do usuário
                - timestamp: Timestamp ISO do evento
                - action: Ação realizada pelo usuário
                - page_url: URL da página acessada
                - browser: Navegador utilizado
                - session_duration: Duração da sessão em segundos
                - ip_address: Endereço IP simulado
                - event_id: UUID único do evento
        """
        actions = ['login', 'logout', 'view_page', 'purchase', 'add_to_cart', 'search']
        browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
        
        return {
            'user_id': f"user_{random.randint(1000, 9999)}",
            'timestamp': datetime.now().isoformat(),
            'action': random.choice(actions),
            'page_url': f"/page_{random.randint(1, 100)}",
            'browser': random.choice(browsers),
            'session_duration': random.randint(30, 3600),
            'ip_address': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'event_id': str(uuid.uuid4())
        }
    
    def start_streaming(self, topic_sensors='iot_sensors', topic_users='user_activity', interval=1):
        """
        Inicia o streaming contínuo de dados para os tópicos Kafka.
        
        Executa um loop infinito gerando e enviando dados de sensores IoT e
        atividade de usuários para os respectivos tópicos Kafka.
        
        Args:
            topic_sensors (str): Nome do tópico Kafka para dados de sensores.
                               Padrão: 'iot_sensors'
            topic_users (str): Nome do tópico Kafka para atividade de usuários.
                             Padrão: 'user_activity'
            interval (int): Intervalo em segundos entre envios de dados.
                          Padrão: 1 segundo
        
        Raises:
            KeyboardInterrupt: Capturado para parada graceful do streaming.
        """
        print(f"Iniciando geração de dados para tópicos: {topic_sensors}, {topic_users}")
        
        try:
            while True:
                sensor_data = self.generate_sensor_data()
                self.producer.send(topic_sensors, sensor_data)
                
                if random.random() < 0.7:
                    user_data = self.generate_user_activity()
                    self.producer.send(topic_users, user_data)
                
                print(f"Dados enviados - Sensor: {sensor_data['device_id']}, Temp: {sensor_data['temperature']}°C")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("Parando geração de dados...")
        finally:
            self.producer.close()

if __name__ == "__main__":
    generator = IoTDataGenerator()
    generator.start_streaming()