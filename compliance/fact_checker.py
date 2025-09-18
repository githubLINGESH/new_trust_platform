# compliance/fact_checker.py

import wikipedia
import logging

logger = logging.getLogger(__name__)

def verify_facts(text: str) -> dict:
    """
    Perform a lightweight fact verification by cross-referencing keywords with Wikipedia.
    (Prototype-level implementation)

    Args:
        text (str): News article content

    Returns:
        dict: {"verified": bool, "matched_sources": list}
    """
    if not text or len(text.strip()) == 0:
        return {"verified": False, "matched_sources": []}

    try:
        # Extract simple keywords (naive approach for prototype)
        keywords = [word for word in text.split() if word.istitle() and len(word) > 3]
        matched_sources = []

        for kw in keywords[:3]:  # check top 3 keywords
            try:
                summary = wikipedia.summary(kw, sentences=1)
                if kw.lower() in summary.lower():
                    matched_sources.append({"keyword": kw, "source": "Wikipedia"})
            except Exception:
                continue

        verified = len(matched_sources) > 0
        return {"verified": verified, "matched_sources": matched_sources}

    except Exception as e:
        logger.error(f"Fact-checking failed: {e}")
        return {"verified": False, "matched_sources": []}

if __name__ == "__main__":
    # Simple test
    import sys
    result = verify_facts(sys.argv[0])
    print(result)