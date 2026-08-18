import os
import uuid
from typing import Optional
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", _BACKEND_DIR / "storage" / "uploads"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

def save_upload_file(content: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = STORAGE_DIR / unique_name
    with open(file_path, "wb") as f:
        f.write(content)
    return str(file_path)

def get_file_path(evidence_id: str) -> Optional[str]:
    for f in os.listdir(STORAGE_DIR):
        if f.startswith(evidence_id):
            return str(STORAGE_DIR / f)
    return None
