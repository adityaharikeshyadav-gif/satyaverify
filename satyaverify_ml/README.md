# SATYAVERIFY ML - Deepfake Detection Pipeline

Production-quality traditional ML pipeline for deepfake detection using handcrafted visual, frequency, audio, and metadata features.

## Setup
`ash
pip install -r requirements.txt
`

## Training
`ash
python satyaverify_ml/main.py
`

## Inference API
`ash
uvicorn satyaverify_ml.api.main:app --host 0.0.0.0 --port 8000
`

POST to /analyze with image, ideo, or udio file.

## Models
- Random Forest, XGBoost, SVM, Hybrid Ensemble
- Trained with leak-free source-based splitting