import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def classify_intent(transcript: str) -> dict:
    prompt = f"""
You are an intent classification agent for a financial assistant.

Given a user's query, identify **all relevant intents** from this list:
- stock_lookup
- earnings_summary
- sentiment_analysis
- risk_exposure
- holder_analysis
- option_insight
- financials
- news_summary

Also extract:
- Target stock ticker symbol (if any)
- Region: US, Asia, Global (if mentioned)
- Time reference: 'Q1 2024', 'this week', etc.

Respond ONLY with a valid JSON object in the format:

{{
  "intents": ["<intent1>", "<intent2>", ...],
  "tickers": ["<ticker1>", "<ticker2>", ...],
  "region": "<US | Asia | Global | blank>",
  "time_frame": "<e.g., 'Q1 2023', 'last week', 'today', or blank>"
}}
Transcript: "{transcript}"
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://veronica.local",
        "X-Title": "veronica-agent"
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": "mistralai/devstral-small:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            },
            timeout=15
        )

        data = response.json()
        if "choices" not in data or not data["choices"]:
            raise ValueError(f"OpenRouter error: {data}")

        content = data["choices"][0]["message"]["content"].strip()

        parsed = json.loads(content)

        return {
            "intents": parsed.get("intents", []),
            "tickers": parsed.get("tickers", []),
            "region": parsed.get("region", ""),
            "time_frame": parsed.get("time_frame", "")
        }

    except Exception as e:
        return {
            "intents": [],
            "ticker": "",
            "region": "",
            "time_frame": "",
            "error": str(e)
        }