from confluent_kafka import Consumer, KafkaException
import json
import joblib
import pandas as pd
import numpy as np
from config.kafka_settings import KAFKA_CONFIG
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='fraud_detection.log'
)

logger = logging.getLogger(__name__)

class FraudDetectionConsumer:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_CONFIG['bootstrap_servers'],
            'group.id': KAFKA_CONFIG['consumer_group'],
            'auto.offset.reset': 'earliest'
        })
        self.transaction_topic = KAFKA_CONFIG['transaction_topic']
        self.fraud_topic = KAFKA_CONFIG['fraud_topic']
        self.producer = Producer({
            'bootstrap.servers': KAFKA_CONFIG['bootstrap_servers']
        })
        
        # Load trained model and preprocessing artifacts
        self.model = joblib.load('models/xgboost_tuned.pkl')
        self.scaler = joblib.load('models/scaler.pkl')
        self.feature_columns = joblib.load('models/feature_columns.pkl')
        
    def preprocess_transaction(self, transaction):
        """Convert raw transaction to model input features"""
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame([transaction])
        
        # Feature engineering (similar to batch processing)
        df['amount_log'] = np.log1p(df['amount'])
        df['hour_of_day'] = pd.to_datetime(df['timestamp'], unit='ms').dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp'], unit='ms').dt.dayofweek
        
        # One-hot encode categoricals
        df = pd.get_dummies(df, columns=['merchant_category', 'location'])
        
        # Ensure all expected columns are present
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Reorder columns to match training data
        df = df[self.feature_columns]
        
        # Scale numerical features
        df_scaled = self.scaler.transform(df)
        
        return df_scaled

    def detect_fraud(self, transaction):
        """Run fraud detection on transaction"""
        try:
            # Preprocess transaction
            features = self.preprocess_transaction(transaction)
            
            # Predict fraud probability
            fraud_prob = self.model.predict_proba(features)[0, 1]
            
            # Add prediction to transaction data
            transaction['fraud_probability'] = float(fraud_prob)
            transaction['is_fraud'] = bool(fraud_prob > 0.85)  # Threshold
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error processing transaction {transaction['transaction_id']}: {str(e)}")
            return None

    def process_transactions(self):
        """Consume and process transactions from Kafka"""
        self.consumer.subscribe([self.transaction_topic])
        
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                
                try:
                    transaction = json.loads(msg.value().decode('utf-8'))
                    logger.info(f"Processing transaction {transaction['transaction_id']}")
                    
                    # Detect fraud
                    processed_txn = self.detect_fraud(transaction)
                    
                    if processed_txn and processed_txn['is_fraud']:
                        # Send to fraud alerts topic
                        self.producer.produce(
                            topic=self.fraud_topic,
                            value=json.dumps(processed_txn),
                            key=str(processed_txn['transaction_id'])
                        logger.warning(f"Fraud detected in transaction {processed_txn['transaction_id']}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding message: {str(e)}")
                except KeyError as e:
                    logger.error(f"Missing field in transaction: {str(e)}")
                    
        except KeyboardInterrupt:
            logger.info("Shutting down consumer...")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    logger.info("Starting fraud detection consumer...")
    fraud_consumer = FraudDetectionConsumer()
    fraud_consumer.process_transactions()