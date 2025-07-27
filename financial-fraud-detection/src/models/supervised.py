import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score, average_precision_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import joblib
import scikitplot as skplt
import matplotlib.pyplot as plt
from config.settings import DATA_PATHS

def evaluate_model(model, X_test, y_test, name):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    print(f"\n{name} Evaluation:")
    print(f"ROC AUC: {roc_auc_score(y_test, y_proba):.4f}")
    print(f"PR AUC: {average_precision_score(y_test, y_proba):.4f}")
    
    # Plot important metrics
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 2, 1)
    skplt.metrics.plot_roc(y_test, model.predict_proba(X_test))
    plt.title(f'{name} ROC Curve')
    
    plt.subplot(1, 2, 2)
    skplt.metrics.plot_precision_recall(y_test, model.predict_proba(X_test))
    plt.title(f'{name} Precision-Recall Curve')
    
    plt.tight_layout()
    plt.show()
    
    return {
        'model': name,
        'roc_auc': roc_auc_score(y_test, y_proba),
        'pr_auc': average_precision_score(y_test, y_proba)
    }

def train_supervised_models():
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Define models
    models = {
        'XGBoost': XGBClassifier(
            scale_pos_weight=len(y_train[y_train==0])/len(y_train[y_train==1]),
            eval_metric='aucpr',
            n_jobs=-1,
            random_state=42
        ),
        'LightGBM': LGBMClassifier(
            is_unbalance=True,
            metric='average_precision',
            n_jobs=-1,
            random_state=42
        ),
        'Logistic Regression': Pipeline([
            ('smote', SMOTE(random_state=42)),
            ('scaler', StandardScaler()),
            ('lr', LogisticRegression(
                class_weight='balanced',
                max_iter=1000,
                n_jobs=-1,
                random_state=42
            ))
        ])
    }
    
    results = []
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        joblib.dump(model, f'models/{name.lower().replace(" ", "_")}.pkl')
        results.append(evaluate_model(model, X_test, y_test, name))
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    print("Training supervised models...")
    results_df = train_supervised_models()
    print("\nModel Comparison:")
    print(results_df)