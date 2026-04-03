# VOX-Scholar Unified System

![CI Status](https://github.com/yashrajkanawade357/vox-scholar-system/actions/workflows/ci.yml/badge.svg)

This is the unified mono-repository combining the anti-vishing audio service (`vox_service`) with the legal compliance application frontend (`scholar_ui`).

### Structure
- `/vox_service`: Backend APIs (FastAPI, Whisper, ChromaDB RAG).
- `/scholar_ui`: Streamlit frontend, AI scanners.
- `/core`: Zero Trust architecture logic.
- `main.py`: Edge orchestration entrypoint.
- `langgraph_brain.py`: LLM pipeline orchestration.
