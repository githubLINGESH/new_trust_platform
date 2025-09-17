# compliance/compliance_rules.py

import re
import logging

logger = logging.getLogger(__name__)

BANNED_KEYWORDS = ["fake", "hoax", "rumor", "clickbait"]
SENSITIVE_TOPICS = ["terrorism", "violence", "hate speech"]

def check_compliance(text: str, categories: list = None) -> dict:
    """
    Check text against compliance rules.

    Args:
        text (str): Cleaned news text
        categories (list): Optional list of categories assigned to the text

    Returns:
        dict: {"compliant": bool, "issues": list}
    """
    issues = []

    # Rule 1: banned keywords
    for word in BANNED_KEYWORDS:
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            issues.append(f"Contains banned keyword: {word}")

    # Rule 2: sensitive topics
    for topic in SENSITIVE_TOPICS:
        if re.search(rf"\b{topic}\b", text, re.IGNORECASE):
            issues.append(f"Contains sensitive topic: {topic}")

    # Rule 3: category-specific compliance
    if categories:
        if "finance" in categories and "scam" in text.lower():
            issues.append("Finance article flagged for potential scam content")
        if "health" in categories and "unverified cure" in text.lower():
            issues.append("Health article flagged for unverified medical claim")

    compliant = len(issues) == 0
    return {"compliant": compliant, "issues": issues}
