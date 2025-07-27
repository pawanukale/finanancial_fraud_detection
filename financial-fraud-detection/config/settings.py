import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '3306'),  # MySQL default port
    'user': os.getenv('DB_USER', 'root'),  # Common MySQL default user
    'password': os.getenv('DB_PASSWORD', '#Pawan3108'),
    'database': os.getenv('DB_NAME', 'fraud_detection'),
    'charset': 'utf8mb4',  # Important for MySQL
    'autocommit': True  # Often needed for MySQL
}

DATA_PATHS = {
    'raw': 'data/raw/transactions.csv',
    'processed': 'data/processed/transactions_processed.parquet'
}