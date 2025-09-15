# processing/text_cleaner.py
import re
import string

def clean_text(text: str) -> str:
    """
    Cleans raw text by:
    - Removing URLs, special characters
    - Lowercasing
    - Removing extra spaces
    - Keeping meaningful content
    """
    if not text:
        return ""

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

    # Remove HTML tags
    text = re.sub(r"<.*?>", "", text)

    # Remove numbers
    text = re.sub(r"\d+", "", text)

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Convert to lowercase
    text = text.lower()

    # Remove extra whitespace
    text = " ".join(text.split())

    return text
