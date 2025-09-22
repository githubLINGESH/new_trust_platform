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
client = genai.Client(api_key="AIzaSyCeMMLTLhR9cLKA-M85LWJ65KInVUPPhQc")

def analyze_with_gemini(article_text: str) -> dict:
    """
    Use Gemini to summarize, extract entities, and provide context-aware insights.
    """
    prompt = f"""
    Analyze the following news article and return ONLY valid JSON without any additional text, markdown, or formatting.

    ARTICLE:
    {article_text[:4000]}  # Limit text to avoid token limits

    Return valid JSON with exactly these keys:
    - "summary": array of 3-4 bullet point strings
    - "entities": array of company/organization names mentioned
    - "sentiment_narrative": string with 1-2 sentence explanation
    - "category": string with best fitting topic/industry

    Example format:
    {{
        "summary": ["Point 1", "Point 2", "Point 3"],
        "entities": ["Company A", "Organization B"],
        "sentiment_narrative": "The article expresses...",
        "category": "technology"
    }}

    JSON:
    """

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        
        # Clean the response - remove markdown code blocks if present
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        import json
        data = json.loads(response_text)
        
        # Validate required keys
        required_keys = ["summary", "entities", "sentiment_narrative", "category"]
        for key in required_keys:
            if key not in data:
                data[key] = [] if key == "entities" else "N/A"
                
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Gemini returned invalid JSON: {e}")
        logger.debug(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
        # Return structured fallback
        return {
            "summary": ["Analysis unavailable"],
            "entities": [],
            "sentiment_narrative": "Sentiment analysis failed",
            "category": "general"
        }
    except Exception as e:
        logger.error(f"❌ Gemini analysis failed: {e}")
        return {
            "summary": ["Analysis failed"],
            "entities": [],
            "sentiment_narrative": "Analysis error",
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
            if llm_analysis:
                try:
                    topics_raw = TopicModeler.gemini_topic_model(text) or []
                    #topics_raw = []
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
