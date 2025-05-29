import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer

INDEX_PATH = Path("data/vector_index/faiss.index")
META_PATH = Path("data/vector_index/meta.pkl")
INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_faiss_index(embedded_chunks: List[Dict], dim: int = 384):
    """
    Builds a FAISS index from embedded MCP chunks and saves both vectors and metadata
    """
    if not embedded_chunks:
        print("No embedded chunks available — skipping FAISS index build.")
        return

    index = faiss.IndexFlatL2(dim)
    vectors = np.array([chunk["embedding"] for chunk in embedded_chunks])
    index.add(vectors)

    faiss.write_index(index, str(INDEX_PATH))
    print(f"FAISS index saved to {INDEX_PATH}")

    meta = [{
        "chunk_id": c["chunk_id"],
        "text": c["text"],
        "source": c.get("source", ""),
        "ticker": c.get("ticker", ""),
        "intent_tags": c.get("intent_tags", [])
    } for c in embedded_chunks]

    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)
    print(f"Metadata saved to {META_PATH}")

def load_faiss_index():
    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, "rb") as f:
        meta = pickle.load(f)
    return index, meta

def query_faiss_index(query: str, top_k: int = 5) -> List[Dict]:
    """
    Embeds the query, retrieves top-k relevant chunks from the FAISS index
    """
    index, meta = load_faiss_index()
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), top_k)

    results = []
    for idx in I[0]:
        if idx < len(meta):
            results.append(meta[idx])
    return results