"""
BIGDADDY - Step 5: Code Scanner Functions
==========================================
Core scanning logic:
  - Input Parser: Receives text or URL
  - Text Classifier: Sends text to LLM for fraud classification
  - URL Checker: Extracts and processes URLs for Step 6
"""

import re
from urllib.parse import urlparse
from llm_engine import analyze_text, quick_keyword_scan


def parse_input(raw_input: str) -> dict:
    """
    Parse raw user input to determine its type and extract components.
    Returns structured data with type classification and extracted elements.
    """
    raw_input = raw_input.strip()

    if not raw_input:
        return {"type": "empty", "text": "", "urls": [], "error": "Empty input provided."}

    # Extract all URLs from the text
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, raw_input)

    # Also catch URLs without http/https prefix
    domain_pattern = r'(?<!\S)(?:www\.)?[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s]*)?(?!\S)'
    bare_domains = re.findall(domain_pattern, raw_input)
    for d in bare_domains:
        full_url = f"http://{d}" if not d.startswith("http") else d
        if full_url not in urls:
            urls.append(full_url)

    # Determine input type
    if len(urls) > 0 and len(raw_input.replace(urls[0], "").strip()) < 10:
        input_type = "url_only"
    elif urls:
        input_type = "text_with_urls"
    else:
        input_type = "text_only"

    # Extract email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, raw_input)

    # Extract phone numbers (Indian format)
    phone_pattern = r'(?:\+91[\-\s]?)?(?:0)?[6-9]\d{9}'
    phones = re.findall(phone_pattern, raw_input)

    # Extract UPI IDs
    upi_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z]{2,}'
    potential_upis = [u for u in re.findall(upi_pattern, raw_input) if u not in emails]

    return {
        "type": input_type,
        "text": raw_input,
        "urls": urls,
        "emails": emails,
        "phones": phones,
        "upi_ids": potential_upis,
        "word_count": len(raw_input.split()),
        "char_count": len(raw_input),
    }


def classify_text(text: str) -> dict:
    """
    Full text classification pipeline:
    1. Quick keyword scan (fast, no LLM)
    2. Full LLM analysis with legal context
    Returns combined results.
    """
    # Phase 1: Quick keyword pre-scan
    keyword_hits = quick_keyword_scan(text)
    keyword_risk = "LOW"
    if len(keyword_hits) >= 3:
        keyword_risk = "HIGH"
    elif len(keyword_hits) >= 1:
        keyword_risk = "MEDIUM"

    # Phase 2: Full LLM analysis
    llm_result = analyze_text(text)

    return {
        "keyword_scan": {
            "hits": keyword_hits,
            "total_matches": len(keyword_hits),
            "pre_scan_risk": keyword_risk,
        },
        "llm_analysis": llm_result,
        "combined_risk": keyword_risk if not llm_result["success"] else keyword_risk,
    }


