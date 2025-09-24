import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer
import uuid

class IoTDataGenerator:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
    def generate_sensor_data(self):
        """Gera dados simulados de sensores IoT"""
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
        """Gera dados simulados de atividade de usuários"""
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
        """Inicia o streaming de dados"""
        print(f"Iniciando geração de dados para tópicos: {topic_sensors}, {topic_users}")
        
        try:
            while True:
                # Gera dados de sensores
                sensor_data = self.generate_sensor_data()
                self.producer.send(topic_sensors, sensor_data)
                
                # Gera dados de usuários (com menor frequência)
                if random.random() < 0.7:  # 70% de chance
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