RISK_CATEGORIES = {
    "high": ["biometric", "legal", "medical"],
    "medium": ["employment", "education"],
    "low": ["creative", "personal"]
}

def classify_risk(text, ai_prob):
    for category, keywords in RISK_CATEGORIES.items():
        if any(keyword in text.lower() for keyword in keywords) and ai_prob > 0.7:
            return category
    return "low"