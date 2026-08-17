import numpy as np
import cv2
from scipy import fftpack
from typing import Optional

class FrequencyConfig:
    def __init__(self):
        self.fft_features = ['mean', 'std', 'energy', 'entropy', 'peak_freq']
        self.dct_features = ['mean', 'std', 'energy']

def extract_frequency_features(face, cfg=None):
    if cfg is None:
        cfg = FrequencyConfig()
    try:
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) if face.shape[2] == 3 else face
        if face.dtype != np.uint8:
            gray = (gray * 255).astype(np.uint8) if gray.max() <= 1.0 else gray.astype(np.uint8)
        features = []
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude = np.abs(fshift)
        magnitude = magnitude / (magnitude.sum() + 1e-10)
        h, w = gray.shape
        cy, cx = h // 2, w // 2
        y, x = np.indices((h, w))
        r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2).astype(int)
        radial = np.bincount(r.ravel(), weights=magnitude.ravel())
        p = radial / (radial.sum() + 1e-10)
        p = p[p > 0]
        features.append(np.mean(radial))
        features.append(np.std(radial))
        features.append(np.sum(radial ** 2))
        features.append(-np.sum(p * np.log(p + 1e-10)))
        features.append(np.argmax(radial) / (len(radial) + 1e-10))
        dct = fftpack.dct(fftpack.dct(gray.T, norm='ortho').T, norm='ortho')
        coeffs = dct.ravel() / (np.sum(np.abs(dct.ravel())) + 1e-10)
        features.append(np.mean(coeffs))
        features.append(np.std(coeffs))
        features.append(np.sum(coeffs ** 2))
        return np.array(features, dtype=np.float64)
    except Exception:
        return None
