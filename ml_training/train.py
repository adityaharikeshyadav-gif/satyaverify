import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import glob
import random

MODELS_DIR = os.getenv("MODELS_DIR", "backend/models_ml")
os.makedirs(MODELS_DIR, exist_ok=True)

def generate_synthetic_data(n_samples=500):
    X = []
    y = []
    for _ in range(n_samples):
        if random.random() > 0.5:
            x = np.random.randn(512) * 0.8 + 0.2
            y.append(1)
        else:
            x = np.random.randn(512) * 0.3 + 0.1
            y.append(0)
    return np.array(X), np.array(y)

def train():
    print("Generating synthetic training data...")
    X, y = generate_synthetic_data(500)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train_scaled, y_train)
    rf_pred = rf.predict(X_test_scaled)
    print(f"Random Forest Accuracy: {accuracy_score(y_test, rf_pred):.2f}")

    print("Training XGBoost...")
    xgb = XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss')
    xgb.fit(X_train_scaled, y_train)
    xgb_pred = xgb.predict(X_test_scaled)
    print(f"XGBoost Accuracy: {accuracy_score(y_test, xgb_pred):.2f}")

    print("Training SVM...")
    svm = SVC(probability=True, kernel='rbf', random_state=42)
    svm.fit(X_train_scaled, y_train)
    svm_pred = svm.predict(X_test_scaled)
    print(f"SVM Accuracy: {accuracy_score(y_test, svm_pred):.2f}")

    print("\nClassification Report (XGBoost):")
    print(classification_report(y_test, xgb_pred, target_names=['REAL', 'FAKE']))

    joblib.dump(rf, os.path.join(MODELS_DIR, "rf_model.joblib"))
    joblib.dump(xgb, os.path.join(MODELS_DIR, "xgb_model.joblib"))
    joblib.dump(svm, os.path.join(MODELS_DIR, "svm_model.joblib"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.joblib"))
    print(f"\nModels saved to {MODELS_DIR}")

if __name__ == "__main__":
    train()
