import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from data_processor import DataProcessor

def train_regression():
    processor = DataProcessor()
    df = processor.load_credit_risk_data()
    df_processed = processor.preprocess_credit_risk(df)
    
    # We'll predict 'risk_score' based on other features
    X = df_processed.drop(['risk_score', 'loan_status'], axis=1)
    y = df_processed['risk_score']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Regression R2 Score: {r2_score(y_test, y_pred)}")
    print(f"Regression MSE: {mean_squared_error(y_test, y_pred)}")
    
    # Save the model and the processor
    if not os.path.exists("models"):
        os.makedirs("models")
    joblib.dump(model, "models/regression_model.pkl")
    joblib.dump(processor, "models/data_processor.pkl")
    return model

if __name__ == "__main__":
    train_regression()
