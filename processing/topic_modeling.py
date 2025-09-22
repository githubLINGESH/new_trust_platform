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
                client = genai.Client(api_key="AIzaSyCeMMLTLhR9cLKA-M85LWJ65KInVUPPhQc")
                response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=f"Extract 3-5 main topics or themes from the following article. Return them as a simple list:\n\n{text}"
                )

                raw_output = response.candidates[0].content.parts[0].text.strip()
                topics = [t.strip("-• ") for t in raw_output.split("\n") if t.strip()]

                if len(topics) == 0:
                    print(" 😑 No topics found, defaulting to 'general'")
                else:
                    print(f"👍Extracted topics: {topics}")

                return [{"label": t} for t in topics]

            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}")
                return [{"label": "general"}]


    @staticmethod
    def gemini_embedding_topic_model(docs, n_clusters=5):
        """
        Generate topics by embedding articles and clustering.
        Returns a dict with cluster IDs as keys and a list of labeled topics as values.
        """
        print("Executing embedidng model")
        try:
            client = genai.Client(api_key="AIzaSyCeMMLTLhR9cLKA-M85LWJ65KInVUPPhQc")

            embeddings = []
            for doc in docs:
                resp = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=doc
                )
                embeddings.append(resp.embedding.values)

            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(embeddings)

            clustered = {i: [] for i in range(n_clusters)}
            for idx, label in enumerate(labels):
                clustered[label].append({
                    "label": docs[idx][:50],  # short preview of doc
                    "score": 1.0
                })

            return clustered

        except Exception as e:
            logger.error(f"Gemini embedding topic modeling failed: {e}")
            return {0: [{"label": "error", "score": 0.0}]}
