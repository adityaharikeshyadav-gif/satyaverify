import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import joblib
import logging

logger = logging.getLogger(__name__)

class BaseModel(ABC):
    def __init__(self, name):
        self.name = name
        self.model = None
        self.best_params_ = {}

    @abstractmethod
    def fit(self, X, y):
        pass

    @abstractmethod
    def predict(self, X):
        pass

    @abstractmethod
    def predict_proba(self, X):
        pass

    def save(self, path):
        joblib.dump({'model': self.model, 'best_params': self.best_params_}, path)
        logger.info(f'Model saved to {path}')

    def load(self, path):
        data = joblib.load(path)
        self.model = data['model']
        self.best_params_ = data.get('best_params', {})
