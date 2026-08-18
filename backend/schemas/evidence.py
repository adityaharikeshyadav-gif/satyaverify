from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class EvidenceCreate(BaseModel):
    filename: str
    media_type: str
    sha256: str
    size: int

class EvidenceResponse(BaseModel):
    id: int
    evidence_id: str
    filename: str
    media_type: str
    mime_type: str
    sha256: str
    size: int
    ipfs_cid: Optional[str]
    ai_prediction: Optional[str]
    ai_confidence: Optional[float]
    model_scores: Optional[Dict[str, Any]]
    suspicious_frames: Optional[List[Dict[str, Any]]]
    gemini_assessment: Optional[Dict[str, Any]]
    features: Optional[Dict[str, Any]]
    media_metadata: Optional[Dict[str, Any]]
    model_version: str
    status: str
    blockchain_tx_hash: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ProvenanceResponse(BaseModel):
    id: int
    evidence_id: int
    event_type: str
    description: Optional[str]
    actor: str
    tx_hash: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True
