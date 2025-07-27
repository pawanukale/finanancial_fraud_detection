from confluent_kafka import Producer
import json
import time
import random
from config.kafka_settings import KAFKA_CONFIG
from config.settings import DATA_PATHS

class TransactionProducer:
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': KAFKA_CONFIG['bootstrap_servers']
        })
        self.transaction_topic = KAFKA_CONFIG['transaction_topic']
        
    def delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def generate_mock_transaction(self):
        """Generate a mock transaction for testing"""
        return {
            'transaction_id': str(random.randint(100000, 999999)),
            'user_id': f"user_{random.randint(1, 1000)}",
            'amount': round(random.uniform(1, 10000), 2),
            'merchant_id': f"merchant_{random.randint(1, 50)}",
            'merchant_category': random.choice(['retail', 'travel', 'food', 'entertainment']),
            'location': random.choice(['US', 'UK', 'CA', 'AU', 'JP']),
            'timestamp': int(time.time() * 1000)
        }

    def produce_transactions(self, num_messages=100, delay=0.1):
        """Produce mock transactions to Kafka"""
        for _ in range(num_messages):
            transaction = self.generate_mock_transaction()
            self.producer.produce(
                topic=self.transaction_topic,
                value=json.dumps(transaction),
                callback=self.delivery_report
            )
            time.sleep(delay)
        
        self.producer.flush()

if __name__ == "__main__":
    producer = TransactionProducer()
    print("Producing test transactions to Kafka...")
    producer.produce_transactions(num_messages=1000, delay=0.05)
    