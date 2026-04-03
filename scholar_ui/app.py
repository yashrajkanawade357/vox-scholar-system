"""
BIGDADDY - Step 7: Streamlit Application
==========================================
Complete fraud scanner UI with testing & feedback loop.
"""

import streamlit as st
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Must be first Streamlit command
st.set_page_config(
    page_title="BIGDADDY - Cyber Fraud Scanner",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
:root { --bg-dark: #0a0a0f; --card-bg: #12121a; --accent: #00d4ff; --accent2: #7c3aed;
        --danger: #ef4444; --warning: #f59e0b; --success: #10b981; --text: #e2e8f0; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0a0f 100%); }
h1, h2, h3 { font-family: 'Inter', sans-serif !important; }
.big-title { font-size: 3rem; font-weight: 900; background: linear-gradient(135deg, #00d4ff, #7c3aed, #00d4ff);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center;
             animation: glow 3s ease-in-out infinite alternate; margin-bottom: 0; }
@keyframes glow { from { filter: brightness(1); } to { filter: brightness(1.3); } }
.subtitle { text-align: center; color: #64748b; font-size: 1.1rem; margin-top: -10px; margin-bottom: 30px; }
.risk-high { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 15px 25px;
             border-radius: 12px; font-weight: 700; font-size: 1.3rem; text-align: center; }
.risk-medium { background: linear-gradient(135deg, #f59e0b, #d97706); color: #1a1a1a; padding: 15px 25px;
               border-radius: 12px; font-weight: 700; font-size: 1.3rem; text-align: center; }
.risk-low { background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 15px 25px;
            border-radius: 12px; font-weight: 700; font-size: 1.3rem; text-align: center; }
.stat-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
             border-radius: 16px; padding: 20px; text-align: center; backdrop-filter: blur(10px); }
.stat-number { font-size: 2.2rem; font-weight: 900; font-family: 'JetBrains Mono', monospace; }
.scan-result { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);
               border-radius: 16px; padding: 25px; margin: 10px 0; }
.legal-ref { background: rgba(124,58,237,0.1); border-left: 4px solid #7c3aed; padding: 12px 16px;
             border-radius: 0 8px 8px 0; margin: 6px 0; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)


def init_session():
    if "scan_history" not in st.session_state:
        st.session_state.scan_history = []
    if "db_ingested" not in st.session_state:
        st.session_state.db_ingested = False


def check_system_status():
    """Check all system components."""
    status = {}
    # ChromaDB
    try:
        from ingest_data import get_chroma_client, COLLECTION_NAME
        client = get_chroma_client()
        col = client.get_collection(COLLECTION_NAME)
        status["chromadb"] = {"ok": True, "docs": col.count()}
    except Exception:
        status["chromadb"] = {"ok": False, "docs": 0}
    # Ollama
    try:
        from llm_engine import check_ollama_status
        oll = check_ollama_status()
        status["ollama"] = {"ok": oll["status"] == "online", "model_ready": oll["target_available"],
                            "model": oll["target_model"], "models": oll.get("models", [])}
    except Exception as e:
        status["ollama"] = {"ok": False, "model_ready": False, "error": str(e)}
    # APIs
    vt_key = os.getenv("VIRUSTOTAL_API_KEY", "")
    gsb_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "")
    status["virustotal"] = {"configured": bool(vt_key) and vt_key != "your_virustotal_api_key_here"}
    status["safe_browsing"] = {"configured": bool(gsb_key) and gsb_key != "your_google_safe_browsing_key_here"}
    return status


def render_sidebar(status):
    with st.sidebar:
        st.markdown("## ⚙️ System Status")
        # ChromaDB
        if status["chromadb"]["ok"]:
            st.success(f"✅ Legal Brain: {status['chromadb']['docs']} laws loaded")
        else:
            st.error("❌ Legal Brain: Not ingested")
            if st.button("🧠 Ingest Legal Data Now", key="ingest_btn"):
                with st.spinner("Ingesting legal data into ChromaDB..."):
                    from ingest_data import ingest_legal_data
                    ingest_legal_data(force_reingest=True)
                    st.session_state.db_ingested = True
                st.rerun()
        # Ollama
        if status["ollama"]["ok"] and status["ollama"]["model_ready"]:
            st.success(f"✅ LLM: {status['ollama']['model']} ready")
        elif status["ollama"]["ok"]:
            st.warning(f"⚠️ Ollama online, model '{status['ollama']['model']}' not pulled")
            if status["ollama"].get("models"):
                st.info(f"Available: {', '.join(status['ollama']['models'])}")
        else:
            st.error("❌ Ollama: Offline")
        # APIs
        st.markdown("---")
        st.markdown("### 🔗 External APIs")
        st.write("🔍 VirusTotal:", "✅ Ready" if status["virustotal"]["configured"] else "⚠️ No key")
        st.write("🛡️ Safe Browsing:", "✅ Ready" if status["safe_browsing"]["configured"] else "⚠️ No key")
        st.markdown("---")
        st.markdown("### 📊 Session Stats")
        st.metric("Scans This Session", len(st.session_state.scan_history))
        fraud_count = sum(1 for s in st.session_state.scan_history if s.get("overall_risk") == "HIGH")
        st.metric("Frauds Detected", fraud_count)


def render_scan_tab(status):
    st.markdown('<p class="big-title">🛡️ BIGDADDY</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Cyber Fraud Scanner • Indian Legal Framework</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-card"><div class="stat-number" style="color:#00d4ff">30</div><div>Legal Sections</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:#7c3aed">{len(st.session_state.scan_history)}</div><div>Scans Done</div></div>', unsafe_allow_html=True)
    with col3:
        fraud_count = sum(1 for s in st.session_state.scan_history if s.get("overall_risk") == "HIGH")
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:#ef4444">{fraud_count}</div><div>Frauds Found</div></div>', unsafe_allow_html=True)
    with col4:
        model_name = status["ollama"].get("model", "N/A")
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:#10b981; font-size:1.2rem">{model_name}</div><div>AI Model</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Input area
    input_text = st.text_area("📝 Paste suspicious text, message, or URL to scan:",
                              height=150, placeholder="Example: Dear customer, your SBI account has been blocked. Click http://sbi-update.xyz to update KYC. Share OTP to verify.")

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        scan_full = st.button("🔍 Full AI Scan", type="primary", use_container_width=True)
    with col_b:
        scan_quick = st.button("⚡ Quick Keyword Scan", use_container_width=True)
    with col_c:
        scan_url = st.button("🌐 URL Check Only", use_container_width=True)

    if scan_full and input_text:
        with st.spinner("🧠 Running full AI analysis... This may take a moment."):
            from scanner import scan_input
            result = scan_input(input_text)
            result["scan_type"] = "full"
            st.session_state.scan_history.append(result)
            render_full_result(result)

    elif scan_quick and input_text:
        with st.spinner("⚡ Running keyword scan..."):
            from scanner import parse_input, extract_url_features
            from llm_engine import quick_keyword_scan
            parsed = parse_input(input_text)
            kw_hits = quick_keyword_scan(input_text)
            url_results = [extract_url_features(u) for u in parsed.get("urls", [])]
            risk = "HIGH" if len(kw_hits) >= 3 else "MEDIUM" if kw_hits else "LOW"
            result = {"parsed_input": parsed, "keyword_hits": kw_hits, "url_analyses": url_results,
                      "overall_risk": risk, "scan_type": "quick"}
            st.session_state.scan_history.append(result)
            render_quick_result(result)

    elif scan_url and input_text:
        with st.spinner("🌐 Checking URLs..."):
            from scanner import parse_input, extract_url_features
            from api_checker import check_url_all_sources
            parsed = parse_input(input_text)
            if parsed["urls"]:
                for url in parsed["urls"]:
                    features = extract_url_features(url)
                    external = check_url_all_sources(url)
                    st.markdown(f"### 🔗 URL: `{url}`")
                    risk_class = f"risk-{features['risk_level'].lower()}"
                    st.markdown(f'<div class="{risk_class}">Risk: {features["risk_level"]} (Score: {features["suspicion_score"]}/100)</div>', unsafe_allow_html=True)
                    if features["suspicion_reasons"]:
                        st.markdown("**⚠️ Red Flags:**")
                        for r in features["suspicion_reasons"]:
                            st.warning(r)
                    st.json(external)
            else:
                st.warning("No URLs found in the input text.")

    elif (scan_full or scan_quick or scan_url) and not input_text:
        st.warning("Please enter text or URL to scan.")


def render_full_result(result):
    st.markdown("---")
    st.markdown("## 📋 Scan Results")
    risk = result.get("overall_risk", "UNKNOWN")
    risk_class = f"risk-{risk.lower()}" if risk in ["HIGH", "MEDIUM", "LOW"] else "risk-medium"
    st.markdown(f'<div class="{risk_class}">⚡ OVERALL RISK: {risk}</div>', unsafe_allow_html=True)

    # Keyword hits
    kw = result.get("text_classification", {}).get("keyword_scan", {})
    if kw.get("hits"):
        st.markdown("### 🔑 Keyword Matches")
        for hit in kw["hits"][:5]:
            st.markdown(f'<div class="legal-ref"><strong>{hit["section"]}</strong> ({hit["source"]}) — '
                        f'Category: {hit["category"]} | Risk: {hit["risk_level"]}<br/>'
                        f'Matched: <code>{", ".join(hit["matched_keywords"])}</code></div>', unsafe_allow_html=True)

    # LLM Analysis
    llm = result.get("text_classification", {}).get("llm_analysis", {})
    if llm.get("success"):
        st.markdown("### 🧠 AI Analysis")
        st.markdown(f'<div class="scan-result">{llm["analysis"]}</div>', unsafe_allow_html=True)
        if llm.get("legal_references"):
            st.markdown("### ⚖️ Legal References Used")
            for ref in llm["legal_references"]:
                st.markdown(f'<div class="legal-ref"><strong>{ref["section"]}</strong> ({ref["source"]}) — '
                            f'{ref["category"]} | Similarity: {ref["similarity"]}</div>', unsafe_allow_html=True)
    elif llm.get("error"):
        st.error(f"LLM Error: {llm['error']}")

    # URL analyses
    if result.get("url_analyses"):
        st.markdown("### 🌐 URL Analysis")
        for ua in result["url_analyses"]:
            risk_class = f"risk-{ua['risk_level'].lower()}"
            st.markdown(f"**URL:** `{ua['url']}`")
            st.markdown(f'<div class="{risk_class}">URL Risk: {ua["risk_level"]} (Score: {ua["suspicion_score"]}/100)</div>', unsafe_allow_html=True)
            if ua.get("suspicion_reasons"):
                for r in ua["suspicion_reasons"]:
                    st.warning(r)


def render_quick_result(result):
    st.markdown("---")
    st.markdown("## ⚡ Quick Scan Results")
    risk = result.get("overall_risk", "UNKNOWN")
    risk_class = f"risk-{risk.lower()}" if risk in ["HIGH", "MEDIUM", "LOW"] else "risk-medium"
    st.markdown(f'<div class="{risk_class}">⚡ RISK LEVEL: {risk}</div>', unsafe_allow_html=True)

    hits = result.get("keyword_hits", [])
    if hits:
        st.markdown(f"### 🔑 {len(hits)} Legal Section(s) Triggered")
        for hit in hits:
            st.markdown(f'<div class="legal-ref"><strong>{hit["section"]}</strong> ({hit["source"]})<br/>'
                        f'Category: {hit["category"]} | Risk: {hit["risk_level"]}<br/>'
                        f'Keywords: <code>{", ".join(hit["matched_keywords"])}</code></div>', unsafe_allow_html=True)
    else:
        st.success("✅ No fraud keywords detected in the text.")

    if result.get("url_analyses"):
        st.markdown("### 🌐 URLs Found")
        for ua in result["url_analyses"]:
            rc = f"risk-{ua['risk_level'].lower()}"
            st.markdown(f'<div class="{rc}">URL: {ua["url"]} — Risk: {ua["risk_level"]}</div>', unsafe_allow_html=True)


def render_test_tab():
    st.markdown("## 🧪 Testing & Feedback Loop")
    st.markdown("Run predefined test cases to validate the scanner's accuracy.")

    test_cases = [
        {"label": "🔴 Phishing SMS — KYC Update", "text": "Dear SBI customer, your KYC has expired. Update immediately to avoid account block: http://sbi-kyc-verify.xyz. Enter OTP to confirm.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Digital Arrest Scam", "text": "This is CBI officer calling. FIR registered against your Aadhaar number for money laundering. You are under digital arrest. Transfer ₹2,50,000 to avoid arrest warrant. Do not tell anyone or you will be arrested.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 UPI Fraud — Collect Request", "text": "I am sending you ₹5000 refund on PhonePe. Approve the collect request and enter your UPI PIN to receive the money immediately.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Investment Scam", "text": "Join our WhatsApp trading group! Guaranteed 300% returns in 30 days. Our AI algorithm trading never fails. Invest minimum ₹10,000. Click link to join: http://crypto-profit-assured.top",
         "expected": "FRAUDULENT"},
        {"label": "🔴 APK Malware", "text": "You are invited to Rahul & Priya's wedding! Download the invitation card: wedding-card.apk. Install from this link: http://192.168.45.12/invite.apk",
         "expected": "FRAUDULENT"},
        {"label": "🟢 Legitimate — Meeting Reschedule", "text": "Hi team, the project review meeting has been moved to 4 PM tomorrow. Please update your calendars. Thanks, Rahul.",
         "expected": "SAFE"},
        {"label": "🟢 Legitimate — Delivery Update", "text": "Your Amazon order #402-1234567 has been shipped. Expected delivery: April 5. Track at amazon.in/track",
         "expected": "SAFE"},
        {"label": "🟡 Suspicious — Vague Offer", "text": "Congratulations! You have been selected for a special offer. Call us at 9876543210 for more details about your prize.",
         "expected": "SUSPICIOUS"},
        {"label": "🔴 Extortion / Sextortion", "text": "We have recorded your video call. Send INR 50,000 immediately or your morphed pictures will be sent to your family and friends. We share your private photos. Pay to delete video.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Loan App Extortion", "text": "Your instant loan approval was processed. However, your EMI is overdue! Repay immediately or we call your contacts. We have hacked your contact list and will ruin your life.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Electricity Disconnection Scam", "text": "Dear consumer, your power disconnect tonight at 9.30 PM from electricity office because your previous month bill was not updated. Please call the electricity officer on 9876543210 immediately.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Fake Customer Care Helpline", "text": "Looking for the refund support number? Dial this for reversal. Our customer care helpline agent will guide you to download screen share / AnyDesk support to process your refund.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Customs / Courier Scam", "text": "This is FedEx. Your parcel to London has been seized. FedEx parcel seized by customs drug interception. Urgent customs clearance fee of ₹45,000 is required or the narcotics department will arrest you.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Matrimonial Scam", "text": "My dear, I am sending an expensive gift from London for you. But it is stuck at airport. Please transfer ₹1,50,000 to the customs account for customs clearance for gift so I can come to India.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Work-From-Home Task Fraud", "text": "Part-time work from home! Earn ₹3,000 daily by simply like YouTube videos. Just deposit to unlock earnings of your prepaid task. Join our telegram task group now.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Privacy Violation / Hidden Camera", "text": "We possess non-consensual image sharing material and voyeurism recordings of you. The recording without permission was done by our hidden camera. Pay or we leak.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Ponzi Scheme", "text": "Join our multi level marketing group! Guaranteed 10% daily return on your investment in our high yield investment program. Refer 3 friends chain to earn 5x crypto deposit scheme bonus.",
         "expected": "FRAUDULENT"},
        {"label": "🔴 Credit Card Reward Points Scam", "text": "Your HDFC reward points expiring today! Redeem credit card points instantly. Click to claim points and convert points to cash directly into your bank account via this link.",
         "expected": "FRAUDULENT"},
    ]

    if st.button("🚀 Run All Tests", type="primary"):
        from llm_engine import quick_keyword_scan
        from scanner import parse_input, extract_url_features

        results_table = []
        progress = st.progress(0)

        for i, tc in enumerate(test_cases):
            progress.progress((i + 1) / len(test_cases))
            parsed = parse_input(tc["text"])
            kw_hits = quick_keyword_scan(tc["text"])
            url_results = [extract_url_features(u) for u in parsed.get("urls", [])]

            # Determine detected risk
            risks = []
            if len(kw_hits) >= 3:
                risks.append("HIGH")
            elif kw_hits:
                risks.append("MEDIUM")
            for ua in url_results:
                risks.append(ua["risk_level"])
            detected = "HIGH" if "HIGH" in risks else "MEDIUM" if "MEDIUM" in risks else "LOW"

            # Map to verdict
            if detected == "HIGH":
                verdict = "FRAUDULENT"
            elif detected == "MEDIUM":
                verdict = "SUSPICIOUS"
            else:
                verdict = "SAFE"

            match = "✅" if verdict == tc["expected"] else "❌"
            results_table.append({
                "Test": tc["label"],
                "Expected": tc["expected"],
                "Detected": verdict,
                "Keywords": len(kw_hits),
                "URLs": len(parsed.get("urls", [])),
                "Match": match,
            })

        st.markdown("### 📊 Test Results")
        st.dataframe(results_table, use_container_width=True)
        correct = sum(1 for r in results_table if r["Match"] == "✅")
        total = len(results_table)
        acc = round(correct / total * 100, 1)
        color = "success" if acc >= 75 else "warning" if acc >= 50 else "error"
        getattr(st, color)(f"Accuracy: {correct}/{total} ({acc}%)")
    else:
        st.markdown("### 📝 Test Cases")
        for tc in test_cases:
            with st.expander(tc["label"]):
                st.text(tc["text"])
                st.caption(f"Expected: {tc['expected']}")


def render_history_tab():
    st.markdown("## 📜 Scan History")
    if not st.session_state.scan_history:
        st.info("No scans yet. Go to the Scanner tab to start scanning.")
        return
    for i, scan in enumerate(reversed(st.session_state.scan_history)):
        risk = scan.get("overall_risk", "UNKNOWN")
        emoji = "🔴" if risk == "HIGH" else "🟡" if risk == "MEDIUM" else "🟢"
        text_preview = scan.get("parsed_input", {}).get("text", "N/A")[:100]
        scan_type = scan.get("scan_type", "unknown")
        with st.expander(f"{emoji} [{risk}] {text_preview}... ({scan_type} scan)"):
            st.json(scan)
    if st.button("🗑️ Clear History"):
        st.session_state.scan_history = []
        st.rerun()


# ── Main ──
def main():
    init_session()
    status = check_system_status()
    render_sidebar(status)

    tab1, tab2, tab3 = st.tabs(["🔍 Scanner", "🧪 Testing Lab", "📜 History"])
    with tab1:
        render_scan_tab(status)
    with tab2:
        render_test_tab()
    with tab3:
        render_history_tab()


if __name__ == "__main__":
    main()
