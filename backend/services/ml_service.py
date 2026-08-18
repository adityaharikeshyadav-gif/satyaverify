import os
import json
import tempfile
from pathlib import Path
import numpy as np
from typing import Dict, Any, List, Optional

try:
    import cv2
except Exception:
    cv2 = None
try:
    import librosa
except Exception:
    librosa = None
try:
    from skimage.feature import hog, local_binary_pattern
except Exception:
    hog = None
    local_binary_pattern = None
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
except Exception:
    RandomForestClassifier = None
    SVC = None
    StandardScaler = None
try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None
try:
    import joblib
except Exception:
    joblib = None

_BACKEND_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = Path(os.getenv("MODELS_DIR", _BACKEND_DIR / "models_ml"))
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATHS = {
    "random_forest": MODELS_DIR / "rf_model.joblib",
    "xgboost": MODELS_DIR / "xgb_model.joblib",
    "svm": MODELS_DIR / "svm_model.joblib",
    "scaler": MODELS_DIR / "scaler.joblib"
}

def extract_hog(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    gray = cv2.resize(gray, (128, 128))
    features = hog(gray, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), visualize=False)
    return features

def extract_lbp(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    gray = cv2.resize(gray, (128, 128))
    lbp = local_binary_pattern(gray, P=8, R=1, method="uniform")
    hist, _ = np.histogram(lbp.ravel(), bins=10, range=(0, 10), density=True)
    return hist

def extract_color_features(image: np.ndarray) -> np.ndarray:
    image = cv2.resize(image, (128, 128))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h_hist = cv2.calcHist([hsv], [0], None, [16], [0, 180]).flatten()
    s_hist = cv2.calcHist([hsv], [1], None, [16], [0, 256]).flatten()
    v_hist = cv2.calcHist([hsv], [2], None, [16], [0, 256]).flatten()
    return np.concatenate([h_hist, s_hist, v_hist])

def extract_freq_features(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    gray = cv2.resize(gray, (128, 128))
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude = np.abs(fshift)
    feat = cv2.resize(magnitude, (16, 16)).flatten()
    return feat

def extract_audio_features(audio_path: str) -> np.ndarray:
    try:
        y, sr = librosa.load(audio_path, sr=None)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
        sc_mean = np.mean(spectral_centroids)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        sr_mean = np.mean(spectral_rolloff)
        zero_crossing = librosa.feature.zero_crossing_rate(y)
        zcr_mean = np.mean(zero_crossing)
        return np.concatenate([mfcc_mean, [sc_mean, sr_mean, zcr_mean]])
    except Exception:
        return np.zeros(16)

def extract_video_features(video_path: str, max_frames: int = 10) -> Dict[str, Any]:
    cap = cv2.VideoCapture(video_path)
    frames = []
    suspicious_frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = np.linspace(0, max(1, total_frames - 1), min(max_frames, total_frames), dtype=int)
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if not ret:
            continue
        hog_f = extract_hog(frame)
        lbp_f = extract_lbp(frame)
        color_f = extract_color_features(frame)
        freq_f = extract_freq_features(frame)
        feat = np.concatenate([hog_f, lbp_f, color_f, freq_f])
        frames.append({
            "frame_number": int(idx),
            "timestamp": round(float(idx) / max(1, total_frames), 3),
            "features": feat.tolist()
        })
    cap.release()
    return {"frames": frames, "total_frames": total_frames}

def extract_image_features(image_path: str) -> np.ndarray:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not read image")
    hog_f = extract_hog(image)
    lbp_f = extract_lbp(image)
    color_f = extract_color_features(image)
    freq_f = extract_freq_features(image)
    return np.concatenate([hog_f, lbp_f, color_f, freq_f])

def load_models():
    models = {}
    scaler = None
    if os.path.exists(MODEL_PATHS["scaler"]):
        scaler = joblib.load(MODEL_PATHS["scaler"])
    for name, path in MODEL_PATHS.items():
        if name == "scaler":
            continue
        if os.path.exists(path):
            models[name] = joblib.load(path)
    return models, scaler

def predict_with_ensemble(features: np.ndarray, models: Dict[str, Any], scaler: Optional[Any]) -> Dict[str, Any]:
    if not models or scaler is None:
        return {
            "prediction": "UNVERIFIED",
            "confidence": 0.5,
            "model_scores": {},
            "features": {}
        }
    X = scaler.transform(features.reshape(1, -1))
    scores = {}
    for name, model in models.items():
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X)[0]
                scores[name] = float(proba[1]) if len(proba) > 1 else float(proba[0])
            else:
                pred = model.predict(X)[0]
                scores[name] = float(pred)
        except Exception:
            scores[name] = 0.5
    valid_scores = [v for v in scores.values() if isinstance(v, float)]
    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.5
    prediction = "MANIPULATED" if avg_score > 0.7 else "SUSPICIOUS" if avg_score > 0.4 else "VERIFIED"
    return {
        "prediction": prediction,
        "confidence": round(avg_score * 100, 2),
        "model_scores": {k: round(v * 100, 2) for k, v in scores.items()},
        "features": {
            "feature_count": int(features.shape[0]),
            "mean": round(float(np.mean(features)), 4),
            "std": round(float(np.std(features)), 4)
        }
    }

def analyze_media(file_path: str, media_type: str, content: bytes) -> Dict[str, Any]:
    metadata = {"size": len(content), "path": file_path}
    if media_type == "image":
        try:
            features = extract_image_features(file_path)
            metadata["type"] = "image"
        except Exception as e:
            return {"prediction": "ERROR", "confidence": 0.0, "error": str(e), "metadata": metadata}
    elif media_type == "video":
        try:
            video_data = extract_video_features(file_path)
            metadata["type"] = "video"
            metadata["total_frames"] = video_data["total_frames"]
            frame_features = [f["features"] for f in video_data["frames"]]
            if frame_features:
                features = np.mean(frame_features, axis=0)
                suspicious_frames = []
                models, scaler = load_models()
                for f in video_data["frames"]:
                    fvec = np.array(f["features"])
                    result = predict_with_ensemble(fvec, models, scaler)
                    if result["prediction"] in ("SUSPICIOUS", "MANIPULATED"):
                        suspicious_frames.append({
                            "frame_number": f["frame_number"],
                            "timestamp": f["timestamp"],
                            "prediction": result["prediction"],
                            "confidence": result["confidence"]
                        })
            else:
                features = np.zeros(512)
                suspicious_frames = []
        except Exception as e:
            return {"prediction": "ERROR", "confidence": 0.0, "error": str(e), "metadata": metadata}
    elif media_type == "audio":
        try:
            audio_feat = extract_audio_features(file_path)
            features = audio_feat
            metadata["type"] = "audio"
            suspicious_frames = []
        except Exception as e:
            return {"prediction": "ERROR", "confidence": 0.0, "error": str(e), "metadata": metadata}
    else:
        return {"prediction": "UNSUPPORTED", "confidence": 0.0, "metadata": metadata}
    models, scaler = load_models()
    if not models:
        return {
            "prediction": "UNVERIFIED",
            "confidence": 50.0,
            "model_scores": {},
            "suspicious_frames": [],
            "features": {"note": "Models not trained. Run python ml_training/train.py"},
            "metadata": metadata
        }
    result = predict_with_ensemble(features, models, scaler)
    result["metadata"] = metadata
    if media_type == "video" and 'suspicious_frames' in locals():
        result["suspicious_frames"] = suspicious_frames
    elif media_type != "video":
        result["suspicious_frames"] = []
    return result
