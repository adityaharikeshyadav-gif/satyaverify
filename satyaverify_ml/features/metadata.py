import numpy as np
from typing import Optional
import hashlib

class MetadataConfig:
    def __init__(self):
        self.extract = ['fps', 'frame_count', 'width', 'height', 'duration', 'bitrate']

def extract_metadata_features(meta, cfg=None):
    if cfg is None:
        cfg = MetadataConfig()
    try:
        features = []
        for key in cfg.extract:
            val = getattr(meta, key, None)
            if val is not None:
                if isinstance(val, str):
                    h = int(hashlib.md5(val.encode()).hexdigest(), 16)
                    val = float(h % 1000000)
                features.append(float(val))
            else:
                features.append(0.0)
        return np.array(features, dtype=np.float64)
    except Exception:
        return None
