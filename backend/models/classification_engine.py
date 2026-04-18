from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from data_processor import DataProcessor

def train_classification():
    processor = DataProcessor()
    df = processor.load_credit_risk_data()
    df_processed = processor.preprocess_credit_risk(df)
    
    # Predict 'loan_status'
    X = df_processed.drop(['loan_status', 'risk_score'], axis=1)
    y = df_processed['loan_status']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Classification Accuracy: {accuracy_score(y_test, y_pred)}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    if not os.path.exists("models"):
        os.makedirs("models")
    joblib.dump(model, "models/classification_model.pkl")
    return model

if __name__ == "__main__":
    train_classification()
