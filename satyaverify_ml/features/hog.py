import numpy as np
import cv2
from skimage.feature import hog
from typing import Optional
from scipy import stats

class HOGConfig:
    def __init__(self):
        self.orientations = 9
        self.pixels_per_cell = (8, 8)
        self.cells_per_block = (2, 2)
        self.channel_axis = -1

def extract_hog_statistics(face, cfg=None):
    if cfg is None:
        cfg = HOGConfig()
    try:
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) if face.shape[2] == 3 else face
        if face.dtype != np.uint8:
            gray = (gray * 255).astype(np.uint8) if gray.max() <= 1.0 else gray.astype(np.uint8)
        features = hog(
            gray,
            orientations=cfg.orientations,
            pixels_per_cell=cfg.pixels_per_cell,
            cells_per_block=cfg.cells_per_block,
            block_norm='L2-Hys',
            feature_vector=True,
            channel_axis=None,
        )
        if features is None or len(features) == 0:
            return None
        s = []
        s.extend([np.mean(features), np.std(features), np.median(features),
                  np.percentile(features, 25), np.percentile(features, 75),
                  np.min(features), np.max(features), np.max(features) - np.min(features),
                  stats.skew(features), stats.kurtosis(features)])
        return np.array(s, dtype=np.float64)
    except Exception:
        return None
