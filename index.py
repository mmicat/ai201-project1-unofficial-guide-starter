"""
Milestone 4 — Embedding + vector store + retrieval.

Embeds every chunk from pipeline.build_chunks() with all-MiniLM-L6-v2 and stores
them in a local persistent ChromaDB collection (cosine similarity). Provides a
retrieve(query, k) helper used by the generation layer (rag.py).

Build / rebuild the index, then run a quick retrieval test:
    python index.py
"""

import os

import chromadb
from sentence_transformers import SentenceTransformer

from pipeline import build_chunks

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "unofficial_guide"
EMBED_MODEL = "all-MiniLM-L6-v2"

_model = None
_client = None


def get_model():
    """Load the embedding model once (downloads on first use, then cached)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
    return _client


def build_index():
    """(Re)build the ChromaDB collection from all document chunks."""
    chunks = build_chunks()
    client = get_client()

    # Start fresh so re-running doesn't duplicate or stale-out chunks.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    model = get_model()
    texts = [c["text"] for c in chunks]
    print(f"Embedding {len(texts)} chunks with {EMBED_MODEL} ...")
    embeddings = model.encode(
        texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True
    ).tolist()

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[c["metadata"] for c in chunks],
    )
    print(f"Indexed {collection.count()} chunks into '{COLLECTION_NAME}' at {CHROMA_DIR}")
    return collection


def get_collection():
    """Return the existing collection, building it first if missing/empty."""
    client = get_client()
    try:
        col = client.get_collection(COLLECTION_NAME)
        if col.count() > 0:
            return col
    except Exception:
        pass
    return build_index()


def retrieve(query, k=5):
    """Return the top-k chunks for a query as a list of dicts."""
    model = get_model()
    col = get_collection()
    q_emb = model.encode(query, convert_to_numpy=True).tolist()
    res = col.query(
        query_embeddings=[q_emb],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for doc, md, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append({"text": doc, "metadata": md, "distance": dist})
    return hits


# Three of the five planning.md eval questions — used to sanity-check retrieval.
_TEST_QUERIES = [
    "How do I stop the Choo-Choo Train?",
    "How does pity work on a 5-star limited resonance banner?",
    "What is the diamond cost to buy Vital Energy?",
]


def _test():
    for q in _TEST_QUERIES:
        print("\n" + "=" * 70)
        print(f"QUERY: {q}")
        print("=" * 70)
        for i, hit in enumerate(retrieve(q, k=3), 1):
            md = hit["metadata"]
            preview = hit["text"].replace("\n", " ")
            preview = preview[:160] + (" …" if len(preview) > 160 else "")
            print(f"  {i}. dist={hit['distance']:.3f}  source={md['source']}  "
                  f"section={md.get('section', '')!r}")
            print(f"     {preview}")


if __name__ == "__main__":
    build_index()
    _test()
