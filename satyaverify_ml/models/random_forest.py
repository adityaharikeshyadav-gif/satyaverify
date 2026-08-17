import numpy as np
from typing import Dict, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from .base import BaseModel
from ..config import cfg
import logging

logger = logging.getLogger(__name__)

class RandomForestModel(BaseModel):
    def __init__(self):
        super().__init__('RandomForest')

    def fit(self, X, y):
        param_grid = cfg.get('models', 'random_forest', 'param_grid', default={
            'n_estimators': [100, 300, 500],
            'max_depth': [10, 20, 30, None],
            'min_samples_split': [2, 5, 10],
            'max_features': ['sqrt', 'log2'],
        })
        base = RandomForestClassifier(random_state=42, n_jobs=cfg.get('training', 'n_jobs', default=-1))
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
        logger.info(f'RF best params: {self.best_params_}')
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)
