"""
Stretch-feature evidence harness.

Part A — Hybrid vs Semantic vs BM25 retrieval on several queries (shows what each
         method returns and where hybrid helps).
Part B — Metadata filtering: the same query with and without a category filter,
         showing a visible change in which chunks are returned.

    python compare_stretch.py
"""

import hybrid
from index import retrieve


def _label(cid):
    md = hybrid._by_id[cid]["metadata"]
    return f"{md['source']} :: {md.get('section', '')}"


def _show_ids(ids):
    for r, cid in enumerate(ids, 1):
        print(f"     {r}. {_label(cid)}")


PART_A_QUERIES = [
    # keyword + semantic; the documented Q2 failure (hybrid rescues it)
    "On a 5-star Limited Resonance banner, how many pulls guarantee a 5-star?",
    # rare proper noun — BM25 territory
    "How do I get the Spira Shelldome warp spire?",
    # paraphrase with no shared keywords — semantic territory
    "How do I make my character giant to scare off enemies?",
]


def part_a():
    print("#" * 74)
    print("PART A — HYBRID vs SEMANTIC vs BM25 (top 3 each)")
    print("#" * 74)
    hybrid._ensure_loaded()
    for q in PART_A_QUERIES:
        print(f"\nQUERY: {q}")
        print("  SEMANTIC-only:")
        _show_ids(hybrid.semantic_ranked(q, n=3))
        print("  BM25-only:")
        _show_ids(hybrid.bm25_ranked(q, n=3))
        print("  HYBRID (RRF):")
        _show_ids([h["id"] for h in hybrid.hybrid_retrieve(q, k=3)])


def part_b():
    print("\n" + "#" * 74)
    print("PART B — METADATA FILTERING (visible effect)")
    print("#" * 74)
    q = "How do I get more bling?"
    print(f"\nQUERY: {q}")
    print("  UNFILTERED (top 3):")
    for r, h in enumerate(retrieve(q, k=3), 1):
        print(f"     {r}. {h['metadata']['source']} :: {h['metadata'].get('section', '')}")
    cat = "Misc and Customer Support"
    print(f"  FILTERED to category = '{cat}' (top 3):")
    for r, h in enumerate(retrieve(q, k=3, where={"category": cat}), 1):
        print(f"     {r}. {h['metadata']['source']} :: {h['metadata'].get('section', '')}")
    print("\n  -> The filter restricts retrieval to a single category, so the chunks "
          "returned change visibly (no -blings General chunk survives the filter).")


if __name__ == "__main__":
    part_a()
    part_b()
