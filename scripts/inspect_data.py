import pandas as pd
import os

def inspect_dataset(filename):
    print(f"\n{'='*20} {filename} {'='*20}")
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filename)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(filename)
        else:
            print(f"Unsupported file type: {filename}")
            return

        print(f"Shape: {df.shape}")
        print("\nColumns:")
        print(df.columns.tolist())
        print("\nData Types:")
        print(df.dtypes)
        print("\nMissing Values:")
        print(df.isnull().sum())
        print("\nFirst 5 rows:")
        print(df.head())
        
        # Basic stats for numerical columns
        print("\nNumerical Summary:")
        print(df.describe())
        
    except Exception as e:
        print(f"Error reading {filename}: {e}")

datasets = ['../data/credit_risk_dataset.csv', '../data/financial_dataset.csv', '../data/esgdata_download-2026-01-09.xlsx']
for ds in datasets:
    if os.path.exists(ds):
        inspect_dataset(ds)
    else:
        print(f"File not found: {ds}")
