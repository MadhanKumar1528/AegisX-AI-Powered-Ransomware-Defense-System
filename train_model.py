import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

def train_models(data_path='dataset.csv', model_path='model.pkl', anomaly_model_path='anomaly_model.pkl'):
    """Trains the Random Forest and Isolation Forest models."""
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run generate_dataset.py first.")
        return

    print("Loading dataset...")
    df = pd.read_csv(data_path)
    
    # Features and labels
    X = df.drop('label', axis=1)
    y = df['label']
    
    # Split for classification model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # --- 1. Train Random Forest Classifier ---
    print("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = rf_model.predict(X_test)
    print("\nRandom Forest Evaluation:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred))
    
    # Save RF model
    joblib.dump(rf_model, model_path)
    print(f"Random Forest model saved to {model_path}")
    
    # --- 2. Train Isolation Forest (Anomaly Detection) ---
    print("\nTraining Isolation Forest (Anomaly Detection)...")
    # Train Isolation forest only on 'Safe' data to learn normal behavior
    X_safe = df[df['label'] == 0].drop('label', axis=1)
    
    # Contamination defines the expected proportion of outliers.
    iso_model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    iso_model.fit(X_safe)
    
    # Save Anomaly model
    joblib.dump(iso_model, anomaly_model_path)
    print(f"Isolation Forest model saved to {anomaly_model_path}")

if __name__ == '__main__':
    train_models()
