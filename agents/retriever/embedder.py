from sentence_transformers import SentenceTransformer
from typing import List, Dict

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks: List[Dict]) -> List[Dict]:
    """
    Adds vector embeddings to each chunk using MiniLM and preserves metadata
    """
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    embedded_chunks = []
    for chunk, embedding in zip(chunks, embeddings):
        embedded_chunks.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "embedding": embedding,
            "source": chunk.get("source", ""),
            "ticker": chunk.get("ticker", ""),
            "intent_tags": chunk.get("intent_tags", [])
        })

    print(f"Embedded {len(embedded_chunks)} chunks from MCP data.")
    return embedded_chunks