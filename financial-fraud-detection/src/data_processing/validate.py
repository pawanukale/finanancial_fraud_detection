import pandas as pd
from config.settings import DATA_PATHS

def validate_data():
    df = pd.read_parquet(DATA_PATHS['processed'])
    
    validation_results = {
        'total_records': len(df),
        'missing_values': df.isnull().sum().to_dict(),
        'negative_amounts': len(df[df['amount'] < 0]),
        'duplicate_transactions': len(df[df.duplicated(subset=['transaction_id'])]),
        'data_range': {
            'min_date': df['transaction_date'].min(),
            'max_date': df['transaction_date'].max()
        }
    }
    
    return validation_results

if __name__ == "__main__":
    results = validate_data()
    print("Data Validation Results:")
    for k, v in results.items():
        print(f"{k}: {v}")
        