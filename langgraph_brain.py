"""
LangGraph Brain Simulator
Node B: Audio Processing & Edge Routing
"""

import requests
from core.config import VOX_SERVICE_URL
from core.zero_trust_gate import get_secure_headers

def send_to_vox_service(payload: dict) -> dict:
    """
    A simulated LangGraph node that takes the payload and funnels
    it seamlessly over the internet securely to the friend's laptop endpoint.
    """
    url = f"{VOX_SERVICE_URL}/analyze-text"
    headers = get_secure_headers()
    
    print(f"[Node B Request] Outbound to: {url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[Node B Error] Network boundary failure: {e}")
        return {"error": str(e)}

def healthcheck_vox_link() -> dict:
    """Pings the /health block using generic routing"""
    try:
        url = f"{VOX_SERVICE_URL}/health"
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}
