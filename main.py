import sys
from ingestion.news_fetcher import fetch_live_news
from processing.text_cleaner import clean_text
from processing.nlp_segmentation import categorize_news
from processing.sentiment_analysis import get_sentiment
from compliance.fact_checker import verify_facts
from compliance.compliance_rules import check_compliance
from compliance.trust_score import calculate_trust_score
from analysis.trend_analysis import detect_trends
from dashboard.cli_dashboard import show_results
from utils.logger import get_logger
from processing.topic_modeling import TopicModeler

logger = get_logger(__name__)


def run_pipeline():
    logger.info("🚀 Starting News Trust Platform pipeline...")

    # 1. Fetch latest news
    try:
        news_data = fetch_live_news()
        logger.info(f"✅ Fetched {len(news_data)} news articles")
    except Exception as e:
        logger.error(f"❌ Error fetching news: {e}")
        sys.exit(1)

    results = []

    for idx, article in enumerate(news_data):
        try:
            if not isinstance(article, dict):  # ✅ safeguard
                logger.error(f"❌ Skipping article at index {idx}, not a dict: {article}")
                continue

            # ✅ Safe dictionary access
            title = article.get("title", "Untitled")
            trust_score = article.get("trust_score", None)
            label = article.get("label", None)

            logger.info(f"Processing article: {title} | Trust Score: {trust_score} | Label: {label}")

            # ---- Clean text ----
            content = article.get("content", "")
            text = clean_text(content)
            logger.debug(f"Successfully cleaned text for article: {title}")

            # ---- Categorization & sentiment ----
            categories = categorize_news(text) or ["uncategorized"]
            sentiment = get_sentiment(text)  # dict {label, score}

            # ---- Compliance & Fact Checking ----
            facts_ok = verify_facts(text)
            compliance_ok = check_compliance(text)  # ✅ only 1 arg

            trust_score = calculate_trust_score(sentiment, compliance_ok, facts_ok)

            # ---- Trend Analysis ----
            trend_tags = detect_trends(text) or []

            # ---- Gemini Topic Modeling ----
            topics_raw = TopicModeler.gemini_topic_model(text) or []
            topics = [t.get("label", "unknown") for t in topics_raw if isinstance(t, dict)]

            # ---- Collect Results ----
            results.append({
                "title": title,
                "categories": categories,
                "sentiment": sentiment,
                "facts_verified": facts_ok,
                "compliance_passed": compliance_ok,
                "trust_score": trust_score,
                "trends": trend_tags,
                "topics": topics
            })

        except Exception as e:
            # ✅ Don’t assume dict here → safe logging
            safe_title = article["title"] if isinstance(article, dict) and "title" in article else str(article)
            logger.error(f"❌ Error processing article {safe_title}: {e}", exc_info=True)
            continue

    # ---- Show Results ----
    if results:
        show_results(results)
    else:
        logger.warning("⚠️ No results to display.")



if __name__ == "__main__":
    run_pipeline()
