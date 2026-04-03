"""
VOX Service — Logic Module
Project BigDaddy | Anti-Vishing System

Coordinates local audio transcription (Whisper) and semantic
analysis (Llama 3 + ChromaDB RAG) to detect scams based on
Indian legal context.

- 100% offline — no API keys required
- Local Whisper "base" model
- Local Ollama `llama3` for LLM inference
"""

import warnings
import requests
import whisper
import re
from rag_pipeline import query_legal

# Suppress FP16 warnings on CPU from Whisper
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# ──────────────────────────────────────────────
# Global Configuration & Cached Models
# ──────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

# Load the model once to avoid re-loading on each call
# It will automatically download 'base.pt' on the first run (74 MB)
print("⏳ Loading Whisper base model into memory...")
try:
    _whisper_model = whisper.load_model("base")
    print("✅ Whisper model loaded successfully.")
except Exception as e:
    print(f"⚠️ Error loading whisper model: {e}")
    _whisper_model = None


# ──────────────────────────────────────────────
# Audio Transcription
# ──────────────────────────────────────────────
def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe a local audio file using OpenAI Whisper (local).
    """
    if _whisper_model is None:
        raise RuntimeError("Whisper model was not loaded. Check dependencies or paths.")
    
    print(f"🎤 Transcribing audio: {audio_path}")
    result = _whisper_model.transcribe(audio_path)
    text = result.get("text", "").strip()
    return text


# ──────────────────────────────────────────────
# Call Analysis via Ollama (Llama 3)
# ──────────────────────────────────────────────
def analyze_text_only(transcription_text: str) -> dict:
    """
    1. Queries local RAG DB for relevant Indian legal context
    2. Builds specific 'Fatherly Advisor' prompt
    3. Calls local Ollama llama3 model
    4. Returns categorized scam analysis dict
    """
    if not transcription_text.strip():
        return {
            "transcription": "",
            "risk_level": "UNKNOWN",
            "red_flags": "None",
            "what_to_do": "Audio/Text could not be analyzed or was empty.",
            "legal_note": "N/A"
        }

    # 1. Get legal context
    print("🔍 Fetching legal context from ChromaDB...")
    legal_results = query_legal(transcription_text, top_k=3)
    
    context_text = "\n\n".join([f"Source ({r['source']}):\n{r['text']}" for r in legal_results])
    if not context_text:
        context_text = "No specific legal directives found. Use general Indian banking safety principles."

    # 2. Build the prompt
    prompt = f"""You are a "Fatherly Advisor" — a calm, protective figure helping elderly Indians detect phone scams.

CONTEXT (Indian Legal Info & Advisories):
{context_text}

CALL TRANSCRIPTION:
{transcription_text}

INSTRUCTIONS:
Analyze the transcription against the context provided. Detect the following red flags:
1. Impersonation of bank, CBI, TRAI, police, or government officials
2. Urgency and pressure tactics
3. Requests for OTP, PIN, Aadhaar, or card numbers
4. Threats of arrest or account blocking
5. Too good to be true offers

You must respond in EXACTLY this format, with no extra conversation or markdown:
RISK LEVEL: [LOW / MEDIUM / HIGH / CRITICAL]
RED FLAGS FOUND: [list each one or "None"]
WHAT TO DO: [simple advice in 2-3 sentences in simple English]
LEGAL NOTE: [relevant Indian law that applies]
"""

    print("🧠 Sending prompt to local Ollama (Llama 3)...")
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    # 3. Call Ollama
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        llm_output = response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Ollama: {e}")
        llm_output = "RISK LEVEL: UNKNOWN\nRED FLAGS FOUND: Error\nWHAT TO DO: Could not reach AI server.\nLEGAL NOTE: N/A"

    # 4. Parse the output exactly as requested
    parsed_result = {
        "transcription": transcription_text,
        "risk_level": "UNKNOWN",
        "red_flags": "None",
        "what_to_do": "Check the transcription manually.",
        "legal_note": "None"
    }

    # Regex patterns to extract fields based on exact formatting request
    risk_match = re.search(r"RISK LEVEL:\s*(.*?)(?=\nRED FLAGS)", llm_output, flags=re.DOTALL | re.IGNORECASE)
    flags_match = re.search(r"RED FLAGS FOUND:\s*(.*?)(?=\nWHAT TO DO)", llm_output, flags=re.DOTALL | re.IGNORECASE)
    what_match = re.search(r"WHAT TO DO:\s*(.*?)(?=\nLEGAL NOTE)", llm_output, flags=re.DOTALL | re.IGNORECASE)
    legal_match = re.search(r"LEGAL NOTE:\s*(.*)", llm_output, flags=re.DOTALL | re.IGNORECASE)

    if risk_match: parsed_result["risk_level"] = risk_match.group(1).strip()
    if flags_match: parsed_result["red_flags"] = flags_match.group(1).strip()
    if what_match: parsed_result["what_to_do"] = what_match.group(1).strip()
    if legal_match: parsed_result["legal_note"] = legal_match.group(1).strip()

    print(f"✅ Analysis complete. Risk Level: {parsed_result['risk_level']}")
    
    return parsed_result


def analyze_call(audio_path: str) -> dict:
    """
    1. Transcribes audio
    2. Passes transcription to analyze_text_only
    """
    transcription = transcribe_audio(audio_path)
    return analyze_text_only(transcription)


# ──────────────────────────────────────────────
# Manual Test Execution
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vox_logic.py <path_to_audio_file>")
        print("Expected a valid audio file (e.g., .wav, .mp3, .m4a)")
        sys.exit(1)
        
    test_audio = sys.argv[1]
    
    print("=" * 60)
    print("🔷 VOX Service — Logic Pipeline Test")
    print("=" * 60)
    
    result = analyze_call(test_audio)
    
    print("\n" + "=" * 60)
    print("📊 RESULT DICTIONARY:")
    for k, v in result.items():
        print(f"\n[{k.upper()}]\n{v}")
    print("=" * 60)
