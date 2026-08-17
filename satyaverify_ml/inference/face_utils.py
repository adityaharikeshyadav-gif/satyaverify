import cv2
import numpy as np
from typing import Optional, Tuple

def detect_and_crop_face(frame, target_size=128):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
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