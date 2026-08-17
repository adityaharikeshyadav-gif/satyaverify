import numpy as np
from typing import Dict, Any
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from .base import BaseModel
from ..config import cfg
import logging

logger = logging.getLogger(__name__)

class SVMModel(BaseModel):
    def __init__(self):
        super().__init__('SVM')

    def fit(self, X, y):
        param_grid = cfg.get('models', 'svm', 'param_grid', default={
            'kernel': ['rbf', 'linear'],
            'C': [0.1, 1, 10, 100],
            'gamma': ['scale', 'auto'],
        })
        base = SVC(probability=True, random_state=42)
        n_splits = min(5, len(np.unique(y)), len(y) // 2)
        if n_splits < 2:
            self.model = base.fit(X, y)
            self.best_params_ = {}
            return self
        grid = GridSearchCV(base, param_grid, cv=n_splits, scoring='f1',
                            n_jobs=cfg.get('training', 'n_jobs', default=-1),
                            verbose=cfg.get('training', 'verbose', default=2))
        grid.fit(X, y)
        self.model = grid.best_estimator_
        self.best_params_ = grid.best_params_
        logger.info(f'SVM best params: {self.best_params_}')
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)
