import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

from backend.database.db import SessionLocal, engine, Base
from backend.models.evidence import Evidence, ProvenanceEvent
from backend.schemas.evidence import EvidenceCreate, EvidenceResponse, ProvenanceResponse
from backend.services.hashing_service import compute_sha256
from backend.services.storage_service import save_upload_file
from backend.services.ml_service import analyze_media
from backend.services.gemini_service import gemini_analyze
from backend.services.blockchain_service import register_evidence_on_chain, get_contract_status

app = FastAPI(title="SATYAVERIFY API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/jpg",
    "video/mp4", "video/quicktime", "video/x-msvideo",
    "audio/wav", "audio/mpeg", "audio/mp3"
}
MAX_FILE_SIZE = 500 * 1024 * 1024

class AnalysisRequest(BaseModel):
    evidence_id: str

class VerificationRequest(BaseModel):
    evidence_id: str = None

class VerifyFileRequest(BaseModel):
    pass

@app.get("/api/health")
async def health():
    contract = get_contract_status()
    return {
        "status": "ok",
        "demo_mode": not contract["configured"],
        "blockchain": contract
    }

@app.post("/api/analyze", response_model=EvidenceResponse)
async def analyze_media_endpoint(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    sha256 = compute_sha256(content)
    db = SessionLocal()
    existing = db.query(Evidence).filter(Evidence.sha256 == sha256).first()
    if existing:
        db.close()
        return EvidenceResponse.from_orm(existing)
    file_path = save_upload_file(content, file.filename)
    mime_type = file.content_type
    media_type = "video" if mime_type.startswith("video") else "audio" if mime_type.startswith("audio") else "image"
    ml_result = analyze_media(file_path, media_type, content)
    gemini_result = gemini_analyze(file_path, ml_result) if os.getenv("GEMINI_API_KEY") else None
    evidence_id = str(uuid.uuid4())
    evidence = Evidence(
        evidence_id=evidence_id,
        filename=file.filename,
        media_type=media_type,
        mime_type=mime_type,
        sha256=sha256,
        size=len(content),
        ai_prediction=ml_result.get("prediction"),
        ai_confidence=ml_result.get("confidence"),
        model_scores=ml_result.get("model_scores"),
        suspicious_frames=ml_result.get("suspicious_frames"),
        gemini_assessment=gemini_result,
        features=ml_result.get("features"),
        media_metadata=ml_result.get("metadata"),
        status="ANALYZED"
    )
    db.add(evidence)
    db.flush()
    provenance = ProvenanceEvent(
        evidence_id=evidence.id,
        event_type="REGISTERED",
        description="Evidence registered for analysis",
        actor="system"
    )
    db.add(provenance)
    tx_hash = register_evidence_on_chain(evidence_id, sha256)
    if tx_hash:
        evidence.blockchain_tx_hash = tx_hash
        evidence.status = "VERIFIED"
        prov = ProvenanceEvent(
            evidence_id=evidence.id,
            event_type="ANALYZED",
            description=f"Analysis complete. Blockchain tx: {tx_hash}",
            actor="system",
            tx_hash=tx_hash
        )
        db.add(prov)
    db.commit()
    db.refresh(evidence)
    db.close()
    try:
        os.remove(file_path)
    except Exception:
        pass
    return EvidenceResponse.from_orm(evidence)

@app.post("/api/verify", response_model=dict)
async def verify_evidence(evidence_id: str = None, file: UploadFile = File(None)):
    db = SessionLocal()
    result = {"status": "UNKNOWN", "evidence_id": evidence_id, "message": ""}
    if file:
        content = await file.read()
        sha256 = compute_sha256(content)
        evidence = db.query(Evidence).filter(Evidence.sha256 == sha256).first()
        if evidence:
            result = {
                "status": "HASH_MATCH",
                "evidence_id": evidence.evidence_id,
                "sha256": sha256,
                "message": "Exact file hash matches registered evidence. File is identical to the registered copy. A hash match confirms file integrity, not content authenticity.",
                "evidence": EvidenceResponse.from_orm(evidence).dict()
            }
        else:
            result = {
                "status": "NOT_REGISTERED",
                "evidence_id": None,
                "sha256": sha256,
                "message": "File hash not found in registry. This does not mean the file is malicious; it simply means this exact file has not been previously registered."
            }
    elif evidence_id:
        evidence = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
        if evidence:
            result = {
                "status": "REGISTERED",
                "evidence_id": evidence.evidence_id,
                "sha256": evidence.sha256,
                "message": "Evidence found in registry.",
                "evidence": EvidenceResponse.from_orm(evidence).dict()
            }
        else:
            result = {
                "status": "NOT_REGISTERED",
                "evidence_id": evidence_id,
                "message": "Evidence ID not found in registry."
            }
    db.close()
    return result

@app.get("/api/evidence", response_model=list[EvidenceResponse])
async def list_evidence():
    db = SessionLocal()
    evidence_list = db.query(Evidence).order_by(Evidence.created_at.desc()).all()
    db.close()
    return [EvidenceResponse.from_orm(e) for e in evidence_list]

@app.get("/api/evidence/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(evidence_id: str):
    db = SessionLocal()
    evidence = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    db.close()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return EvidenceResponse.from_orm(evidence)

@app.get("/api/provenance/{evidence_id}", response_model=list[ProvenanceResponse])
async def get_provenance(evidence_id: str):
    db = SessionLocal()
    evidence = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    if not evidence:
        db.close()
        raise HTTPException(status_code=404, detail="Evidence not found")
    events = db.query(ProvenanceEvent).filter(ProvenanceEvent.evidence_id == evidence.id).order_by(ProvenanceEvent.timestamp.asc()).all()
    db.close()
    return [ProvenanceResponse.from_orm(e) for e in events]

@app.get("/api/blockchain/{evidence_id}", response_model=dict)
async def get_blockchain_record(evidence_id: str):
    db = SessionLocal()
    evidence = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    db.close()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    contract = get_contract_status()
    return {
        "evidence_id": evidence.evidence_id,
        "tx_hash": evidence.blockchain_tx_hash,
        "contract_configured": contract["configured"],
        "network": contract.get("network"),
        "demo_mode": not contract["configured"]
    }

@app.post("/api/report/{evidence_id}")
async def generate_report(evidence_id: str):
    db = SessionLocal()
    evidence = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    if not evidence:
        db.close()
        raise HTTPException(status_code=404, detail="Evidence not found")
    events = db.query(ProvenanceEvent).filter(ProvenanceEvent.evidence_id == evidence.id).order_by(ProvenanceEvent.timestamp.asc()).all()
    db.close()
    report = {
        "evidence_id": evidence.evidence_id,
        "filename": evidence.filename,
        "generated_at": datetime.utcnow().isoformat(),
        "disclaimer": "This system provides AI-assisted forensic analysis and should not be treated as an independent legal determination of authenticity.",
        "file_integrity": {
            "sha256": evidence.sha256,
            "size": evidence.size,
            "mime_type": evidence.mime_type
        },
        "ml_analysis": {
            "prediction": evidence.ai_prediction,
            "confidence": evidence.ai_confidence,
            "model_scores": evidence.model_scores,
            "suspicious_frames": evidence.suspicious_frames
        },
        "gemini_assessment": evidence.gemini_assessment,
        "media_metadata": evidence.media_metadata,
        "blockchain": {
            "tx_hash": evidence.blockchain_tx_hash,
            "status": "DEMO_MODE" if not evidence.blockchain_tx_hash else "RECORDED"
        },
        "provenance": [
            {
                "event": e.event_type,
                "timestamp": e.timestamp.isoformat(),
                "description": e.description,
                "actor": e.actor,
                "tx_hash": e.tx_hash
            } for e in events
        ]
    }
    return report
