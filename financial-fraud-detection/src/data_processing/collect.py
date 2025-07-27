import pandas as pd
from sqlalchemy import create_engine
from config.settings import DATABASE_CONFIG, DATA_PATHS

def collect_data():
    # Database connection
    conn_string = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
    engine = create_engine(conn_string)
    
    # Sample query - modify based on your schema
    query = """
    SELECT 
        t.transaction_id, t.amount, t.transaction_date,
        u.user_id, u.age, u.gender, u.credit_score,
        m.merchant_id, m.merchant_category,
        l.location_id, l.country, l.city
    FROM transactions t
    JOIN users u ON t.user_id = u.user_id
    JOIN merchants m ON t.merchant_id = m.merchant_id
    JOIN locations l ON t.location_id = l.location_id
    WHERE t.transaction_date BETWEEN '2023-01-01' AND '2023-12-31'
    """
    
    # Load data
    df = pd.read_sql(query, engine)
    
    # Save raw data
    df.to_csv(DATA_PATHS['raw'], index=False)
    
    return df

if __name__ == "__main__":
    print("Collecting data from database...")
    data = collect_data()
    print(f"Collected {len(data)} transactions. Saved to {DATA_PATHS['raw']}")