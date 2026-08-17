import os
import sys
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
import numpy as np
import cv2
import librosa
from scipy import stats
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, mutual_info_classif
import joblib
import psutil

logger = logging.getLogger(__name__)


@dataclass
class VideoMetadata:
    video_id: str
    label: str
    file_path: str
    manipulation_type: str
    duration: float = 0.0
    fps: float = 0.0
    frame_count: int = 0
    width: int = 0
    height: int = 0
    codec: str = ""
    format: str = ""
    has_audio: bool = False
    bitrate: int = 0
    file_size: int = 0


@dataclass
class FrameSample:
    frame_idx: int
    timestamp: float
    face_crop: Optional[np.ndarray] = None
    face_bbox: Optional[Tuple[int, int, int, int]] = None
    landmarks: Optional[np.ndarray] = None


@dataclass
class FeatureVector:
    video_id: str
    label: str
    hog: Optional[np.ndarray] = None
    lbp: Optional[np.ndarray] = None
    color_lighting: Optional[np.ndarray] = None
    frequency: Optional[np.ndarray] = None
    audio: Optional[np.ndarray] = None
    metadata: Optional[np.ndarray] = None
    frame_features: List[Dict[str, Any]] = field(default_factory=list)


def get_video_metadata(video_path: str, video_id: str, label: str, manipulation_type: str) -> VideoMetadata:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0.0
    cap.release()

    file_size = Path(video_path).stat().st_size
    ext = Path(video_path).suffix.lower()
    fmt = ext[1:] if ext else "mp4"

    has_audio = False
    try:
        import ffmpeg
        probe = ffmpeg.probe(video_path)
        for stream in probe.get("streams", []):
            if stream.get("codec_type") == "audio":
                has_audio = True
                break
    except Exception:
        pass

    return VideoMetadata(
        video_id=video_id,
        label=label,
        file_path=video_path,
        manipulation_type=manipulation_type,
        duration=duration,
        fps=fps,
        frame_count=frame_count,
        width=width,
        height=height,
        format=fmt,
        has_audio=has_audio,
        bitrate=int(file_size / duration) if duration > 0 else 0,
        file_size=file_size,
    )


def detect_and_crop_face(
    frame: np.ndarray,
    target_size: int = 128,
) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]]]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
    if len(faces) == 0:
        return None, None

    x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
    pad_w = int(w * 0.3)
    pad_h = int(h * 0.3)
    x1 = max(0, x - pad_w)
    y1 = max(0, y - pad_h)
    x2 = min(frame.shape[1], x + w + pad_w)
    y2 = min(frame.shape[0], y + h + pad_h)
    face = frame[y1:y2, x1:x2]
    if face.size == 0:
        return None, None
    face = cv2.resize(face, (target_size, target_size), interpolation=cv2.INTER_AREA)
    return face, (x, y, w, h)


def sample_frames(
    video_path: str,
    target_fps: float = 5.0,
    max_frames: int = 30,
    target_size: int = 128,
) -> List[FrameSample]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    orig_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if orig_fps <= 0 or frame_count <= 0:
        cap.release()
        return []

    interval = max(1, int(orig_fps / target_fps))
    samples = []
    idx = 0
    while idx < frame_count and len(samples) < max_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            break
        timestamp = idx / orig_fps
        face, bbox = detect_and_crop_face(frame, target_size=target_size)
        samples.append(FrameSample(
            frame_idx=idx,
            timestamp=timestamp,
            face_crop=face,
            face_bbox=bbox,
        ))
        idx += interval
    cap.release()
    return samples


def extract_audio(
    video_path: str,
    sample_rate: int = 16000,
) -> Optional[np.ndarray]:
    try:
        import ffmpeg
        out, _ = (
            ffmpeg.input(video_path, threads=0)
            .output("-", format="wav", ac=1, ar=sample_rate, loglevel="error")
            .run(capture_stdout=True, capture_stderr=True)
        )
        audio = np.frombuffer(out, dtype=np.float32)
        return audio
    except Exception:
        return None


def combine_feature_vector(fv: FeatureVector) -> np.ndarray:
    parts = []
    feature_names = []

    if fv.hog is not None:
        parts.append(fv.hog)
        feature_names.extend([f"hog_{i}" for i in range(len(fv.hog))])
    if fv.lbp is not None:
        parts.append(fv.lbp)
        feature_names.extend([f"lbp_{i}" for i in range(len(fv.lbp))])
    if fv.color_lighting is not None:
        parts.append(fv.color_lighting)
        feature_names.extend([f"cl_{i}" for i in range(len(fv.color_lighting))])
    if fv.frequency is not None:
        parts.append(fv.frequency)
        feature_names.extend([f"freq_{i}" for i in range(len(fv.frequency))])
    if fv.audio is not None:
        parts.append(fv.audio)
        feature_names.extend([f"audio_{i}" for i in range(len(fv.audio))])
    if fv.metadata is not None:
        parts.append(fv.metadata)
        feature_names.extend([f"meta_{i}" for i in range(len(fv.metadata))])

    if not parts:
        return np.array([])

    combined = np.concatenate(parts)
    return combined, feature_names


def save_pipeline(
    scaler: StandardScaler,
    pca: Optional[PCA],
    feature_names: List[str],
    selected_features: List[str],
    label_encoder: LabelEncoder,
    output_dir: str,
):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, out / "scaler.pkl")
    joblib.dump(feature_names, out / "feature_names.pkl")
    joblib.dump(selected_features, out / "selected_features.pkl")
    joblib.dump(label_encoder, out / "label_encoder.pkl")
    if pca is not None:
        joblib.dump(pca, out / "pca.pkl")
    logger.info(f"Pipeline artifacts saved to {out}")


def load_pipeline(output_dir: str) -> Dict[str, Any]:
    out = Path(output_dir)
    artifacts = {}
    for name in ["scaler.pkl", "feature_names.pkl", "selected_features.pkl",
                 "label_encoder.pkl", "pca.pkl"]:
        path = out / name
        if path.exists():
            artifacts[name.replace(".pkl", "")] = joblib.load(path)
    return artifacts


def log_memory():
    mem = psutil.Process().memory_info().rss / (1024 ** 2)
    logger.debug(f"Memory usage: {mem:.1f} MB")
