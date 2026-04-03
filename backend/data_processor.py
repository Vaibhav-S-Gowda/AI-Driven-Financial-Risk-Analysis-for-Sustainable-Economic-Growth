import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler

class DataProcessor:
    def __init__(self, base_path=None):
        self.base_path = base_path if base_path is not None else os.path.join(os.path.dirname(__file__), '..', 'data')
        self.label_encoders = {}
        self.scaler = StandardScaler()

    def load_credit_risk_data(self):
        df = pd.read_csv(os.path.join(self.base_path, "credit_risk_dataset.csv"))
        # Fill missing values
        df['person_emp_length'] = df['person_emp_length'].fillna(df['person_emp_length'].median())
        df['loan_int_rate'] = df['loan_int_rate'].fillna(df['loan_int_rate'].median())
        
        # Simple Risk Score: weighted average of interest rate and debt ratio
        df['risk_score'] = (df['loan_int_rate'] * 0.6) + (df['loan_percent_income'] * 40)
        return df

    def preprocess_credit_risk(self, df, training=True):
        categorical_cols = ['person_home_ownership', 'loan_intent', 'loan_grade', 'cb_person_default_on_file']
        df_processed = df.copy()
        
        for col in categorical_cols:
            if training:
                le = LabelEncoder()
                df_processed[col] = le.fit_transform(df_processed[col].astype(str))
                self.label_encoders[col] = le
            else:
                le = self.label_encoders.get(col)
                if le:
                    # Handle unseen labels by mapping them to the first known label or a default
                    df_processed[col] = df_processed[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else 0)
        
        return df_processed

    def load_financial_data(self):
        df = pd.read_csv(os.path.join(self.base_path, "financial_dataset.csv"))
        return df

    def load_esg_data(self):
        file_path = os.path.join(self.base_path, "esgdata_download-2026-01-09.xlsx")
        xl = pd.ExcelFile(file_path)
        sheet_name = 'Data' if 'Data' in xl.sheet_names else xl.sheet_names[0]
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Melt year columns into a single 'Year' column
        year_cols = [col for col in df.columns if col.isdigit()]
        id_vars = [col for col in df.columns if not col.isdigit()]
        
        df_melted = df.melt(id_vars=id_vars, value_vars=year_cols, var_name='Year', value_name='Value')
        df_melted['Year'] = df_melted['Year'].astype(int)
        df_melted = df_melted.dropna(subset=['Value'])
        return df_melted

if __name__ == "__main__":
    processor = DataProcessor()
    
    print("Processing Credit Risk Data...")
    credit_df = processor.load_credit_risk_data()
    credit_processed = processor.preprocess_credit_risk(credit_df)
    print(f"Credit processed shape: {credit_processed.shape}")
    
    print("\nProcessing Financial Data...")
    fin_df = processor.load_financial_data()
    print(f"Financial data shape: {fin_df.shape}")
    
    print("\nProcessing ESG Data...")
    esg_df = processor.load_esg_data()
    print(f"ESG melted data shape: {esg_df.shape}")
    print(esg_df.head())
