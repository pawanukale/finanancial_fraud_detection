from flask import Flask, jsonify, request
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config.settings import DATA_PATHS
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load model and data
model = joblib.load('models/xgboost_tuned.pkl')
scaler = joblib.load('models/scaler.pkl')
feature_columns = joblib.load('models/feature_columns.pkl')

# In-memory storage for demo (replace with database in production)
fraud_alerts = []
transaction_stats = {
    'total_count': 0,
    'fraud_count': 0,
    'total_amount': 0,
    'fraud_amount': 0
}

@app.route('/api/detect', methods=['POST'])
def detect_fraud():
    """API endpoint for single transaction fraud detection"""
    try:
        transaction = request.json
        
        # Preprocess transaction
        df = pd.DataFrame([transaction])
        df['amount_log'] = np.log1p(df['amount'])
        df['hour_of_day'] = pd.to_datetime(df['timestamp'], unit='ms').dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp'], unit='ms').dt.dayofweek
        df = pd.get_dummies(df, columns=['merchant_category', 'location'])
        
        # Ensure all expected columns
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0
        df = df[feature_columns]
        
        # Scale and predict
        features = scaler.transform(df)
        fraud_prob = model.predict_proba(features)[0, 1]
        
        # Update stats
        transaction_stats['total_count'] += 1
        transaction_stats['total_amount'] += transaction['amount']
        if fraud_prob > 0.85:
            transaction_stats['fraud_count'] += 1
            transaction_stats['fraud_amount'] += transaction['amount']
            fraud_alerts.append({
                **transaction,
                'fraud_probability': float(fraud_prob),
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'transaction_id': transaction['transaction_id'],
            'fraud_probability': float(fraud_prob),
            'is_fraud': bool(fraud_prob > 0.85)
        })
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get summary statistics"""
    return jsonify({
        'stats': transaction_stats,
        'fraud_rate': (transaction_stats['fraud_count'] / transaction_stats['total_count']) if transaction_stats['total_count'] > 0 else 0,
        'avg_fraud_amount': (transaction_stats['fraud_amount'] / transaction_stats['fraud_count']) if transaction_stats['fraud_count'] > 0 else 0
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get recent fraud alerts"""
    limit = int(request.args.get('limit', 10))
    return jsonify({
        'alerts': sorted(fraud_alerts, key=lambda x: x['timestamp'], reverse=True)[:limit]
    })

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Get fraud trends over time"""
    # In a real system, query from database
    now = datetime.now()
    days = int(request.args.get('days', 7))
    
    # Mock data for demo
    trends = []
    for i in range(days):
        date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
        trends.append({
            'date': date,
            'total': random.randint(800, 1200),
            'fraud': random.randint(5, 20)
        })
    
    return jsonify({'trends': trends})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)