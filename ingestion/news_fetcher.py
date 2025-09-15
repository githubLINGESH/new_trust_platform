import os
import requests
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def fetch_live_news(query="technology", language="en", page_size=10):
    """
    Fetch live news articles from NewsAPI.
    Docs: https://newsapi.org/docs/endpoints/everything
    """
    # config = load_config()
    # api_key = config.get("newsapi_key")
    api_key = "5cd910f0fead41fdbcb8955a79210d43"

    if not api_key:
        raise ValueError("Missing NewsAPI key in config/config.yaml")

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
        results.append({
            "title": art.get("title"),
            "description": art.get("description"),
            "content": art.get("content"),
            "source": art.get("source", {}).get("name"),
            "publishedAt": art.get("publishedAt"),
            "url": art.get("url")
        })
    return results

if __name__ == "__main__":
    # Quick test run
    news = fetch_live_news("AI", page_size=5)
    for n in news:
        print(f"{n['title']} ({n['source']}) -> {n['url']}")
