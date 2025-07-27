
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
from sklearn.preprocessing import StandardScaler
from imblearn.under_sampling import RandomUnderSampler
import joblib
from config.settings import DATA_PATHS

def load_data():
    df = pd.read_parquet(DATA_PATHS['processed'])
    
    # Assuming we have a 'is_fraud' column (1 for fraud, 0 for legitimate)
    X = df.drop(columns=['is_fraud', 'transaction_id', 'transaction_date'])
    y = df['is_fraud']
    
    # Convert categoricals (simple one-hot for baseline)
    X = pd.get_dummies(X, columns=['merchant_category', 'country', 'gender'])
    
    return X, y

def train_baseline_model():
    X, y = load_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y)
    
    # Handle class imbalance
    rus = RandomUnderSampler(random_state=42)
    X_train_res, y_train_res = rus.fit_resample(X_train, y_train)
    
    # Scale numerical features
    scaler = StandardScaler()
    X_train_res = scaler.fit_transform(X_train_res)
    X_test = scaler.transform(X_test)
    
    # Train Random Forest baseline
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    
    model.fit(X_train_res, y_train_res)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    print("Baseline Model Evaluation:")
    print(classification_report(y_test, y_pred))
    print(f"ROC AUC: {roc_auc_score(y_test, y_proba):.4f}")
    print(f"PR AUC: {average_precision_score(y_test, y_proba):.4f}")
    
    # Save artifacts
    joblib.dump(model, 'models/baseline_rf.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    
    return model

if __name__ == "__main__":
    print("Training baseline model...")
    model = train_baseline_model()
    print("Baseline model training complete!")