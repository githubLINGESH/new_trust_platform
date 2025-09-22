import os
import requests
import yaml
import logging

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        logger.warning("⚠️ Config file not found, falling back to environment or hardcoded key.")
        return {}
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def fetch_live_news(query="technology", language="en", page_size=2):
    """
    Fetch live news articles from NewsAPI and normalize them into dicts.
    Docs: https://newsapi.org/docs/endpoints/everything
    """
    # config = load_config()
    # api_key = config.get("newsapi_key")
    api_key = os.getenv("NEWSAPI_KEY", "5cd910f0fead41fdbcb8955a79210d43")

    if not api_key:
        raise ValueError("❌ Missing NewsAPI key (set in config/config.yaml or env NEWSAPI_KEY)")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": language,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    articles = data.get("articles", [])
    results = []

    for art in articles:
        if not isinstance(art, dict):
            logger.warning(f"⚠️ Skipping non-dict article: {art}")
            continue

        results.append({
            "title": art.get("title") or "",
            "description": art.get("description") or "",
            "content": art.get("content") or "",
            "source": art.get("source", {}).get("name", ""),
            "publishedAt": art.get("publishedAt") or "",
            "url": art.get("url") or ""
        })

    logger.info(f"✅ Normalized {len(results)} articles")
    print(type(results))
    return results


if __name__ == "__main__":
    # Quick test run
    news = fetch_live_news("AI", page_size=5)
    for n in news:
        print(f"{n['title']} ({n['source']}) -> {n['url']}")
