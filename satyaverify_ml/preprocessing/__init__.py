import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, mutual_info_classif
import joblib
from ..utils.helpers import FeatureVector, combine_feature_vector
from ..config import cfg

logger = logging.getLogger(__name__)

def features_to_arrays(feature_vectors):
    rows = []
    feature_names = []
    label_encoder = LabelEncoder()
    labels = []
    for fv in feature_vectors:
        combined, names = combine_feature_vector(fv)
        if combined.size == 0:
            continue
        rows.append(combined)
        if not feature_names:
            feature_names = names
        labels.append(fv.label)
    if not rows:
        return np.empty((0, 0)), [], np.array([])
    X = np.vstack(rows).astype(np.float64)
    y = label_encoder.fit_transform(labels)
    return X, feature_names, y

class PreprocessingPipeline:
    def __init__(self, scaler=None, pca=None):
        self.scaler = scaler if scaler is not None else StandardScaler()
        self.pca = pca
        self.feature_names = []
        self.selected_features = []

    def fit(self, X, feature_names):
        self.feature_names = feature_names
        X_scaled = self.scaler.fit_transform(X)
        use_pca = cfg.get('preprocessing', 'pca', 'enabled', default=True)
        if use_pca:
            var_thresh = cfg.get('preprocessing', 'pca', 'variance_threshold', default=0.95)
            max_comp = cfg.get('preprocessing', 'pca', 'max_components', default=100)
            self.pca = PCA(n_components=min(max_comp, X_scaled.shape[1]), svd_solver='randomized', random_state=42)
            X_pca = self.pca.fit_transform(X_scaled)
            cumvar = np.cumsum(self.pca.explained_variance_ratio_)
            n_comp = np.argmax(cumvar >= var_thresh) + 1
            self.pca = PCA(n_components=n_comp, svd_solver='randomized', random_state=42)
            X_pca = self.pca.fit_transform(X_scaled)
            logger.info(f'PCA: {X_scaled.shape[1]} -> {n_comp} components ({cumvar[n_comp-1]:.3f} variance)')
            return X_pca
        return X_scaled

    def transform(self, X):
        X_scaled = self.scaler.transform(X)
        if self.pca is not None:
            return self.pca.transform(X_scaled)
        return X_scaled

    def save(self, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        joblib.dump(self.scaler, Path(output_dir) / 'scaler.pkl')
        if self.pca is not None:
            joblib.dump(self.pca, Path(output_dir) / 'pca.pkl')
        joblib.dump(self.feature_names, Path(output_dir) / 'feature_names.pkl')
        joblib.dump(self.selected_features, Path(output_dir) / 'selected_features.pkl')
        logger.info(f'Preprocessing pipeline saved to {output_dir}')

    def load(self, output_dir):
        d = Path(output_dir)
        self.scaler = joblib.load(d / 'scaler.pkl')
        pca_path = d / 'pca.pkl'
        if pca_path.exists():
            self.pca = joblib.load(pca_path)
        self.feature_names = joblib.load(d / 'feature_names.pkl')
        self.selected_features = joblib.load(d / 'selected_features.pkl')
