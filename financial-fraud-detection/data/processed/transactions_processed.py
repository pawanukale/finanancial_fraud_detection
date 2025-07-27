import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config.settings import DATA_PATHS

# Load raw data
df = pd.read_csv("financial-fraud-detection\data\raw\creditcard.csv")
print(f"Original shape: {df.shape}")
print(df['Class'].value_counts(normalize=True))

# Check missing values
print("\nMissing values:")
print(df.isnull().sum())