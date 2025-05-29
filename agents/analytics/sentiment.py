import os
import requests

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
FINBERT_MODEL = "ProsusAI/finbert"

def analyze_sentiment_finbert(text: str) -> str:
    url = f"https://api-inference.huggingface.co/models/{FINBERT_MODEL}"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
    }
    payload = {
        "inputs": text,
        "options": {"wait_for_model": True}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        predictions = response.json()
        if isinstance(predictions, list) and predictions:
            top = max(predictions[0], key=lambda x: x['score'])
            return top['label']
        return "NEUTRAL"
    except Exception as e:
        print(f"Sentiment analysis failed: {e}")
        return "UNKNOWN"