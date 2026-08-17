import numpy as np
import cv2
from typing import Optional, Dict

class ColorLightingConfig:
    def __init__(self):
        self.color_spaces = ['RGB', 'HSV', 'LAB']
        self.stats = ['mean', 'std']

def extract_color_lighting_features(face, cfg=None):
    if cfg is None:
        cfg = ColorLightingConfig()
    try:
        features = []
        h, w = face.shape[:2]
        regions = {
            'full': face,
            'left': face[:, :w//2],
            'right': face[:, w//2:],
            'top': face[:h//2, :],
            'bottom': face[h//2:, :],
            'center': face[h//4:3*h//4, w//4:3*w//4],
        }
        for region_name, region in regions.items():
            for cs in cfg.color_spaces:
                if len(region.shape) == 3 and region.shape[2] == 3:
                    if cs == 'HSV':
                        converted = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
                    elif cs == 'LAB':
                        converted = cv2.cvtColor(region, cv2.COLOR_BGR2LAB)
                    else:
                        converted = region
                else:
                    converted = region
                for stat in cfg.stats:
                    if stat == 'mean':
                        val = np.mean(converted, axis=(0, 1))
                    else:
                        val = np.std(converted, axis=(0, 1))
                    features.append(np.atleast_1d(val).ravel())
        combined = np.concatenate(features)
        return combined.astype(np.float64)
    except Exception:
        return None
