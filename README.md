# SATYAVERIFY — AI Digital Media Forensics & Provenance Platform

A full-stack forensic analysis platform for detecting deepfakes and verifying media integrity using AI, cryptographic hashing, and blockchain provenance.

## Architecture

```
SATYAVERIFY
├── Frontend (React + Vite + Tailwind) → port 5173
├── Backend (FastAPI + Python)         → port 8000
├── Database (PostgreSQL)              → port 5432
├── ML Pipeline (scikit-learn/XGBoost)
├── AI Layer (Gemini API)
└── Blockchain (EVM-compatible / Demo Mode)
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- (Optional) Gemini API key

### Installation

1. Clone and enter the project:
```bash
cd satyaverify
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and GEMINI_API_KEY
```

3. Start with Docker Compose:
```bash
docker-compose up --build
```

4. Or run manually:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Database Setup

```bash
psql -U postgres -c "CREATE DATABASE satyaverify;"
```

### Train ML Models

```bash
cd ml_training
pip install scikit-learn xgboost joblib numpy
python train.py
```

### Gemini API Configuration

Set `GEMINI_API_KEY` in `.env`. Never expose the key in frontend code.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/analyze | Upload and analyze media |
| POST | /api/verify | Verify file integrity |
| GET | /api/evidence | List all evidence |
| GET | /api/evidence/{id} | Get evidence by ID |
| GET | /api/provenance/{id} | Get provenance chain |
| GET | /api/blockchain/{id} | Get blockchain record |
| POST | /api/report/{id} | Generate forensic report |
| GET | /api/health | Health check |

## Demo Mode

If blockchain credentials are not configured, the system runs in **Demo Mode**:
- Real SHA-256 hashing
- Real ML inference
- Local storage
- Simulated blockchain records (clearly labeled)

## Security Notes

- Never hard-code API keys
- Gemini API key is server-side only
- Temporary files are deleted after processing
- File uploads are validated for type and size
- Metadata is never treated as proof of authenticity

## Disclaimer

This system provides AI-assisted forensic analysis and should not be treated as an independent legal determination of authenticity.
