import pandas as pd
import os
import sys

# Ensure stdout uses utf-8
sys.stdout.reconfigure(encoding='utf-8')

def inspect_dataset(filename):
    print(f"\n{'='*20} {filename} {'='*20}")
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filename)
        elif filename.endswith('.xlsx'):
            xl = pd.ExcelFile(filename)
            print(f"Sheets: {xl.sheet_names}")
            # Try to read the first non-empty sheet or the one named 'Data'
            sheet_name = 'Data' if 'Data' in xl.sheet_names else xl.sheet_names[0]
            df = pd.read_excel(filename, sheet_name=sheet_name)
        else:
            print(f"Unsupported file type: {filename}")
            return

        print(f"Shape: {df.shape}")
        print("\nColumns:")
        print(df.columns.tolist())
        print("\nData Types:")
        print(df.dtypes)
        print("\nFirst 5 rows:")
        print(df.head())
        
        # Check for target candidates
        if 'loan_status' in df.columns:
            print("\nValue counts for loan_status (Classification target):")
            print(df['loan_status'].value_counts())
        
        # For financial_dataset.csv, check Score
        if 'Score' in df.columns:
            print("\nStats for Score (Regression candidate):")
            print(df['Score'].describe())

    except Exception as e:
        print(f"Error reading {filename}: {e}")

datasets = ['credit_risk_dataset.csv', 'financial_dataset.csv', 'esgdata_download-2026-01-09.xlsx']
for ds in datasets:
    if os.path.exists(ds):
        inspect_dataset(ds)
    else:
        print(f"File not found: {ds}")
