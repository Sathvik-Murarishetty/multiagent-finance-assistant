from agents.retriever.loader import load_and_chunk_documents
from agents.retriever.embedder import embed_chunks
from agents.retriever.faiss_index import build_faiss_index

chunks = load_and_chunk_documents()
embedded = embed_chunks(chunks)
build_faiss_index(embedded)
print("Index built and saved.")
