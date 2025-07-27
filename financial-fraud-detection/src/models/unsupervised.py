import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
from config.settings import DATA_PATHS

def prepare_anomaly_data():
    df = pd.read_parquet(DATA_PATHS['processed'])
    
    # Use only legitimate transactions for training
    X_train = df[df['is_fraud'] == 0].drop(
        columns=['is_fraud', 'transaction_id', 'transaction_date'])
    
    # Prepare test set (mix of fraud and legitimate)
    X_test = df.drop(columns=['is_fraud', 'transaction_id', 'transaction_date'])
    y_test = df['is_fraud']
    
    # One-hot encode categoricals
    X_train = pd.get_dummies(X_train, columns=['merchant_category', 'country', 'gender'])
    X_test = pd.get_dummies(X_test, columns=['merchant_category', 'country', 'gender'])
    
    # Ensure same columns
    X_test = X_test.reindex(columns=X_train.columns, fill_value=0)
    
    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    return X_train, X_test, y_test

def train_anomaly_models():
    X_train, X_test, y_test = prepare_anomaly_data()
    
    models = {
        'IsolationForest': IsolationForest(
            n_estimators=200,
            contamination='auto',
            random_state=42,
            n_jobs=-1
        ),
        'OneClassSVM': OneClassSVM(
            nu=0.05,  # Expected outlier fraction
            kernel='rbf',
            gamma='scale'
        ),
        'LocalOutlierFactor': LocalOutlierFactor(
            n_neighbors=20,
            contamination='auto',
            novelty=True,
            n_jobs=-1
        )
    }
    
    results = []
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        if name != 'LocalOutlierFactor':
            model.fit(X_train)
        
        # Get anomaly scores (higher = more anomalous)
        if name == 'OneClassSVM':
            scores = -model.decision_function(X_test)  # SVM returns distances
        elif name == 'LocalOutlierFactor':
            scores = -model.fit(X_train).decision_function(X_test)
        else:
            scores = -model.score_samples(X_test)  # Isolation Forest returns negative
        
        # Evaluate
        auc = roc_auc_score(y_test, scores)
        print(f"{name} ROC AUC: {auc:.4f}")
        
        # Save model
        joblib.dump(model, f'models/{name.lower()}.pkl')
        results.append({'model': name, 'roc_auc': auc})
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    print("Training anomaly detection models...")
    anomaly_results = train_anomaly_models()
    print("\nAnomaly Detection Performance:")
    print(anomaly_results)

