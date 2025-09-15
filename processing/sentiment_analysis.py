# processing/sentiment_analysis.py

from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Wrapper class around Hugging Face's sentiment-analysis pipeline.
    This will classify each news article as positive, negative, or neutral
    with confidence scores.
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

        Args:
            text (str): Cleaned text to analyze

        Returns:
            dict: Sentiment result {label, score}
        """
        if not text or len(text.strip()) == 0:
            return {"label": "neutral", "score": 0.0}

        try:
            result = self.analyzer(text[:512])[0]  # limit input to 512 tokens
            return {
                "label": result["label"],
                "score": round(float(result["score"]), 4)
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"label": "error", "score": 0.0}
