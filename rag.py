"""
Milestone 5 — Grounded generation.

Ties retrieval (index.retrieve) to a Groq LLM with a grounding prompt that forces
the model to answer ONLY from the retrieved chunks and to refuse when the context
is insufficient. Source attribution is both requested inline and returned
separately for the UI.

Quick CLI test (in-scope + out-of-scope):
    python rag.py
"""

import os

from dotenv import load_dotenv
from groq import Groq

from index import retrieve
from hybrid import hybrid_retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
REFUSAL = "I don't have enough information on that."

SYSTEM_PROMPT = (
    "You are The Unofficial Guide, a helpful assistant for the game Infinity Nikki. "
    "Answer the user's question using ONLY the information in the provided sources. "
    "Do not use outside or prior knowledge. "
    f'If the sources do not contain enough information to answer, reply exactly: "{REFUSAL}" '
    "When you do answer, cite the source file(s) you used in square brackets, "
    "e.g. [FAQs-general-gameplay.txt]. Keep answers concise and practical."
)

_client = None


def get_client():
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key or key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and paste your "
                "Groq API key (get one free at https://console.groq.com)."
            )
        _client = Groq(api_key=key)
    return _client


def _format_context(hits):
    """Render retrieved chunks as a numbered, source-labeled context block."""
    blocks = []
    for i, h in enumerate(hits, 1):
        md = h["metadata"]
        label = md["source"]
        section = md.get("section")
        if section:
            label += f" — {section}"
        blocks.append(f"[{i}] (source: {label})\n{h['text']}")
    return "\n\n".join(blocks)


def _unique_sources(hits):
    seen, out = set(), []
    for h in hits:
        md = h["metadata"]
        key = md["source"]
        label = key + (f" — {md['section']}" if md.get("section") else "")
        if key not in seen:
            seen.add(key)
            out.append(label)
    return out


def ask(question, k=5, mode="semantic", category=None):
    """Retrieve, ground, and generate. Returns {answer, sources, hits}.

    mode:     "semantic" (default) or "hybrid" (BM25 + semantic via RRF).
    category: optional metadata filter, e.g. "Quests and Challenges"; None = all.
    """
    where = {"category": category} if category and category != "All" else None
    if mode == "hybrid":
        hits = hybrid_retrieve(question, k=k, where=where)
    else:
        hits = retrieve(question, k=k, where=where)
    context = _format_context(hits)
    user_prompt = (
        f"Sources:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the sources above, and cite the source file(s) you used."
    )
    client = get_client()
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    answer = resp.choices[0].message.content.strip()
    return {"answer": answer, "sources": _unique_sources(hits), "hits": hits}


if __name__ == "__main__":
    for q in [
        "How do I stop the Choo-Choo Train?",                  # in-scope
        "What is the best pizza topping in New York City?",    # out-of-scope
    ]:
        print("\n" + "=" * 70)
        print("Q:", q)
        print("=" * 70)
        result = ask(q)
        print(result["answer"])
        print("\nRetrieved from:")
        for s in result["sources"]:
            print("  •", s)
