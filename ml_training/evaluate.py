import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np

MODELS_DIR = os.getenv("MODELS_DIR", "backend/models_ml")

def evaluate():
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    import random
    random.seed(42)
    np.random.seed(42)

    X = np.vstack([np.random.randn(250, 512) * 0.8 + 0.2, np.random.randn(250, 512) * 0.3 + 0.1])
    y = np.array([1]*250 + [0]*250)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.joblib"))
    X_test_scaled = scaler.transform(X_test)

    for name in ["rf_model.joblib", "xgb_model.joblib", "svm_model.joblib"]:
        model = joblib.load(os.path.join(MODELS_DIR, name))
        preds = model.predict(X_test_scaled)
        print(f"\n{name}: Accuracy={accuracy_score(y_test, preds):.2f}")
        print(confusion_matrix(y_test, preds))

if __name__ == "__main__":
    evaluate()
