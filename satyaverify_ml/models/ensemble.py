import numpy as np
from typing import Dict, Any
from sklearn.ensemble import VotingClassifier
from .base import BaseModel
from .random_forest import RandomForestModel
from .xgboost_model import XGBoostModel
from .svm_model import SVMModel
from ..config import cfg
import logging

logger = logging.getLogger(__name__)

class HybridEnsemble(BaseModel):
    def __init__(self):
        super().__init__('HybridEnsemble')
        self.rf = RandomForestModel()
        self.xgb = XGBoostModel()
        self.svm = SVMModel()

    def fit(self, X, y):
        self.rf.fit(X, y)
        self.xgb.fit(X, y)
        self.svm.fit(X, y)
        self.model = VotingClassifier(
            estimators=[('rf', self.rf.model), ('xgb', self.xgb.model), ('svm', self.svm.model)],
            voting='soft',
            n_jobs=cfg.get('training', 'n_jobs', default=-1),
        )
        self.model.fit(X, y)
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)
