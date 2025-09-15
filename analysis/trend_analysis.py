# analysis/trend_analysis.py

import collections
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

def detect_trends(articles: List[Dict]) -> dict:
    """
    Detect trends across a batch of processed articles.
    
    Args:
        articles (list): List of dicts containing fields like:
                         {"text": str, "sentiment": dict, "topic": str, "date": datetime}

    Returns:
        dict: {
            "top_topics": list,
            "sentiment_trend": dict,
            "emerging_keywords": list
        }
    """
    if not articles:
        logger.warning("No articles provided for trend analysis.")
        return {
            "top_topics": [],
            "sentiment_trend": {},
            "emerging_keywords": []
        }

    # Track topics
    topic_counter = collections.Counter([a.get("topic", "Unknown") for a in articles])

    # Sentiment trend (positive vs negative vs neutral counts)
    sentiment_counter = collections.Counter([a.get("sentiment", {}).get("label", "neutral") for a in articles])

    # Keyword frequency (naive approach: count capitalized words or >5 chars)
    keyword_counter = collections.Counter()
    for a in articles:
        words = a.get("text", "").split()
        for w in words:
            if len(w) > 5 and w[0].isalpha():
                keyword_counter[w.lower()] += 1

    # Top results
    top_topics = topic_counter.most_common(5)
    sentiment_trend = dict(sentiment_counter)
    emerging_keywords = [kw for kw, _ in keyword_counter.most_common(10)]

    return {
        "top_topics": top_topics,
        "sentiment_trend": sentiment_trend,
        "emerging_keywords": emerging_keywords
    }
