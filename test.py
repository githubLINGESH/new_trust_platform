from google import genai

client = genai.Client(api_key="AIzaSyCeMMLTLhR9cLKA-M85LWJ65KInVUPPhQc")
text = """The global economy is facing unprecedented challenges in 2024, with inflation rates soaring and supply chain disruptions
continuing to impact markets worldwide. Central banks are under pressure to balance interest rate hikes with the    need to support economic growth. Meanwhile, geopolitical tensions are adding further uncertainty to an already volatile landscape."""
response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="Extract 3-5 main topics or themes from the following article:\n\n{text}"
)

print(response.text)