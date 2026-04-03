"""
BIGDADDY - Step 4: LLM Integration with Ollama
================================================
Connects to the local Ollama instance and provides functions to query
the LLM for legal analysis, leveraging the ChromaDB Legal Brain.
"""

import os
import json
from dotenv import load_dotenv
from ollama import Client
from ingest_data import query_legal_brain

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def get_ollama_client() -> Client:
    """Get an Ollama client instance."""
    return Client(host=OLLAMA_BASE_URL)


def check_ollama_status() -> dict:
    """Check if Ollama is running and which models are available."""
    try:
        client = get_ollama_client()
        models = client.list()
        model_names = [m.model for m in models.models] if models.models else []
        return {
            "status": "online",
            "models": model_names,
            "target_model": OLLAMA_MODEL,
            "target_available": any(OLLAMA_MODEL in m for m in model_names),
        }
    except Exception as e:
        return {
            "status": "offline",
            "error": str(e),
            "models": [],
            "target_model": OLLAMA_MODEL,
            "target_available": False,
        }


def build_analysis_prompt(text: str, legal_context: list[dict]) -> str:
    """
    Build a detailed analysis prompt combining the input text
    with relevant legal context from the Legal Brain.
    """
    context_parts = []
    for i, ctx in enumerate(legal_context):
        meta = ctx["metadata"]
        keywords = json.loads(meta.get("trigger_keywords", "[]"))
        context_parts.append(
            f"--- Legal Reference {i+1} ---\n"
            f"Section: {meta['section_number']} ({meta['legal_source']})\n"
            f"Category: {meta['fraud_category']}\n"
            f"Risk Level: {meta['risk_level']}\n"
            f"Penalty: {meta['penalty_brief']}\n"
            f"Trigger Keywords: {', '.join(keywords[:10])}\n"
            f"Similarity Score: {ctx['similarity_score']}\n"
        )

    legal_context_text = "\n".join(context_parts)

    prompt = f"""You are a Digital Forensic Assistant named BIGDADDY, an expert in Indian cyber fraud detection. Your task is to analyze the following text and determine if it contains elements of cyber fraud under Indian law.

CRITICAL INSTRUCTIONS FOR SCORING & LOGIC:
- Prevent Over-confidence Bias: Only match a legal section if the Similarity Score is above 0.5.
- If the Similarity Score is low or negative, explicitly state: 'Potential match found, but legal evidence is weak.'
- Your CONFIDENCE percentage MUST directly reflect the strength of the similarity score. Never hallucinate a 95% confidence if the context matching score is low!

## RELEVANT LEGAL FRAMEWORK (from your Legal Brain database):
{legal_context_text}

## TEXT TO ANALYZE:
\"\"\"{text}\"\"\"

## YOUR ANALYSIS MUST INCLUDE:

1. **VERDICT**: State clearly whether this text is FRAUDULENT, SUSPICIOUS, or SAFE.
   - FRAUDULENT: Clear indicators of fraud/scam matching legal definitions
   - SUSPICIOUS: Some red flags but not conclusive
   - SAFE: No fraud indicators detected

2. **CONFIDENCE**: Rate your confidence from 0-100%.

3. **FRAUD TYPE**: Identify the specific type(s) of fraud (e.g., Phishing, UPI Fraud, Digital Arrest Scam, Identity Theft, etc.)

4. **MATCHED LEGAL SECTIONS**: List the specific Indian legal sections that apply (e.g., IT Act Section 66C, BNS Section 318).

5. **RED FLAGS**: List specific phrases, patterns, or elements in the text that triggered the fraud detection.

6. **RISK LEVEL**: HIGH / MEDIUM / LOW

7. **RECOMMENDED ACTION**: What should the recipient do (e.g., report to Cyber Crime Helpline 1930, ignore and block, etc.)

8. **EXPLANATION**: A brief, clear explanation in simple language that a common person can understand about why this is/isn't fraud.

Format your response as a structured analysis report. Be precise and cite specific legal provisions."""

    return prompt


