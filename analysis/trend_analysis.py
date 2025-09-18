# analysis/trend_analysis.py

import collections
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def detect_trends(articles: List[Dict[str, Any]]) -> dict:
    """
    Detect trends across a batch of processed articles.
    
    Args:
        articles (list): List of dicts containing fields like:
                         {
                             "text": str,
                             "sentiment": {"label": str, "score": float},
                             "topic": str,
                             "date": datetime
                         }

    Returns:
        dict: {
            "top_topics": list of (topic, count),
            "sentiment_trend": dict {label: count},
            "emerging_keywords": list of keywords
        }
    """
    if not articles:
        logger.warning("⚠️ No articles provided for trend analysis.")
        return {
            "top_topics": [],
            "sentiment_trend": {},
            "emerging_keywords": []
        }

    # ✅ Ensure input is a list of dicts
    clean_articles = [a for a in articles if isinstance(a, dict)]
    if not clean_articles:
        logger.error(f"❌ detect_trends received invalid input: {articles}")
        return {
            "top_topics": [],
            "sentiment_trend": {},
            "emerging_keywords": []
        }

    # ---- Track topics ----
    topic_counter = collections.Counter(
        [a.get("topic", "Unknown") for a in clean_articles]
    )

    # ---- Sentiment trend (positive / negative / neutral) ----
    sentiment_counter = collections.Counter(
        [a.get("sentiment", {}).get("label", "neutral") for a in clean_articles]
    )

    # ---- Keyword frequency (naive: words >5 chars, alphabetic) ----
    keyword_counter = collections.Counter()
    for a in clean_articles:
        text = a.get("text", "")
        if not isinstance(text, str):
            continue
        words = text.split()
        for w in words:
            if len(w) > 5 and w[0].isalpha():
                keyword_counter[w.lower()] += 1

    # ---- Build results ----
    top_topics = topic_counter.most_common(5)
    sentiment_trend = dict(sentiment_counter)
    emerging_keywords = [kw for kw, _ in keyword_counter.most_common(10)]

    return {
        "top_topics": top_topics,
        "sentiment_trend": sentiment_trend,
        "emerging_keywords": emerging_keywords
    }
