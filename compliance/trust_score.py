# compliance/trust_score.py

import logging

logger = logging.getLogger(__name__)

def calculate_trust_score(sentiment, compliance, fact_check) -> dict:
    """
    Calculate a trust score (0-100) based on sentiment neutrality,
    compliance results, and fact verification.
    """
    logger.debug("📥 sentiment=%s (type=%s)", sentiment, type(sentiment))
    logger.debug("📥 compliance=%s (type=%s)", compliance, type(compliance))
    logger.debug("📥 fact_check=%s (type=%s)", fact_check, type(fact_check))


    score = 100
    breakdown = {}

    # --- Normalize inputs ---
    # Sentiment: ensure dict format
    if isinstance(sentiment, str):
        sentiment = {"label": sentiment, "score": 1.0}
    elif not isinstance(sentiment, dict):
        sentiment = {"label": "neutral", "score": 0.0}

    # Compliance: ensure dict format
    if not isinstance(compliance, dict):
        compliance = {"compliant": True, "issues": []}

    # Fact check: ensure dict format
    if not isinstance(fact_check, dict):
        fact_check = {"verified": True}

    # --- Sentiment adjustment ---
    if sentiment.get("label") in ["negative", "positive"] and sentiment.get("score", 0) > 0.9:
        score -= 10
        breakdown["sentiment_penalty"] = -10

    # --- Compliance issues ---
    if not compliance.get("compliant", True):
        penalty = len(compliance.get("issues", [])) * 10
        score -= penalty
        breakdown["compliance_penalty"] = -penalty

    # --- Fact verification ---
    if not fact_check.get("verified", True):
        score -= 20
        breakdown["fact_check_penalty"] = -20
    else:
        breakdown["fact_verified_bonus"] = +5
        score += 5

    # Clamp score
    score = max(0, min(100, score))
    return {"trust_score": score, "breakdown": breakdown}
