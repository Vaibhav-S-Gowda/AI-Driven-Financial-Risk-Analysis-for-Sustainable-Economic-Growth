import pandas as pd
import os

def inspect_dataset(filename):
    lines = []
    lines.append(f"\n{'='*20} {filename} {'='*20}")
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filename)
        elif filename.endswith('.xlsx'):
            xl = pd.ExcelFile(filename)
            lines.append(f"Sheets: {xl.sheet_names}")
            # Try to read the first non-empty sheet or the one named 'Data'
            sheet_name = 'Data' if 'Data' in xl.sheet_names else xl.sheet_names[0]
            df = pd.read_excel(filename, sheet_name=sheet_name)
        else:
            lines.append(f"Unsupported file type: {filename}")
            return "\n".join(lines)

        lines.append(f"Shape: {df.shape}")
        lines.append("\nColumns:")
        lines.append(str(df.columns.tolist()))
        lines.append("\nData Types:")
        lines.append(str(df.dtypes))
        lines.append("\nFirst 5 rows:")
        lines.append(str(df.head()))
        
        # Check for target candidates
        if 'loan_status' in df.columns:
            lines.append("\nValue counts for loan_status (Classification target):")
            lines.append(str(df['loan_status'].value_counts()))
        
        # For financial_dataset.csv, check Score
        if 'Score' in df.columns:
            lines.append("\nStats for Score (Regression candidate):")
            lines.append(str(df['Score'].describe()))

    except Exception as e:
        lines.append(f"Error reading {filename}: {e}")
    
    return "\n".join(lines)

datasets = ['../data/credit_risk_dataset.csv', '../data/financial_dataset.csv', '../data/esgdata_download-2026-01-09.xlsx']
full_report = []
for ds in datasets:
    if os.path.exists(ds):
        full_report.append(inspect_dataset(ds))
    else:
        full_report.append(f"File not found: {ds}")

with open("../reports/full_inspection_report_v3.txt", "w", encoding='utf-8') as f:
    f.write("\n".join(full_report))
