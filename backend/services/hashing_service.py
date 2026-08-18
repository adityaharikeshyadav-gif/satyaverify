import hashlib
from typing import Optional
from fastapi import UploadFile

def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

async def compute_sha256_upload(file: UploadFile) -> str:
    content = await file.read()
    await file.seek(0)
    return compute_sha256(content)
