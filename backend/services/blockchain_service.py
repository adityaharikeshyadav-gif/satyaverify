import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except Exception:
    WEB3_AVAILABLE = False

BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "")
BLOCKCHAIN_PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY", "")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")

_contract_status = {"configured": False, "network": None, "address": None}

if WEB3_AVAILABLE and BLOCKCHAIN_RPC_URL and BLOCKCHAIN_PRIVATE_KEY:
    try:
        w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))
        if w3.is_connected() and CONTRACT_ADDRESS:
            _contract_status = {
                "configured": True,
                "network": w3.net.version,
                "address": CONTRACT_ADDRESS
            }
    except Exception:
        pass

def get_contract_status() -> Dict[str, Any]:
    return _contract_status

def register_evidence_on_chain(evidence_id: str, sha256: str) -> Optional[str]:
    if not _contract_status["configured"]:
        return None
    try:
        import traceback
        traceback.print_exc()
        return "0xDEMO" + evidence_id[:8]
    except Exception:
        return None

def get_provenance_from_chain(evidence_id: str) -> Optional[Dict[str, Any]]:
    if not _contract_status["configured"]:
        return None
    return {"demo": True}
