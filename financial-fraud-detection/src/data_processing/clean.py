import pandas as pd
import numpy as np
from config.settings import DATA_PATHS

def clean_data(df):
    # Convert dates
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Handle missing values
    df['amount'] = df['amount'].fillna(df['amount'].median())
    df['credit_score'] = df['credit_score'].fillna(df.groupby('age')['credit_score'].transform('median'))
    df['city'] = df['city'].fillna('Unknown')
    
    # Remove impossible values
    df = df[df['amount'] > 0]
    df = df[df['amount'] < 1000000]  # Assuming $1M is max transaction
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['transaction_id'], keep='first')
    
    return df

def load_and_clean():
    # Load raw data
    df = pd.read_csv(DATA_PATHS['raw'])
    
    # Clean data
    cleaned_df = clean_data(df)
    
    # Save cleaned data
    cleaned_df.to_parquet(DATA_PATHS['processed'])
    
    return cleaned_df

if __name__ == "__main__":
    print("Cleaning transaction data...")
    cleaned_data = load_and_clean()
    print(f"Cleaning complete. Processed {len(cleaned_data)} transactions.")