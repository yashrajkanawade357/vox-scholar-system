"""
BIGDADDY - Step 6: External API Integration
=============================================
VirusTotal API and Google Safe Browsing API integration
for external URL validation.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
GSB_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "")


def check_virustotal(url: str) -> dict:
    """Check a URL against VirusTotal's database."""
    if not VT_API_KEY or VT_API_KEY == "your_virustotal_api_key_here":
        return {"source": "VirusTotal", "status": "no_api_key", "url": url,
                "message": "VirusTotal API key not configured. Add it to .env file."}
    try:
        import base64
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        headers = {"x-apikey": VT_API_KEY}
        resp = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = data.get("malicious", 0)
            suspicious = data.get("suspicious", 0)
            total = sum(data.values()) if data else 0
            risk = "HIGH" if malicious > 2 else "MEDIUM" if (malicious > 0 or suspicious > 0) else "LOW"
            return {"source": "VirusTotal", "status": "found", "url": url,
                    "malicious": malicious, "suspicious": suspicious, "total_engines": total,
                    "risk_level": risk, "raw_stats": data}
        elif resp.status_code == 404:
            return {"source": "VirusTotal", "status": "not_found", "url": url, "risk_level": "UNKNOWN",
                    "message": "URL not in VirusTotal database."}
        else:
            return {"source": "VirusTotal", "status": "error", "url": url, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"source": "VirusTotal", "status": "error", "url": url, "error": str(e)}


def check_google_safe_browsing(url: str) -> dict:
    """Check a URL against Google Safe Browsing API."""
    if not GSB_API_KEY or GSB_API_KEY == "your_google_safe_browsing_key_here":
        return {"source": "Google Safe Browsing", "status": "no_api_key", "url": url,
                "message": "Google Safe Browsing API key not configured. Add it to .env file."}
    try:
        api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GSB_API_KEY}"
        payload = {
            "client": {"clientId": "bigdaddy-scanner", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }
        resp = requests.post(api_url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("matches"):
                threats = [m.get("threatType", "UNKNOWN") for m in data["matches"]]
                return {"source": "Google Safe Browsing", "status": "flagged", "url": url,
                        "threats": threats, "risk_level": "HIGH", "match_count": len(data["matches"])}
            return {"source": "Google Safe Browsing", "status": "clean", "url": url, "risk_level": "LOW"}
        else:
            return {"source": "Google Safe Browsing", "status": "error", "url": url, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"source": "Google Safe Browsing", "status": "error", "url": url, "error": str(e)}


def check_url_all_sources(url: str) -> dict:
    """Check URL against all available external sources."""
    vt = check_virustotal(url)
    gsb = check_google_safe_browsing(url)
    risks = [r.get("risk_level", "UNKNOWN") for r in [vt, gsb] if r.get("risk_level")]
    overall = "HIGH" if "HIGH" in risks else "MEDIUM" if "MEDIUM" in risks else "LOW"
    return {"url": url, "virustotal": vt, "google_safe_browsing": gsb, "overall_risk": overall}