def extract_url_features(url: str) -> dict:
    """
    Extract suspicious features from a URL for fraud detection.
    """
    try:
        parsed = urlparse(url if url.startswith("http") else f"http://{url}")
    except Exception:
        return {"url": url, "valid": False, "error": "Invalid URL format"}

    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    # Whitelisted Domains Check
    WHITELISTED_DOMAINS = ["google.com", "www.google.com", "rbi.org.in", "gov.in", "apple.com", "amazon.in", "flipkart.com", "linkedin.com"]
    is_whitelisted = any(domain == wd or domain.endswith("." + wd) for wd in WHITELISTED_DOMAINS)
    
    if is_whitelisted:
        return {
            "url": url,
            "valid": True,
            "domain": domain,
            "safe_whitelisted": True,
            "suspicion_score": 0,
            "suspicion_reasons": [],
            "risk_level": "LOW",
        }

    # Suspicious TLD patterns
    suspicious_tlds = [".xyz", ".top", ".click", ".link", ".buzz", ".info", ".tk", ".ml", ".ga", ".cf", ".gq"]
    has_suspicious_tld = any(domain.endswith(tld) for tld in suspicious_tlds)

    # Check for brand impersonation in domain
    impersonated_brands = [
        "sbi", "hdfc", "icici", "axis", "pnb", "bob", "kotak", "rbi",
        "paytm", "phonepe", "gpay", "upi", "npci", "uidai", "aadhaar",
        "incometax", "cbi", "police", "gov", "nic", "india"
    ]
    brand_in_domain = [b for b in impersonated_brands if b in domain]

    # Check for IP-based URL
    ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    is_ip_based = bool(re.match(ip_pattern, domain))

    # Check for excessive subdomains
    subdomain_count = len(domain.split(".")) - 2

    # Check for suspicious path keywords
    suspicious_paths = ["login", "verify", "update", "secure", "account", "kyc", "otp", "confirm", "bank"]
    suspicious_path_matches = [p for p in suspicious_paths if p in path]

    # Check URL length (phishing URLs tend to be long)
    is_long_url = len(url) > 75

    # Check for @ symbol (URL obfuscation)
    has_at_symbol = "@" in url

    # Check for data URI schemes
    is_data_uri = url.lower().startswith("data:")

    # Calculate suspicion score
    suspicion_score = 0
    suspicion_reasons = []

    if has_suspicious_tld:
        suspicion_score += 30
        suspicion_reasons.append(f"Suspicious TLD detected")
    if brand_in_domain:
        suspicion_score += 25
        suspicion_reasons.append(f"Brand impersonation: {', '.join(brand_in_domain)}")
    if is_ip_based:
        suspicion_score += 20
        suspicion_reasons.append("IP-based URL (no domain name)")
    if subdomain_count > 2:
        suspicion_score += 15
        suspicion_reasons.append(f"Excessive subdomains ({subdomain_count})")
    if suspicious_path_matches:
        suspicion_score += 15
        suspicion_reasons.append(f"Suspicious path keywords: {', '.join(suspicious_path_matches)}")
    if is_long_url:
        suspicion_score += 10
        suspicion_reasons.append("Unusually long URL")
    if has_at_symbol:
        suspicion_score += 20
        suspicion_reasons.append("Contains @ symbol (URL obfuscation)")
    if is_data_uri:
        suspicion_score += 25
        suspicion_reasons.append("Data URI scheme detected")

    return {
        "url": url,
        "valid": True,
        "domain": domain,
        "path": path,
        "scheme": parsed.scheme,
        "has_suspicious_tld": has_suspicious_tld,
        "brand_impersonation": brand_in_domain,
        "is_ip_based": is_ip_based,
        "subdomain_count": subdomain_count,
        "suspicious_path_keywords": suspicious_path_matches,
        "is_long_url": is_long_url,
        "has_at_symbol": has_at_symbol,
        "suspicion_score": min(suspicion_score, 100),
        "suspicion_reasons": suspicion_reasons,
        "risk_level": "HIGH" if suspicion_score >= 50 else "MEDIUM" if suspicion_score >= 25 else "LOW",
    }


def scan_input(raw_input: str) -> dict:
    """
    Master scanning function that orchestrates the full pipeline:
    1. Parse input
    2. Classify text
    3. Check URLs
    Returns a comprehensive scan report.
    """
    # Step 1: Parse
    parsed = parse_input(raw_input)

    if parsed["type"] == "empty":
        return {"error": "Empty input", "parsed": parsed}

    # Step 2: Classify text
    text_classification = classify_text(parsed["text"])

    # Step 3: Analyze URLs
    url_analyses = []
    for url in parsed.get("urls", []):
        url_analysis = extract_url_features(url)
        url_analyses.append(url_analysis)

    # Step 4: Compute overall risk
    risks = []
    if text_classification["keyword_scan"]["total_matches"] > 0:
        risks.append(text_classification["keyword_scan"]["pre_scan_risk"])
    for ua in url_analyses:
        risks.append(ua["risk_level"])

    if "HIGH" in risks:
        overall_risk = "HIGH"
    elif "MEDIUM" in risks:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    return {
        "parsed_input": parsed,
        "text_classification": text_classification,
        "url_analyses": url_analyses,
        "overall_risk": overall_risk,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("  BIGDADDY Scanner - Test Run")
    print("=" * 60)

    test_inputs = [
        "Dear customer, your SBI account has been blocked. Click here to update KYC: http://sbi-kyc-update.xyz/verify",
        "You have won a lottery of ₹50,00,000! Click http://192.168.1.1/claim to claim your prize. Share OTP to verify.",
        "Hi Aayush, the team meeting is rescheduled to 3 PM tomorrow. Please confirm.",
    ]

    for i, test in enumerate(test_inputs):
        print(f"\n{'─' * 60}")
        print(f"  Test {i+1}: \"{test[:80]}...\"")
        print(f"{'─' * 60}")

        parsed = parse_input(test)
        print(f"  Type: {parsed['type']}")
        print(f"  URLs: {parsed['urls']}")
        print(f"  Emails: {parsed['emails']}")

        if parsed["urls"]:
            for url in parsed["urls"]:
                features = extract_url_features(url)
                print(f"  URL Risk [{features['risk_level']}]: {url}")
                if features["suspicion_reasons"]:
                    for reason in features["suspicion_reasons"]:
                        print(f"    ⚠ {reason}")

        kw = quick_keyword_scan(test)
        print(f"  Keyword Hits: {len(kw)} legal sections")
        for k in kw[:2]:
            print(f"    - {k['section']}: {k['matched_keywords']}")
