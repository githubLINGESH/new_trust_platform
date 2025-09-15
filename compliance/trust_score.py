# compliance/trust_score.py

import logging

logger = logging.getLogger(__name__)

def calculate_trust_score(sentiment: dict, compliance: dict, fact_check: dict) -> dict:
    """
    Calculate a trust score (0-100) based on sentiment neutrality,
    compliance results, and fact verification.

    Args:
        sentiment (dict): Output from SentimentAnalyzer
        compliance (dict): Output from check_compliance
        fact_check (dict): Output from verify_facts

    Returns:
        dict: {"trust_score": int, "breakdown": dict}
    """
    score = 100
    breakdown = {}

    # Sentiment adjustment (too extreme sentiment reduces trust)
    if sentiment["label"] in ["negative", "positive"] and sentiment["score"] > 0.9:
        score -= 10
        breakdown["sentiment_penalty"] = -10

    # Compliance issues
    if not compliance["compliant"]:
        penalty = len(compliance["issues"]) * 10
        score -= penalty
        breakdown["compliance_penalty"] = -penalty

    # Fact verification
    if not fact_check["verified"]:
        score -= 20
        breakdown["fact_check_penalty"] = -20
    else:
        breakdown["fact_verified_bonus"] = +5
        score += 5

    # Clamp score
    score = max(0, min(100, score))
    return {"trust_score": score, "breakdown": breakdown}
