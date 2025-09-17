from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Wrapper class around Hugging Face's sentiment-analysis pipeline.
    """

    def __init__(self, model_name="cardiffnlp/twitter-roberta-base-sentiment"):
        try:
            logger.info(f"Loading sentiment analysis model: {model_name}")
            self.analyzer = pipeline("sentiment-analysis", model=model_name)
        except Exception as e:
            logger.error(f"Failed to load sentiment analysis model: {e}")
            raise

    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of given text.

        Returns:
            dict: {label, score}
        """
        if not text or len(text.strip()) == 0:
            return {"label": "neutral", "score": 0.0}

        try:
            result = self.analyzer(text[:512])[0]  # limit input
            return {
                "label": result.get("label", "unknown"),
                "score": round(float(result.get("score", 0.0)), 4)
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"label": "error", "score": 0.0}


# Singleton analyzer instance
analyzer = SentimentAnalyzer()


def get_sentiment(text: str) -> dict:
    """
    Safe wrapper around analyzer.analyze()
    Always returns {label, score}, never None
    """
    try:
        result = analyzer.analyze(text)
        if not isinstance(result, dict) or "label" not in result:
            return {"label": "neutral", "score": 0.0}
        return result
    except Exception as e:
        logger.error(f"Sentiment wrapper failed: {e}")
        return {"label": "error", "score": 0.0}