def analyze_text(text: str, n_legal_refs: int = 5) -> dict:
    """
    Full analysis pipeline:
    1. Query Legal Brain for relevant legal context
    2. Build enriched prompt
    3. Send to Ollama LLM for analysis
    """
    # Step 1: Get relevant legal context from ChromaDB
    legal_context = query_legal_brain(text, n_results=n_legal_refs)

    # Step 2: Build the analysis prompt
    prompt = build_analysis_prompt(text, legal_context)

    # Step 3: Query Ollama
    client = get_ollama_client()

    try:
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are BIGDADDY, an advanced Indian cyber fraud detection system. "
                        "You analyze text for fraud indicators based on Indian cyber law. "
                        "Always provide structured, actionable analysis."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            options={
                "temperature": 0.2,  # Low temperature for consistent analysis
                "num_predict": 2048,
            },
        )

        analysis_text = response.message.content

        return {
            "success": True,
            "input_text": text,
            "analysis": analysis_text,
            "legal_references": [
                {
                    "section": ctx["metadata"]["section_number"],
                    "source": ctx["metadata"]["legal_source"],
                    "category": ctx["metadata"]["fraud_category"],
                    "risk_level": ctx["metadata"]["risk_level"],
                    "similarity": ctx["similarity_score"],
                }
                for ctx in legal_context
            ],
            "model_used": OLLAMA_MODEL,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "input_text": text,
            "legal_references": [],
        }


def quick_keyword_scan(text: str) -> list[dict]:
    """
    Fast pre-scan using keyword matching against the legal database.
    Does NOT use LLM — purely keyword-based for speed.
    """
    import json as _json

    legal_data_path = os.path.join(os.path.dirname(__file__), "BIGDADDY_Legal_Architecture.json")
    with open(legal_data_path, "r", encoding="utf-8") as f:
        legal_data = _json.load(f)

    text_lower = text.lower()
    matches = []

    for param in legal_data:
        matched_keywords = []
        for kw in param.get("Trigger_Keywords", []):
            if kw.lower() in text_lower:
                matched_keywords.append(kw)

        if matched_keywords:
            matches.append({
                "parameter_id": param["Parameter_ID"],
                "section": param["Section_Number"],
                "source": param["Legal_Source"],
                "category": param["Fraud_Category"],
                "risk_level": param["Risk_Level"],
                "matched_keywords": matched_keywords,
                "match_count": len(matched_keywords),
            })

    # Sort by number of keyword matches (descending)
    matches.sort(key=lambda x: x["match_count"], reverse=True)
    return matches


if __name__ == "__main__":
    print("=" * 60)
    print("  BIGDADDY LLM Engine - Status Check")
    print("=" * 60)

    status = check_ollama_status()
    print(f"\n  Ollama Status: {status['status']}")
    print(f"  Target Model: {status['target_model']}")
    print(f"  Available: {status['target_available']}")
    if status["models"]:
        print(f"  Installed Models: {', '.join(status['models'])}")

    if status["target_available"]:
        print("\n" + "-" * 60)
        print("  Running Test Analysis...")
        print("-" * 60)

        test_text = "Dear customer, your SBI account has been blocked. Click here to update KYC immediately: http://sbi-update-kyc.xyz. Share your OTP to verify."
        print(f"\n  Test Input: \"{test_text}\"\n")

        # Quick keyword scan
        kw_results = quick_keyword_scan(test_text)
        print(f"  Keyword Matches: {len(kw_results)} legal sections triggered")
        for r in kw_results[:3]:
            print(f"    - {r['section']}: {r['matched_keywords']}")

        # Full LLM analysis
        print("\n  Running LLM analysis (this may take a moment)...")
        result = analyze_text(test_text)
        if result["success"]:
            print(f"\n{result['analysis']}")
        else:
            print(f"\n  Error: {result['error']}")
    else:
        print(f"\n  [!] Model '{status['target_model']}' not available. Pull it with: ollama pull {status['target_model']}")
