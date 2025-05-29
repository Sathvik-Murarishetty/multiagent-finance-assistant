from typing import List, Dict
import re
import json

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Splits text into chunks of chunk_size characters using regex sentence splitting,
    with specified overlap between chunks.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = " ".join(current_chunk.split()[-overlap:]) + " " + sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def load_and_chunk_mcp_data(mcp_data: Dict) -> List[Dict]:
    """
    Processes MCP JSON response and returns a list of chunked text blocks with metadata,
    to be used directly for RAG embedding and retrieval.
    """
    chunks = []
    ticker = mcp_data.get("ticker", "UNKNOWN")
    intents = mcp_data.get("intents", [])

    for key, value in mcp_data.get("data", {}).items():
        if not value:
            continue

        try:
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, indent=2)
            else:
                value_str = str(value)

            text_chunks = chunk_text(value_str)

            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    "source": key,
                    "ticker": ticker,
                    "intent_tags": intents,
                    "chunk_id": f"{key}_{i}",
                    "text": chunk
                })

        except Exception as e:
            print(f"Failed to process {key}: {e}")

    print(f"Loaded {len(chunks)} chunks from MCP JSON.")
    return chunks