import joblib
import pandas as pd
import numpy as np

# Load models
# Assumes we run from the backend directory or pass absolute paths in app.py
try:
    rf_model = joblib.load('ml/model.pkl')
    iso_model = joblib.load('ml/anomaly_model.pkl')
except Exception as e:
    # Handle the case where predict is run directly from ml/ folder
    try:
        rf_model = joblib.load('model.pkl')
        iso_model = joblib.load('anomaly_model.pkl')
    except Exception as e2:
        rf_model = None
        iso_model = None
        print("Models not found. Ensure train_model.py has been run.")

def predict_threat(features):
    """
    Predicts the threat level based on given system features.
    features: list or dict of features:
    ['cpu_usage', 'ram_usage', 'disk_write_rate', 'file_modification_rate',
     'file_rename_rate', 'suspicious_extension_count', 'entropy_score', 'process_count']
    """
    if rf_model is None or iso_model is None:
        return {'status': 'error', 'message': 'Models not loaded'}

    # Ensure correct format
    if isinstance(features, dict):
        feature_list = [
            features.get('cpu_usage', 0),
            features.get('ram_usage', 0),
            features.get('disk_write_rate', 0),
            features.get('file_modification_rate', 0),
            features.get('file_rename_rate', 0),
            features.get('suspicious_extension_count', 0),
            features.get('entropy_score', 0),
            features.get('process_count', 0)
        ]
    else:
        feature_list = features

    # Reshape for prediction
    X = np.array(feature_list).reshape(1, -1)
    
    # Random Forest Prediction
    # 0: Safe, 1: Suspicious, 2: Ransomware
    rf_pred = rf_model.predict(X)[0]
    rf_prob = rf_model.predict_proba(X)[0]
    
    # Anomaly Detection (Isolation Forest)
    # 1: Normal, -1: Anomaly
    iso_pred = iso_model.predict(X)[0]
    
    # Calculate Threat Score (0-100)
    # Base score on Random Forest probabilities
    threat_score = (rf_prob[1] * 50) + (rf_prob[2] * 100)
    
    # If anomaly detected, bump up the score
    if iso_pred == -1:
        threat_score = min(100, threat_score + 20)
        
    status = "Safe"
    if threat_score >= 80 or rf_pred == 2:
        status = "Ransomware"
    elif threat_score >= 40 or rf_pred == 1 or iso_pred == -1:
        status = "Suspicious"
        
    return {
        'status': status,
        'threat_score': round(threat_score, 2),
        'rf_prediction': int(rf_pred),
        'is_anomaly': bool(iso_pred == -1),
        'probabilities': {
            'safe': round(rf_prob[0] * 100, 2),
            'suspicious': round(rf_prob[1] * 100, 2),
            'ransomware': round(rf_prob[2] * 100, 2)
        }
    }
