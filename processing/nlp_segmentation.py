import spacy
from typing import Dict, List

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("SpaCy model not found. Run: python -m spacy download en_core_web_sm")

# Simple industry keyword mapping
INDUSTRY_KEYWORDS = {
    "technology": ["ai", "artificial intelligence", "software", "hardware", "cloud", "robotics", "quantum"],
    "finance": ["bank", "stocks", "investment", "ipo", "crypto", "bitcoin", "trading", "fintech"],
    "healthcare": ["hospital", "vaccine", "covid", "drug", "treatment", "biotech", "medical"],
    "energy": ["oil", "gas", "solar", "renewable", "nuclear", "power"],
    "retail": ["ecommerce", "amazon", "shopping", "retail", "consumer"],
    "automotive": ["car", "tesla", "ev", "battery", "automobile", "mobility"],
}

def categorize_news(text: str) -> Dict[str, List[str]]:
    """
    Categorize news into industries and extract named entities.
    Returns dict with {industries, entities}
    """
    if not text:
        return {"industries": [], "entities": []}

    doc = nlp(text)

    # Extract named entities
    entities = list(set([ent.text for ent in doc.ents if ent.label_ in ["ORG", "GPE", "PERSON"]]))

    # Industry detection (keyword-based)
    industries = []
    lowered = text.lower()
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        if any(word in lowered for word in keywords):
            industries.append(industry)

    return {"industries": industries, "entities": entities}

if __name__ == "__main__":
    sample_text = """
    Tesla announced a new AI-powered self-driving feature in its electric vehicles. 
    The company also partnered with Amazon Cloud for scalable infrastructure.
    """
    result = categorize_news(sample_text)
    print("Industries:", result["industries"])
    print("Entities:", result["entities"])
