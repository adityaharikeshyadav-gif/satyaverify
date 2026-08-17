import os
import sys
import logging
from pathlib import Path
import numpy as np
import cv2
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from satyaverify_ml.preprocessing import PreprocessingPipeline, features_to_arrays
from satyaverify_ml.models.random_forest import RandomForestModel
from satyaverify_ml.models.xgboost_model import XGBoostModel
from satyaverify_ml.models.svm_model import SVMModel
from satyaverify_ml.models.ensemble import HybridEnsemble
from satyaverify_ml.config import cfg
from .face_utils import detect_and_crop_face

logger = logging.getLogger(__name__)

class DeepfakePredictor:
    def __init__(self, models_dir='satyaverify_ml/models/artifacts'):
        self.models_dir = Path(models_dir)
        self.pipeline = PreprocessingPipeline()
        self.pipeline.load(models_dir)
        self.models = {}
        for name in ['random_forest', 'xgboost', 'svm', 'ensemble']:
            path = self.models_dir / f'{name}.pkl'
            if path.exists():
                m = RandomForestModel() if name == 'random_forest' else XGBoostModel() if name == 'xgboost' else SVMModel() if name == 'svm' else HybridEnsemble()
                m.load(str(path))
                self.models[name] = m
        self.label_encoder = __import__('joblib').load(self.models_dir / 'label_encoder.pkl')
        self.model_names = list(self.models.keys())
        self.best_model_name = self.model_names[-1] if self.model_names else 'random_forest'

    def analyze_video(self, video_path, model_name=None):
        if model_name is None:
            model_name = self.best_model_name
        model = self.models.get(model_name, self.models.get(self.best_model_name))
        video_id = Path(video_path).stem
        fv = self._extract_video_features(video_path, video_id)
        X, _, _ = features_to_arrays([fv])
        if X.shape[0] == 0:
            return {'error': 'Could not extract features'}
        X_proc = self.pipeline.transform(X)
        pred = model.predict(X_proc)[0]
        proba = model.predict_proba(X_proc)[0]
        pred_label = self.label_encoder.inverse_transform([pred])[0]
        confidence = float(proba[pred])
        n_frames = len([s for s in fv.frame_features if s.get('has_face')])
        suspicious = sum(1 for s in fv.frame_features if s.get('has_face') and s.get('lbp_entropy', 0) > 1.5)
        return {
            'video_id': video_id,
            'prediction': pred_label,
            'confidence': round(confidence, 4),
            'frames_analyzed': n_frames,
            'suspicious_frames': suspicious,
            'model': model_name,
        }

    def _extract_video_features(self, video_path, video_id):
        from satyaverify_ml.data.loader import SATYAVerifyDataset
        from satyaverify_ml.utils.helpers import get_video_metadata, sample_frames, extract_audio
        from satyaverify_ml.features.hog import extract_hog_statistics, HOGConfig
        from satyaverify_ml.features.lbp import extract_lbp_statistics, LBPConfig
        from satyaverify_ml.features.color_lighting import extract_color_lighting_features, ColorLightingConfig
        from satyaverify_ml.features.frequency import extract_frequency_features, FrequencyConfig
        from satyaverify_ml.features.audio_mfcc import extract_audio_features, AudioConfig
        from satyaverify_ml.features.metadata import extract_metadata_features, MetadataConfig
        from satyaverify_ml.utils.helpers import FeatureVector
        meta = get_video_metadata(video_path, video_id, 'REAL')
        samples = sample_frames(video_path, 5.0, 30, 128)
        hog_feats, lbp_feats, cl_feats, freq_feats = [], [], [], []
        for s in samples:
            if s.face_crop is not None:
                face = s.face_crop
                h = extract_hog_statistics(face)
                if h is not None: hog_feats.append(h)
                l = extract_lbp_statistics(face)
                if l is not None: lbp_feats.append(l)
                c = extract_color_lighting_features(face)
                if c is not None: cl_feats.append(c)
                f = extract_frequency_features(face)
                if f is not None: freq_feats.append(f)
        audio_feat = None
        if meta.has_audio:
            audio_raw = extract_audio(video_path, AudioConfig().sample_rate)
            audio_feat = extract_audio_features(audio_raw, AudioConfig().sample_rate)
        meta_feat = extract_metadata_features(meta)
        return FeatureVector(
            video_id=video_id, label='REAL',
            hog=np.mean(hog_feats, axis=0) if hog_feats else None,
            lbp=np.mean(lbp_feats, axis=0) if lbp_feats else None,
            color_lighting=np.mean(cl_feats, axis=0) if cl_feats else None,
            frequency=np.mean(freq_feats, axis=0) if freq_feats else None,
            audio=audio_feat, metadata=meta_feat,
            frame_features=[],
        )

    def analyze_image(self, image_path, model_name=None):
        if model_name is None:
            model_name = self.best_model_name
        model = self.models.get(model_name, self.models.get(self.best_model_name))
        img = cv2.imread(image_path)
        if img is None:
            return {'error': 'Could not read image'}
        face, _ = detect_and_crop_face(img, target_size=128)
        if face is None:
            return {'error': 'No face detected'}
        from satyaverify_ml.features.hog import extract_hog_statistics, HOGConfig
        from satyaverify_ml.features.lbp import extract_lbp_statistics, LBPConfig
        from satyaverify_ml.features.color_lighting import extract_color_lighting_features, ColorLightingConfig
        from satyaverify_ml.features.frequency import extract_frequency_features, FrequencyConfig
        from satyaverify_ml.preprocessing import features_to_arrays
        from satyaverify_ml.utils.helpers import FeatureVector
        hog = extract_hog_statistics(face, HOGConfig())
        lbp = extract_lbp_statistics(face, LBPConfig())
        cl = extract_color_lighting_features(face, ColorLightingConfig())
        freq = extract_frequency_features(face, FrequencyConfig())
        fv = FeatureVector(
            video_id=Path(image_path).stem, label='REAL',
            hog=hog, lbp=lbp, color_lighting=cl, frequency=freq,
            audio=None, metadata=None,
        )
        combined, _ = features_to_arrays([fv])
        X = combined
        X_proc = self.pipeline.transform(X.reshape(1, -1))
        pred = model.predict(X_proc)[0]
        proba = model.predict_proba(X_proc)[0]
        pred_label = self.label_encoder.inverse_transform([pred])[0]
        confidence = float(proba[pred])
        return {'prediction': pred_label, 'confidence': round(confidence, 4)}