from google import genai
from sklearn.cluster import KMeans
import logging

logger = logging.getLogger(__name__)


class TopicModeler:
    @staticmethod
    def gemini_topic_model(text: str) -> list:
            """
            Uses Gemini Pro to extract topics from a news article.
            Always returns a list of dicts: [{"label": "topic"}]
            """
            try:
                client = genai.Client(api_key="YOUR_API_KEY")
                response = client.models.generate_content(
                    model="gemini-pro",
                    contents=f"Extract 3-5 main topics or themes from the following article:\n\n{text}"
                )
                # Gemini often returns a string → split into topics
                topics = response.text.split("\n")
                cleaned = [t.strip("-• ") for t in topics if t.strip()]
                return [{"label": t} for t in cleaned]
            except Exception as e:
                print(f"Gemini topic modeling failed: {e}")
                return [{"label": "general"}]


    @staticmethod
    def gemini_embedding_topic_model(docs, n_clusters=5):
        """
        Generate topics by embedding articles and clustering.
        Returns a dict with cluster IDs as keys and a list of labeled topics as values.
        """
        try:
            client = genai.Client(api_key="YOUR_API_KEY")

            embeddings = []
            for doc in docs:
                resp = client.models.embed_content(
                    model="models/embedding-001",
                    content=doc
                )
                embeddings.append(resp.embedding.values)

            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(embeddings)

            clustered = {i: [] for i in range(n_clusters)}
            for idx, label in enumerate(labels):
                clustered[label].append({"label": docs[idx][:50], "score": 1.0})

            return clustered

        except Exception as e:
            logger.error(f"Gemini embedding topic modeling failed: {e}")
            return {0: [{"label": "error", "score": 0.0}]}
