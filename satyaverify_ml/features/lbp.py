import numpy as np
import cv2
from skimage.feature import local_binary_pattern
from typing import Optional
from scipy import stats

class LBPConfig:
    def __init__(self):
        self.radius = 3
        self.n_points = 24
        self.method = 'uniform'
        self.grid_h = 4
        self.grid_w = 4

def extract_lbp_statistics(face, cfg=None):
    if cfg is None:
        cfg = LBPConfig()
    try:
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) if face.shape[2] == 3 else face
        if face.dtype != np.uint8:
            gray = (gray * 255).astype(np.uint8) if gray.max() <= 1.0 else gray.astype(np.uint8)
        lbp = local_binary_pattern(gray, P=cfg.n_points, R=cfg.radius, method=cfg.method)
        n_bins = cfg.n_points + 2
        hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins), density=True)
        hist = hist / (np.sum(hist) + 1e-10)
        s = []
        s.extend([np.mean(hist), np.std(hist), np.median(hist),
                  np.percentile(hist, 25), np.percentile(hist, 75),
                  np.min(hist), np.max(hist),
                  -np.sum(hist[hist > 0] * np.log(hist[hist > 0] + 1e-10)),
                  np.sum(hist ** 2)])
        return np.array(s, dtype=np.float64)
    except Exception:
        return None
