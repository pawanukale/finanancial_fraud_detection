import optuna
from sklearn.model_selection import cross_val_score
from xgboost import XGBClassifier
from sklearn.metrics import make_scorer, average_precision_score
import joblib
from config.settings import DATA_PATHS

def load_tuning_data():
    df = pd.read_parquet(DATA_PATHS['processed'])
    X = df.drop(columns=['is_fraud', 'transaction_id', 'transaction_date'])
    y = df['is_fraud']
    X = pd.get_dummies(X, columns=['merchant_category', 'country', 'gender'])
    return X, y

def objective(trial):
    X, y = load_tuning_data()
    
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 500),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'gamma': trial.suggest_float('gamma', 0, 1),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'scale_pos_weight': trial.suggest_float('scale_pos_weight', 1, 100),
        'reg_alpha': trial.suggest_float('reg_alpha', 0, 10),
        'reg_lambda': trial.suggest_float('reg_lambda', 0, 10),
    }
    
    model = XGBClassifier(
        **params,
        eval_metric='aucpr',
        n_jobs=-1,
        random_state=42,
        tree_method='hist'
    )
    
    scorer = make_scorer(average_precision_score, needs_proba=True)
    score = cross_val_score(
        model, X, y, cv=StratifiedKFold(n_splits=3), 
        scoring=scorer, n_jobs=-1
    ).mean()
    
    return score

def optimize_xgboost():
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=50, timeout=3600)  # 1 hour timeout
    
    print("Best trial:")
    trial = study.best_trial
    print(f"  PR AUC: {trial.value:.4f}")
    print("  Params: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")
    
    # Train final model with best params
    X, y = load_tuning_data()
    best_model = XGBClassifier(
        **trial.params,
        eval_metric='aucpr',
        n_jobs=-1,
        random_state=42
    )
    best_model.fit(X, y)
    joblib.dump(best_model, 'models/xgboost_tuned.pkl')
    
    return best_model

if __name__ == "__main__":
    print("Optimizing XGBoost model...")
    best_model = optimize_xgboost()
    print("Optimization complete!")