import sys
from ingestion.news_fetcher import fetch_live_news
from processing.text_cleaner import clean_text
from processing.sentiment_analysis import SentimentAnalyzer
from processing.topic_modeling import TopicModeler
from processing.summarizer import Summarizer
from compliance.fact_checker import verify_facts
from compliance.compliance_rules import check_compliance
from compliance.trust_score import calculate_trust_score
from analysis.trend_analysis import detect_trends
from dashboard.cli_dashboard import show_results
from utils.logger import get_logger

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

    # Initialize processors once
    sentiment_analyzer = SentimentAnalyzer()
    topic_modeler = TopicModeler()
    summarizer = Summarizer()

    processed_articles = []

    for article in news_data:
        try:
            title = article.get("title", "Untitled")
            content = article.get("content", "") or article.get("description", "")

            if not content:
                logger.warning(f"⚠️ Skipping article with no content: {title}")
                continue

            # 2. Clean text
            text = clean_text(content)

            # 3. Sentiment & Topic
            sentiment = sentiment_analyzer.analyze(text)
            topics = topic_modeler.fit_transform([text])
            topic_label = list(topics.values())[0]["topic_label"]

            # 4. Summarization
            summary = summarizer.summarize(text)

            # 5. Compliance & Fact Checking
            fact_result = verify_facts(text)
            compliance_result = check_compliance(text)
            trust_score = calculate_trust_score(sentiment, compliance_result, fact_result)

            processed_articles.append({
                "title": title,
                "summary": summary,
                "sentiment": sentiment,
                "topic": topic_label,
                "facts_verified": fact_result,
                "compliance": compliance_result,
                "trust_score": trust_score,
                "text": text
            })

        except Exception as e:
            logger.error(f"❌ Error processing article {article.get('title', 'N/A')}: {e}")
            continue

    # 6. Trend Analysis
    if processed_articles:
        trends = detect_trends(processed_articles)
        show_results(processed_articles, trends)
    else:
        logger.warning("⚠️ No results to display.")

if __name__ == "__main__":
    run_pipeline()
