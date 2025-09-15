# processing/topic_modeling.py

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TopicModeler:
    """
    Performs topic modeling on news articles using BERTopic with Sentence-BERT embeddings.
    """

    def __init__(self, embedding_model="all-MiniLM-L6-v2"):
        try:
            logger.info(f"Loading SentenceTransformer model: {embedding_model}")
            self.embedding_model = SentenceTransformer(embedding_model)
            self.model = BERTopic(embedding_model=self.embedding_model)
        except Exception as e:
            logger.error(f"Failed to initialize TopicModeler: {e}")
            raise

    def fit_transform(self, documents: list) -> dict:
        """
        Fit the topic model on a list of documents.

        Args:
            documents (list): List of news article texts

        Returns:
            dict: Mapping of each doc -> topic
        """
        if not documents:
            logger.warning("Empty document list passed to TopicModeler.")
            return {}

        try:
            topics, _ = self.model.fit_transform(documents)
            result = {
                idx: {
                    "document": documents[idx],
                    "topic": str(topics[idx]),
                    "topic_label": self.model.get_topic(topics[idx])
                }
                for idx in range(len(documents))
            }
            return result
        except Exception as e:
            logger.error(f"Topic modeling failed: {e}")
            return {}
