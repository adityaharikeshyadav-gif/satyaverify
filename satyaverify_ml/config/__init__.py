import os
import yaml
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    _instance = None
    def __new__(cls, config_path = 'satyaverify_ml/config/config.yaml'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load(config_path)
        return cls._instance
    def _load(self, config_path):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f'Config not found: {config_path}')
        with open(self.config_path, 'r') as f:
            self.cfg = yaml.safe_load(f)
    def get(self, *keys, default=None):
        d = self.cfg
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return default
        return d
    def __getitem__(self, item):
        return self.cfg[item]

cfg = Config()