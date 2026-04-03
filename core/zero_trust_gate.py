from fastapi import FastAPI, HTTPException, Request
from .config import ZERO_TRUST_SECRET

def get_secure_headers() -> dict:
    """
    Returns the required headers to access external secure systems,
    injecting the predefined zero-trust shared secret.
    """
    return {
        "X-Trust-Token": ZERO_TRUST_SECRET,
        "Accept": "application/json"
    }

async def verify_trust_token(request: Request):
    """
    FastAPI dependency intended to be used on the VOX backend
    to verify that incoming network connections contain the shared secret.
    """
    token = request.headers.get("X-Trust-Token")
    if not token or token != ZERO_TRUST_SECRET:
        raise HTTPException(
            status_code=403, 
            detail="Zero Trust policy violated: Invalid or missing X-Trust-Token"
        )
