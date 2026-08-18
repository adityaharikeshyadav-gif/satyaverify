import os
import json
import base64
import requests
from typing import Dict, Any, Optional

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def gemini_analyze(file_path: str, ml_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not GEMINI_API_KEY:
        return None
    try:
        prompt = """You are a digital forensics assistant. Analyze the following ML forensic result and provide an AI-assisted observation.
Do not fabricate evidence. Label all observations as 'AI-assisted'.
Return strict JSON with keys: assessment, confidence, observations, possible_manipulations, limitations, recommendation.

ML Result:
""" + json.dumps(ml_result, indent=2)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT"]}
        }
        headers = {"Content-Type": "application/json"}
        params = {"key": GEMINI_API_KEY}
        resp = requests.post(GEMINI_URL, json=payload, headers=headers, params=params, timeout=60)
        if resp.status_code != 200:
            return None
        data = resp.json()
        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        try:
            return json.loads(text)
        except Exception:
            return {"raw": text}
    except Exception:
        return None
