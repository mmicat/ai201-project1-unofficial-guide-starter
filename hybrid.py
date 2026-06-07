"""
Stretch feature — Hybrid search (BM25 + semantic) with Reciprocal Rank Fusion.

Semantic retrieval (ChromaDB / all-MiniLM-L6-v2) is great at meaning but can miss
exact keyword matches; BM25 is the opposite. We run both over the same 463 chunks
and combine their *ranks* with Reciprocal Rank Fusion (RRF):

    score(chunk) = sum over each ranker of  1 / (C + rank_in_that_ranker)

RRF needs no score normalization (semantic uses cosine distance, BM25 uses a
different scale), which is why it's a robust way to merge the two. C=60 is the
standard constant. Both rankers honor the same optional metadata `where` filter,
so hybrid search composes with the metadata-filtering feature.
"""

import re

from index import retrieve as semantic_retrieve
from index import get_model, get_collection
from pipeline import build_chunks

RRF_C = 60          # standard RRF constant
CANDIDATES = 30     # how many candidates to pull from each ranker before fusing

_chunks = None
_by_id = None
_ids = None
_bm25 = None


def _tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def _ensure_loaded():
    """Build the BM25 index and id→chunk lookup once."""
    global _chunks, _by_id, _ids, _bm25
    if _bm25 is not None:
        return
    from rank_bm25 import BM25Okapi

    _chunks = build_chunks()
    _by_id = {c["id"]: c for c in _chunks}
    _ids = [c["id"] for c in _chunks]
    _bm25 = BM25Okapi([_tokenize(c["text"]) for c in _chunks])


def _passes(md, where):
    """Simple equality metadata filter, matching the ChromaDB `where` we use."""
    if not where:
        return True
    return all(md.get(k) == v for k, v in where.items())


def semantic_ranked(query, n=CANDIDATES, where=None):
    """Return chunk ids ranked by semantic similarity (best first)."""
    return [h["id"] for h in semantic_retrieve(query, k=n, where=where)]


def bm25_ranked(query, n=CANDIDATES, where=None):
    """Return chunk ids ranked by BM25 score (best first), respecting `where`."""
    _ensure_loaded()
    scores = _bm25.get_scores(_tokenize(query))
    order = sorted(range(len(_ids)), key=lambda i: scores[i], reverse=True)
    out = []
    for i in order:
        cid = _ids[i]
        if scores[i] <= 0:
            break
        if _passes(_by_id[cid]["metadata"], where):
            out.append(cid)
        if len(out) >= n:
            break
    return out


def hybrid_retrieve(query, k=5, where=None, n=CANDIDATES, c=RRF_C):
    """Fuse semantic + BM25 rankings via RRF; return top-k chunk dicts."""
    _ensure_loaded()
    sem = semantic_ranked(query, n=n, where=where)
    bm = bm25_ranked(query, n=n, where=where)

    fused = {}
    sem_rank = {cid: r for r, cid in enumerate(sem)}
    bm_rank = {cid: r for r, cid in enumerate(bm)}
    for cid in set(sem) | set(bm):
        score = 0.0
        if cid in sem_rank:
            score += 1.0 / (c + sem_rank[cid])
        if cid in bm_rank:
            score += 1.0 / (c + bm_rank[cid])
        fused[cid] = score

    ranked = sorted(fused, key=lambda cid: fused[cid], reverse=True)[:k]
    hits = []
    for cid in ranked:
        chunk = _by_id[cid]
        hits.append({
            "id": cid,
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "rrf_score": round(fused[cid], 5),
            "semantic_rank": sem_rank.get(cid),   # None if BM25-only
            "bm25_rank": bm_rank.get(cid),        # None if semantic-only
        })
    return hits


if __name__ == "__main__":
    # Quick smoke test on the documented Q2 failure query.
    q = "On a 5-star Limited Resonance banner, how many pulls guarantee a 5-star?"
    print(f"HYBRID results for: {q}\n")
    for i, h in enumerate(hybrid_retrieve(q, k=5), 1):
        md = h["metadata"]
        print(f"{i}. rrf={h['rrf_score']}  sem_rank={h['semantic_rank']}  "
              f"bm25_rank={h['bm25_rank']}  {md['source']} :: {md.get('section', '')}")
        print(f"   {h['text'][:120].replace(chr(10), ' ')}")
