import numpy as np
from typing import Dict, Any
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
from .base import BaseModel
from ..config import cfg
import logging

logger = logging.getLogger(__name__)

class XGBoostModel(BaseModel):
    def __init__(self):
        super().__init__('XGBoost')

    def fit(self, X, y):
        param_grid = cfg.get('models', 'xgboost', 'param_grid', default={
            'n_estimators': [100, 300],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.1, 0.3],
            'subsample': [0.8, 1.0],
            'colsample_bytree': [0.8, 1.0],
        })
        base = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss',
                             n_jobs=cfg.get('training', 'n_jobs', default=-1))
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
        logger.info(f'XGB best params: {self.best_params_}')
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)
