import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os
from data_processor import DataProcessor

def train_clustering():
    processor = DataProcessor()
    df = processor.load_financial_data()
    
    # Use financial markers for clustering
    features = ['Income', 'Credit Score', 'Spending Score', 'Transaction Count', 'Savings Ratio']
    X = df[features]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Segment into 4 clusters: Low risk/High income, High risk/Low income, etc.
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    df['Cluster'] = clusters
    
    # Save model and scaler
    if not os.path.exists("models"):
        os.makedirs("models")
    joblib.dump(kmeans, "models/clustering_model.pkl")
    joblib.dump(scaler, "models/clustering_scaler.pkl")
    
    print("Clustering complete. Model saved.")
    print(f"Cluster summary:\n{df.groupby('Cluster').mean(numeric_only=True)}")
    return kmeans

if __name__ == "__main__":
    train_clustering()
