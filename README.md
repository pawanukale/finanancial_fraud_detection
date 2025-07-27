# Financial Fraud Detection System 💳🚨

![Fraud Detection Pipeline](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A real-time fraud detection system using machine learning with Kafka streaming and Flask dashboard.

## Features ✨

- **Data Pipeline**: Automated ETL processing
- **ML Models**: XGBoost, Isolation Forest, and Logistic Regression
- **Real-Time Processing**: Kafka-based transaction streaming
- **Alert System**: Email/SMS notifications
- **Dashboard**: Interactive monitoring UI

## Tech Stack 🛠️

| Component          | Technology               |
|--------------------|--------------------------|
| Backend            | Python 3.8+             |
| ML Framework       | Scikit-learn, XGBoost   |
| Streaming          | Apache Kafka            |
| Dashboard          | Flask + React           |
| Deployment         | Docker                  |

## Installation 🚀

### Prerequisites
- Python 3.8+
- Java 8+ (for Kafka)
- Docker (optional)

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/financial-fraud-detection.git
cd financial-fraud-detection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
