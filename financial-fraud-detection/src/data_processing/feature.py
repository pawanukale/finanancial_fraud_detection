import pandas as pd
import numpy as np
from config.settings import DATA_PATHS

def engineer_features(df):
    # Time-based features
    df['transaction_hour'] = df['transaction_date'].dt.hour
    df['transaction_day'] = df['transaction_date'].dt.day
    df['transaction_dow'] = df['transaction_date'].dt.dayofweek  # Day of week
    df['transaction_month'] = df['transaction_date'].dt.month
    
    # Amount features
    df['log_amount'] = np.log1p(df['amount'])
    
    # User behavior features
    user_stats = df.groupby('user_id')['amount'].agg(['mean', 'std', 'count']).rename(
        columns={'mean': 'user_mean_amount', 'std': 'user_std_amount', 'count': 'user_transaction_count'})
    
    df = df.merge(user_stats, on='user_id', how='left')
    
    df['amount_zscore'] = (df['amount'] - df['user_mean_amount']) / df['user_std_amount'].replace(0, 1)
    df['amount_diff_from_mean'] = df['amount'] - df['user_mean_amount']
    
    # Merchant features
    merchant_stats = df.groupby('merchant_id')['amount'].agg(['mean', 'count']).rename(
        columns={'mean': 'merchant_mean_amount', 'count': 'merchant_transaction_count'})
    
    df = df.merge(merchant_stats, on='merchant_id', how='left')
    
    # Time since last transaction
    df = df.sort_values(['user_id', 'transaction_date'])
    df['time_since_last_txn'] = df.groupby('user_id')['transaction_date'].diff().dt.total_seconds() / 3600  # Hours
    
    # Rolling features (example)
    df['rolling_3day_amount'] = df.groupby('user_id')['amount'].rolling('3D', on='transaction_date').mean().reset_index(level=0, drop=True)
    
    return df

def process_features():
    # Load cleaned data
    df = pd.read_parquet(DATA_PATHS['processed'])
    
    # Engineer features
    df_with_features = engineer_features(df)
    
    # Save with features
    df_with_features.to_parquet(DATA_PATHS['processed'])
    
    return df_with_features

if __name__ == "__main__":
    print("Engineering features...")
    feature_data = process_features()
    print(f"Feature engineering complete. Added {len(feature_data.columns) - 12} new features.")  # Assuming original had 12 cols