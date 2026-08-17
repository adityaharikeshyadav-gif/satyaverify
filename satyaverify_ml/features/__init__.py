import numpy as np
import cv2
import librosa
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
from .hog import extract_hog_statistics, HOGConfig
from .lbp import extract_lbp_statistics, LBPConfig
from .color_lighting import extract_color_lighting_features, ColorLightingConfig
from .frequency import extract_frequency_features, FrequencyConfig
from .audio_mfcc import extract_audio_features, AudioConfig
from .metadata import extract_metadata_features, MetadataConfig
from ..utils.helpers import VideoMetadata, FeatureVector, get_video_metadata, sample_frames, extract_audio
from ..config import cfg

logger = logging.getLogger(__name__)

def extract_video_features(video_path, video_id, label, manipulation_type='unknown',
                           target_fps=5.0, max_frames=30, face_size=128):
    meta = get_video_metadata(video_path, video_id, label, manipulation_type)
    samples = sample_frames(video_path, target_fps, max_frames, face_size)
    hog_feats, lbp_feats, cl_feats, freq_feats = [], [], [], []
    hog_cfg, lbp_cfg, cl_cfg, freq_cfg = HOGConfig(), LBPConfig(), ColorLightingConfig(), FrequencyConfig()
    audio_feat = None
    for s in samples:
        if s.face_crop is not None:
            face = s.face_crop
            h = extract_hog_statistics(face, hog_cfg)
            if h is not None: hog_feats.append(h)
            l = extract_lbp_statistics(face, lbp_cfg)
            if l is not None: lbp_feats.append(l)
            c = extract_color_lighting_features(face, cl_cfg)
            if c is not None: cl_feats.append(c)
            f = extract_frequency_features(face, freq_cfg)
            if f is not None: freq_feats.append(f)
    if meta.has_audio:
        audio_raw = extract_audio(video_path, AudioConfig().sample_rate)
        audio_feat = extract_audio_features(audio_raw, AudioConfig().sample_rate)
    meta_feat = extract_metadata_features(meta)
    return FeatureVector(
        video_id=video_id, label=label,
        hog=np.mean(hog_feats, axis=0) if hog_feats else None,
        lbp=np.mean(lbp_feats, axis=0) if lbp_feats else None,
        color_lighting=np.mean(cl_feats, axis=0) if cl_feats else None,
        frequency=np.mean(freq_feats, axis=0) if freq_feats else None,
        audio=audio_feat, metadata=meta_feat,
        frame_features=[],
    )
