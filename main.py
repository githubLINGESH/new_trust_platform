import sys
import logging
from google import genai
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

# 🔑 Configure Gemini
client = genai.Client(api_key="AIzaSyDZD8N2-YX9pQcC_29IKkXohgbpR55lm78")

def analyze_with_gemini(article_text: str) -> dict:
    """
    Use Gemini to summarize, extract entities, and provide context-aware insights.
    """
    prompt = f"""
    You are an AI analyst. Analyze the following article:

    ARTICLE:
    {article_text}

    Return valid JSON with keys:
    - summary: 3-4 bullet points
    - entities: list of companies/organizations mentioned
    - sentiment_narrative: 1-2 sentence explanation of sentiment
    - category: best fitting topic/industry
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )
        
        # Ensure clean JSON parsing
        import json
        data = json.loads(response.text)
        return data
    except Exception as e:
        logger.error(f"❌ Gemini analysis failed: {e}")
        return {
            "summary": ["N/A"],
            "entities": [],
            "sentiment_narrative": "N/A",
            "category": "general"
        }

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
            compliance_ok = check_compliance(text)
            trust_score = calculate_trust_score(sentiment, compliance_ok, facts_ok)

            # ---- Gemini Context Analysis ----
            llm_analysis = analyze_with_gemini(text)

            # ---- Gemini Topic Modeling ----
            try:
                topics_raw = TopicModeler.gemini_topic_model(text) or []
                topics = [t.get("label", "unknown") for t in topics_raw if isinstance(t, dict)]
            except Exception as e:
                logger.error(f"❌ Topic modeling failed for article '{title}': {e}")
                topics = []

            # ---- Trend Analysis (safe input) ----
            try:
                trend_tags = detect_trends([{
                    "text": text,
                    "sentiment": sentiment,
                    "topic": topics[0] if topics else llm_analysis.get("category", "unknown")
                }]) or {}
            except Exception as e:
                logger.error(f"❌ Trend analysis failed for article '{title}': {e}")
                trend_tags = {}

            # ---- Collect Results ----
            results.append({
                "title": title,
                "summary": llm_analysis.get("summary", []),
                "entities": llm_analysis.get("entities", []),
                "categories": categories,
                "sentiment": sentiment,
                "sentiment_narrative": llm_analysis.get("sentiment_narrative", "N/A"),
                "facts_verified": facts_ok,
                "compliance_passed": compliance_ok,
                "trust_score": trust_score,
                "trends": trend_tags,
                "topics": topics or [llm_analysis.get("category", "general")]
            })

        except Exception as e:
            # ✅ Don’t assume dict here → safe logging
            safe_title = article["title"] if isinstance(article, dict) and "title" in article else str(article)
            logger.error(f"❌ Error processing article {safe_title}: {e}", exc_info=True)
            continue

    # ---- Show Results ----
    if results:
        try:
            global_trends = detect_trends([
                {
                    "text": r["title"] + " " + " ".join(r.get("topics", [])),
                    "sentiment": r["sentiment"],
                    "topic": r["topics"][0] if r["topics"] else "unknown"
                }
                for r in results
            ])
        except Exception as e:
            logger.error(f"❌ Failed to compute global trends: {e}")
            global_trends = {}

        show_results(results, global_trends)
    else:
        logger.warning("⚠️ No results to display.")


if __name__ == "__main__":
    run_pipeline()
