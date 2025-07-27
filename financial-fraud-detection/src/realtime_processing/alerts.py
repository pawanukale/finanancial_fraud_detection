import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from confluent_kafka import Consumer
import json
import logging
from config.kafka_settings import KAFKA_CONFIG
from config.settings import ALERT_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='alert_system.log'
)

logger = logging.getLogger(__name__)

class FraudAlertManager:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_CONFIG['bootstrap_servers'],
            'group.id': 'fraud_alerts',
            'auto.offset.reset': 'earliest'
        })
        self.fraud_topic = KAFKA_CONFIG['fraud_topic']
        
        # Email configuration
        self.smtp_server = ALERT_CONFIG['smtp_server']
        self.smtp_port = ALERT_CONFIG['smtp_port']
        self.sender_email = ALERT_CONFIG['sender_email']
        self.sender_password = ALERT_CONFIG['sender_password']
        self.recipient_emails = ALERT_CONFIG['recipient_emails'].split(',')

    def send_email_alert(self, transaction):
        """Send email notification for fraud detection"""
        subject = f"🚨 Fraud Alert: Transaction {transaction['transaction_id']}"
        
        # Create HTML email content
        html = f"""
        <html>
            <body>
                <h2>High-Risk Transaction Detected</h2>
                <table border="1">
                    <tr><th>Transaction ID</th><td>{transaction['transaction_id']}</td></tr>
                    <tr><th>User ID</th><td>{transaction['user_id']}</td></tr>
                    <tr><th>Amount</th><td>${transaction['amount']:,.2f}</td></tr>
                    <tr><th>Merchant</th><td>{transaction['merchant_id']} ({transaction.get('merchant_category', 'N/A')})</td></tr>
                    <tr><th>Location</th><td>{transaction.get('location', 'N/A')}</td></tr>
                    <tr><th>Fraud Probability</th><td>{transaction['fraud_probability']:.1%}</td></tr>
                    <tr><th>Timestamp</th><td>{pd.to_datetime(transaction['timestamp'], unit='ms')}</td></tr>
                </table>
                <p>Immediate action is recommended.</p>
            </body>
        </html>
        """
        
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = ', '.join(self.recipient_emails)
        
        # Attach HTML content
        msg.attach(MIMEText(html, 'html'))
        
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email, 
                    self.recipient_emails, 
                    msg.as_string()
                )
            logger.info(f"Sent fraud alert for transaction {transaction['transaction_id']}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")

    def process_alerts(self):
        """Consume fraud alerts from Kafka and send notifications"""
        self.consumer.subscribe([self.fraud_topic])
        
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error(f"Kafka error: {msg.error()}")
                    continue
                
                try:
                    fraud_txn = json.loads(msg.value().decode('utf-8'))
                    logger.warning(f"Processing fraud alert for transaction {fraud_txn['transaction_id']}")
                    
                    # Send email alert
                    self.send_email_alert(fraud_txn)
                    
                    # TODO: Add other alert methods (SMS, webhook, etc.)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding message: {str(e)}")
                except KeyError as e:
                    logger.error(f"Missing field in transaction: {str(e)}")
                    
        except KeyboardInterrupt:
            logger.info("Shutting down alert manager...")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    logger.info("Starting fraud alert manager...")
    alert_manager = FraudAlertManager()
    alert_manager.process_alerts()
    