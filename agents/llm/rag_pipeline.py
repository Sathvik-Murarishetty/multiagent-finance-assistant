import os
import requests
from dotenv import load_dotenv
from agents.retriever.faiss_index import query_faiss_index

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def build_rag_prompt(query: str, retrieved_chunks: list, metadata: dict = None) -> str:
    context = "\n---\n".join([chunk["text"] for chunk in retrieved_chunks])

    extra_info = ""

    if metadata:
        if intents := metadata.get("intents"):
            extra_info += f"\nIntent(s): {', '.join(intents)}."
        if ticker := metadata.get("ticker"):
            extra_info += f"\nCompany: {ticker}."
        if region := metadata.get("region"):
            extra_info += f"\nRegion: {region}."
        if time_frame := metadata.get("time_frame"):
            extra_info += f"\nTime Frame: {time_frame}."

        if mcp := metadata.get("mcp_data"):
            sentiment_block = ""
            if "news_sentiment" in mcp:
                sentiment_block += "\nNews Sentiment Tags:\n"
                for i, s in enumerate(mcp["news_sentiment"][:3], 1):
                    sentiment_block += f"{i}. \"{s['text'][:120]}...\" → **{s['sentiment']}**\n"

            other_data = "\n".join(
                f"{k}: {str(v)[:500]}" for k, v in mcp.items()
                if k != "news_sentiment" and v
            )

            extra_info += f"\n\nStructured Market Info:\n{sentiment_block}\n{other_data}"


    prompt = f"""
You are VERONICA, a professional financial assistant.

Using the structured market data and contextual documents provided below, generate a clear, concise financial briefing in paragraph form. Your tone should be analytical yet approachable and do not use the ticker in the response use the company name where it is needed — as if presenting insights to a portfolio manager in a meeting.

If the user query relates to **stock lookup**, **earnings summary**, **option insight**, or **financials**, include relevant numerical figures such as:
- Stock price trends
- Calculate EPS values and surprises
- Option chain volumes or strike prices
- Key financial statement values (e.g., revenue, profit, cashflow, AUM)
- Avoid lists unless comparing multiple metrics.
- If data is missing or unclear, briefly note that.
- Keep the response under 250 words.
- In the end give your one line statement of what you think.

User Query:
"{query}"

Context for Analysis:
{extra_info}

Retrieved Context Chunks:
{context}

Provide a brief but insightful summary of the financial status or key insights relevant to the query.
"""
    return prompt.strip()

def query_llm(prompt: str, model="mistralai/devstral-small:free") -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://veronica.local",
        "X-Title": "veronica-rag-agent"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM Error: {e}"

def run_rag_pipeline(query: str, top_k: int = 5, metadata: dict = None) -> str:
    retrieved = query_faiss_index(query, top_k=top_k)
    if not retrieved:
        return "No relevant information found from MCP data."

    prompt = build_rag_prompt(query, retrieved, metadata=metadata)
    return query_llm(prompt)