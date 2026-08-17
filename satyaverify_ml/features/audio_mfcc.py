import numpy as np
import librosa
from typing import Optional

class AudioConfig:
    def __init__(self):
        self.sample_rate = 16000
        self.n_mfcc = 13
        self.hop_length = 512

def extract_audio_features(audio, sr=16000, cfg=None):
    if cfg is None:
        cfg = AudioConfig()
    if audio is None or len(audio) == 0:
        return None
    try:
        features = []
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=cfg.n_mfcc, hop_length=cfg.hop_length)
        features.extend(np.mean(mfcc, axis=1).tolist())
        features.extend(np.std(mfcc, axis=1).tolist())
        sc = librosa.feature.spectral_centroid(y=audio, sr=sr, hop_length=cfg.hop_length)
        features.append(float(np.mean(sc)))
        features.append(float(np.std(sc)))
        sb = librosa.feature.spectral_bandwidth(y=audio, sr=sr, hop_length=cfg.hop_length)
        features.append(float(np.mean(sb)))
        features.append(float(np.std(sb)))
        zcr = librosa.feature.zero_crossing_rate(y=audio, hop_length=cfg.hop_length)
        features.append(float(np.mean(zcr)))
        features.append(float(np.std(zcr)))
        rms = librosa.feature.rms(y=audio, hop_length=cfg.hop_length)
        features.append(float(np.mean(rms)))
        features.append(float(np.std(rms)))
        chroma = librosa.feature.chroma_stft(y=audio, sr=sr, hop_length=cfg.hop_length)
        features.extend(np.mean(chroma, axis=1).tolist())
        features.extend(np.std(chroma, axis=1).tolist())
        rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr, hop_length=cfg.hop_length)
        features.append(float(np.mean(rolloff)))
        features.append(float(np.std(rolloff)))
        return np.array(features, dtype=np.float64)
    except Exception:
        return None
