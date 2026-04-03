import asyncio
import json
import random
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Data Models
# ──────────────────────────────────────────────
class SettingsUpdate(BaseModel):
    toggles: Dict[str, bool]
    sensitivity: int

# ──────────────────────────────────────────────
# Mock Data Generators
# ──────────────────────────────────────────────
def get_mock_stats():
    return {
        "metrics": [
            { "id": 1, "label": "Threats Blocked", "value": f"{random.randint(1200, 1300):,}", "sub": "+12 today", "color": "red" },
            { "id": 2, "label": "Calls Screened", "value": f"{random.randint(3500, 3800):,}", "sub": "by VOX today", "color": "blue" },
            { "id": 3, "label": "Msgs Analysed", "value": f"{random.randint(9000, 9500):,}", "sub": "by Scholar today", "color": "purple" },
            { "id": 4, "label": "Safe Score", "value": f"{random.uniform(96, 99):.1f}%", "sub": "↑ 0.3% this week", "color": "green" },
        ],
        "threatsByType": [
            { "name": "Phishing", "value": 520 },
            { "name": "Voice Scam", "value": 310 },
            { "name": "Deepfake", "value": 180 },
            { "name": "Malware", "value": 140 },
            { "name": "OTP Fraud", "value": 95 },
            { "name": "Other", "value": 39 },
        ],
        "attackDistribution": [
            { "name": "Phishing", "value": 41 },
            { "name": "Voice", "value": 24 },
            { "name": "Deepfake", "value": 14 },
            { "name": "Malware", "value": 11 },
            { "name": "Other", "value": 10 },
        ],
        "recentAlerts": [
            { "id": 1, "caller": "+1 405-293-1102", "timestamp": "2 mins ago", "severity": "HIGH", "status": "Blocked", "summary": "Emergency relative scam pattern (A.I. Voice Clone detected)" },
            { "id": 2, "caller": "Unknown (Private)", "timestamp": "15 mins ago", "severity": "MEDIUM", "status": "Monitoring", "summary": "Unusual rapid-fire OTP request heuristic triggered." },
            { "id": 3, "caller": "Amazon Support (Spoofed)", "timestamp": "42 mins ago", "severity": "HIGH", "status": "Blocked", "summary": "Social engineering script - Refund claim detected." },
        ]
    }

# ──────────────────────────────────────────────
# REST Endpoints
# ──────────────────────────────────────────────
@app.get("/api/stats")
async def get_stats():
    return get_mock_stats()

@app.get("/api/alerts")
async def get_alerts(filter: str = "ALL", page: int = 1):
    # Standard high-fidelity mock alerts
    all_alerts = [
        { "id": 1, "severity": "HIGH", "title": "A.I. Voice Clone Detected", "desc": "Emergency relative scam pattern triggered from +1 405-293-1102.", "source": "VOX", "time": "2 mins ago", "status": "Blocked" },
        { "id": 2, "severity": "MEDIUM", "title": "Suspicious OTP Burst", "desc": "Rapid OTP requests (8+ in 60s) from unverified banking gateway.", "source": "Scholar", "time": "14 mins ago", "status": "Monitoring" },
        { "id": 3, "severity": "HIGH", "title": "Blacklisted Phishing Link", "desc": "User received message with known malicious domain: bank-verif.net.", "source": "Scholar", "time": "41 mins ago", "status": "Blocked" },
        { "id": 4, "severity": "LOW", "title": "Unusual Call Frequency", "desc": "Outbound call volume high for this contact ID. Mark for review.", "source": "VOX", "time": "1h 12m ago", "status": "Logged" },
        { "id": 5, "severity": "MEDIUM", "title": "Mimicked Sender ID", "desc": "Bank of America spoofed via unverified regional gateway.", "source": "Scholar", "time": "2h 15m ago", "status": "Flagged" },
    ]
    return {
        "alerts": all_alerts,
        "total": 1284,
        "page": page,
        "limit": 10
    }

@app.post("/api/settings")
async def update_settings(settings: SettingsUpdate):
    print(f"DEBUG: Updating settings: {settings}")
    return {"status": "success", "message": "Settings updated"}

@app.post("/api/block")
async def block_sender(data: dict):
    print(f"DEBUG: Blocking sender: {data}")
    return {"status": "success"}

@app.post("/api/report")
async def report_fraud(data: dict):
    print(f"DEBUG: Reporting fraud: {data}")
    return {"status": "success"}

# ──────────────────────────────────────────────
# WebSockets for Real-time Monitoring
# ──────────────────────────────────────────────
@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    await websocket.accept()
    print(f"WS: Client connected to channel: {channel}")
    try:
        while True:
            # Send live updates based on the channel
            if channel == "scholar":
                await websocket.send_text(json.dumps({
                    "id": random.randint(100, 999),
                    "sender": f"+1 {random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    "time": datetime.now().strftime("%I:%M %p"),
                    "text": "URGENT: Your account was accessed. Click here if this wasn't you: http://bit.ly/scam-verif",
                    "severity": "HIGH",
                    "linkStatus": "PHISHING",
                    "linkDetails": "bit.ly/scam-verif (Blacklisted)",
                    "vtCount": "52/90",
                    "sbVerdict": "MALICIOUS",
                    "indicators": ["Urgency language", "Mimics sender ID"]
                }))
            else:
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "status": "active",
                    "timestamp": datetime.now().isoformat()
                }))
            await asyncio.sleep(8) # Live updates every 8 seconds
    except WebSocketDisconnect:
        print(f"WS: Client disconnected from channel: {channel}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
