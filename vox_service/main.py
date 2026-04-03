"""
VOX Service — Main FastAPI Server
Project BigDaddy | Anti-Vishing System

Exposes 4 endpoints for audio transcription, RAG queries,
and text analysis to detect phone scams. Connects directly
to local `vox_logic.py` and `rag_pipeline.py`.
"""

import os
import uuid
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from vox_logic import analyze_call, analyze_text_only
from rag_pipeline import query_legal

# ──────────────────────────────────────────────
# Initialization
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "=" * 60)
    print("🚀 VOX Service started — Llama 3 ready on port 8000")
    print("=" * 60 + "\n")
    yield

app = FastAPI(title="Project BigDaddy VOX Service", lifespan=lifespan)

# Allow all origins (CORS)
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
class QueryRequest(BaseModel):
    question: str

class TextRequest(BaseModel):
    text: str

# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Returns basic health status of the API."""
    return {
        "status": "VOX service running", 
        "model": "llama3", 
        "service": "BigDaddy VOX"
    }


@app.post("/analyze-audio")
async def process_audio(file: UploadFile = File(...)):
    """
    Accepts an audio file upload, saves it temporarily, and runs
    the full local transcription + LLM analysis pipeline.
    """
    # Verify extension simply
    if not (file.filename.endswith(".wav") or file.filename.endswith(".mp3") or file.filename.endswith(".m4a")):
        raise HTTPException(status_code=400, detail="Only .wav, .mp3, and .m4a files are supported.")

    # Generate a safe temporary filepath
    ext = file.filename.split('.')[-1]
    tmp_path = f"tmp_{uuid.uuid4().hex}.{ext}"
    
    try:
        # Save file to disk
        with open(tmp_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        print(f"\n📦 Received audio file: {file.filename} -> saved as {tmp_path}")
        
        # Run full analysis
        result = analyze_call(tmp_path)
        return result
        
    except Exception as e:
        print(f"❌ Error during /analyze-audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Clean up temporary audio file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            print(f"🗑️ Cleaned up temporary file: {tmp_path}")


@app.post("/query-legal")
def query_legal_docs(request: QueryRequest):
    """
    Query the internal Indian Legal ChromaDB pipeline directly.
    """
    try:
        results = query_legal(request.question, top_k=3)
        return {
            "question": request.question,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-text")
def process_text(request: TextRequest):
    """
    Bypass the transcription module and directly analyze raw text 
    against the RAG legal context using Llama 3.
    """
    try:
        print(f"\n📝 Received raw text for analysis: {request.text[:100]}...")
        result = analyze_text_only(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ──────────────────────────────────────────────
# Main Server Execution
# ──────────────────────────────────────────────
if __name__ == "__main__":
    # Start the local uvicorn server unconditionally
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
