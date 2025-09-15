# dashboard/cli_dashboard.py

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

def show_results(article_results: list, trends: dict):
    """
    Render results in a CLI dashboard format.

    Args:
        article_results (list): List of dicts containing analysis per article
        trends (dict): Output from trend_analysis
    """
    console.rule("[bold blue]📢 News Analysis Dashboard[/bold blue]")

    # Section 1: Per-Article Results
    table = Table(title="📰 Article Analysis", expand=True)
    table.add_column("ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Summary", style="green")
    table.add_column("Sentiment", justify="center", style="magenta")
    table.add_column("Topic", justify="center", style="yellow")
    table.add_column("Trust Score", justify="center", style="bold red")

    for idx, article in enumerate(article_results, 1):
        summary = article.get("summary", "")[:80] + "..."
        sentiment = f"{article['sentiment']['label']} ({article['sentiment']['score']:.2f})"
        topic = str(article.get("topic", "N/A"))
        trust = str(article.get("trust_score", {}).get("trust_score", "N/A"))
        table.add_row(str(idx), summary, sentiment, topic, trust)

    console.print(table)

    # Section 2: Trends
    console.rule("[bold yellow]📊 Trend Analysis[/bold yellow]")

    # Top Topics
    topics_table = Table(title="Top Topics")
    topics_table.add_column("Topic", style="cyan")
    topics_table.add_column("Count", style="green")
    for topic, count in trends.get("top_topics", []):
        topics_table.add_row(str(topic), str(count))
    console.print(topics_table)

    # Sentiment Trend
    sentiment_table = Table(title="Sentiment Distribution")
    sentiment_table.add_column("Sentiment", style="magenta")
    sentiment_table.add_column("Count", style="green")
    for label, count in trends.get("sentiment_trend", {}).items():
        sentiment_table.add_row(label, str(count))
    console.print(sentiment_table)

    # Emerging Keywords
    keywords_text = ", ".join(trends.get("emerging_keywords", []))
    console.print(Panel(Text(keywords_text, justify="center"), title="Emerging Keywords", subtitle="Top 10"))
