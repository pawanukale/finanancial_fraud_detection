import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_CONFIG = {
    'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'transaction_topic': os.getenv('KAFKA_TRANSACTION_TOPIC', 'transactions'),
    'fraud_topic': os.getenv('KAFKA_FRAUD_TOPIC', 'fraud_alerts'),
    'consumer_group': os.getenv('KAFKA_CONSUMER_GROUP', 'fraud_detection')
}