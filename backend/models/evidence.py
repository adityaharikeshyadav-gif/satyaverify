from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, Text, JSON
from sqlalchemy.sql import func
from backend.database.db import Base

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    media_type = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    sha256 = Column(String, nullable=False, index=True)
    size = Column(Integer, nullable=False)
    ipfs_cid = Column(String, nullable=True)
    ai_prediction = Column(String, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    model_scores = Column(JSON, nullable=True)
    suspicious_frames = Column(JSON, nullable=True)
    gemini_assessment = Column(JSON, nullable=True)
    features = Column(JSON, nullable=True)
    media_metadata = Column(JSON, nullable=True)
    model_version = Column(String, default="hybrid-v1")
    status = Column(String, default="PENDING")
    blockchain_tx_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProvenanceEvent(Base):
    __tablename__ = "provenance_events"
    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    actor = Column(String, default="system")
    tx_hash = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
