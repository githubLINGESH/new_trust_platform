# processing/summarizer.py

from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Summarizer:
    """
    Summarizes news articles using a Transformer-based summarization pipeline.
    """

    def __init__(self, model_name="facebook/bart-large-cnn"):
        try:
            logger.info(f"Loading summarization model: {model_name}")
            self.summarizer = pipeline("summarization", model=model_name)
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
            raise

    def summarize(self, text: str, max_length: int = 130, min_length: int = 30) -> str:
        """
        Summarize a given text into a shorter form.

        Args:
            text (str): Input text/article
            max_length (int): Maximum length of summary
            min_length (int): Minimum length of summary

        Returns:
            str: Generated summary
        """
        if not text or len(text.strip()) == 0:
            return ""

        try:
            result = self.summarizer(
                text[:1024],  # truncate overly long text
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            return result[0]["summary_text"]
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return ""
