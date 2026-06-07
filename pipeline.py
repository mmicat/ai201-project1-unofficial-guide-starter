"""
Milestone 3 — Document pipeline: load, clean, and structure-aware chunk.

Chunking strategy (see planning.md):
  * Split on the structural markers built into the cleaned documents:
      - FAQ files:  entries delimited by lines containing only `---`
      - Wiki/guide: sections delimited by `===` banners
      - Markdown guides: `#`/`##` headings
  * Each structural unit becomes one chunk (the retrieval unit = the query unit).
  * Soft cap of MAX_CHARS (~800 chars / ~200 tokens) keeps every chunk under
    all-MiniLM-L6-v2's 256-token truncation limit. Oversized sections are
    sub-split on paragraph boundaries, then hard-split with OVERLAP only where
    continuous prose must be cut.

Run directly to inspect the chunks:
    python pipeline.py
"""

import os
import re
import glob

MAX_CHARS = 800       # soft cap per chunk (~200 tokens for all-MiniLM-L6-v2)
OVERLAP = 120         # overlap chars, applied only to secondary (forced) splits
MIN_CHARS = 20        # drop trivial fragments

DOCUMENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")

# A banner is three lines: ===, a title, ===   (used by wiki/guide/reddit files)
BANNER_RE = re.compile(r"^={3,}[ \t]*\n(.+?)\n={3,}[ \t]*$", re.MULTILINE)
# A horizontal rule: a line containing only --- (separates FAQ entries)
HR_RE = re.compile(r"(?m)^[ \t]*---[ \t]*$")
# Markdown headings, levels 1-2 only (so ### subsections stay with their parent)
HEADING_RE = re.compile(r"(?m)^#{1,2}[ \t]+(.+?)[ \t]*$")


# --------------------------------------------------------------------------- #
# Loading & cleaning
# --------------------------------------------------------------------------- #
def load_documents(documents_dir=DOCUMENTS_DIR):
    """Return [{'source': filename, 'text': str}] for every non-empty .txt file."""
    docs = []
    for path in sorted(glob.glob(os.path.join(documents_dir, "*.txt"))):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if not text.strip():
            continue  # skip empty files (e.g. guides-quests.txt)
        docs.append({"source": os.path.basename(path), "text": text})
    return docs


def clean_text(text):
    """Light normalization that preserves the structural markers we split on."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse 3+ blank lines
    return text.strip()


def _source_title(text, fallback):
    m = re.search(r"(?m)^Source:\s*(.+)$", text)
    return m.group(1).strip() if m else fallback


# --------------------------------------------------------------------------- #
# Structural sectioning
# --------------------------------------------------------------------------- #
def _split_sections(text, source):
    """Split a document into [(title, body)] using its structural markers."""
    # 1) FAQ files: `---`-delimited entries, each containing COMMAND:
    if HR_RE.search(text) and "COMMAND:" in text:
        sections = []
        for seg in HR_RE.split(text):
            seg = seg.strip()
            if not seg or "COMMAND:" not in seg:
                continue  # skip the FORMAT NOTE / category-banner segment
            cm = re.search(r"(?m)^COMMAND:\s*(.+)$", seg)
            title = cm.group(1).strip() if cm else source
            sections.append((title, seg))
        return sections

    # 2) Banner files: `===` section banners
    if BANNER_RE.search(text):
        parts = BANNER_RE.split(text)  # [pre, title1, body1, title2, body2, ...]
        sections = []
        for i in range(1, len(parts), 2):
            title = parts[i].strip()
            body = parts[i + 1].strip() if i + 1 < len(parts) else ""
            if body:
                sections.append((title, body))
        return sections

    # 3) Markdown-heading files (e.g. pearfect-realms.txt)
    if HEADING_RE.search(text):
        matches = list(HEADING_RE.finditer(text))
        sections = []
        for idx, m in enumerate(matches):
            title = m.group(1).strip()
            start = m.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                sections.append((title, body))
        if sections:
            return sections

    # 4) Fallback: whole document as one section
    return [(source, text)]


# --------------------------------------------------------------------------- #
# Secondary (size) splitting
# --------------------------------------------------------------------------- #
def _hard_split(s, max_chars=MAX_CHARS, overlap=OVERLAP):
    """Sliding-window split with overlap, for a single oversized paragraph."""
    step = max(1, max_chars - overlap)
    return [s[i:i + max_chars] for i in range(0, len(s), step)]


def _split_oversized(body, max_chars=MAX_CHARS, overlap=OVERLAP):
    """Keep a section whole if it fits; else pack paragraphs up to the cap."""
    if len(body) <= max_chars:
        return [body]
    pieces, cur = [], ""
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para:
            continue
        if len(para) > max_chars:               # paragraph itself too big
            if cur:
                pieces.append(cur)
                cur = ""
            pieces.extend(_hard_split(para, max_chars, overlap))
        elif not cur:
            cur = para
        elif len(cur) + 2 + len(para) <= max_chars:
            cur += "\n\n" + para
        else:
            pieces.append(cur)
            cur = para
    if cur:
        pieces.append(cur)
    return pieces


# --------------------------------------------------------------------------- #
# Chunking
# --------------------------------------------------------------------------- #
def chunk_document(text, source, max_chars=MAX_CHARS, overlap=OVERLAP):
    """Return [{'text', 'metadata'}] chunks for one document."""
    text = clean_text(text)
    source_title = _source_title(text, source)
    chunks = []
    for title, body in _split_sections(text, source):
        body = body.strip()
        if not body:
            continue
        is_faq = body.startswith("COMMAND:")
        category = None
        if is_faq:
            cm = re.search(r"(?m)^CATEGORY:\s*(.+)$", body)
            category = cm.group(1).strip() if cm else None

        # Context header prepended to every piece so a split section's
        # continuation chunks aren't orphaned. Budget for it so prepending
        # keeps the final chunk under the cap.
        header = f"COMMAND: {title}" if is_faq else (title or "")
        reserve = len(header) + 2 if header else 0
        budget = max(200, max_chars - reserve)

        for piece in _split_oversized(body, budget, overlap):
            piece = piece.strip()
            if header and not piece.startswith("COMMAND:") and not piece.startswith(header):
                chunk_text = f"{header}\n\n{piece}"
            else:
                chunk_text = piece
            if len(chunk_text) < MIN_CHARS:
                continue
            md = {"source": source, "source_title": source_title, "section": title}
            if category:
                md["category"] = category
            chunks.append({"text": chunk_text, "metadata": md})
    return chunks


def build_chunks(documents_dir=DOCUMENTS_DIR):
    """Load every document and return the full list of chunks with ids."""
    all_chunks = []
    for doc in load_documents(documents_dir):
        for j, c in enumerate(chunk_document(doc["text"], doc["source"])):
            c["metadata"]["chunk_index"] = j
            c["id"] = f"{doc['source']}::{j}"
            all_chunks.append(c)
    return all_chunks


# --------------------------------------------------------------------------- #
# Inspection (Milestone 3, Step 4)
# --------------------------------------------------------------------------- #
def _inspect():
    chunks = build_chunks()
    total = len(chunks)
    sizes = [len(c["text"]) for c in chunks]
    per_source = {}
    for c in chunks:
        per_source[c["metadata"]["source"]] = per_source.get(c["metadata"]["source"], 0) + 1

    print(f"\nTotal chunks: {total}")
    print(f"Chunk size (chars): min={min(sizes)}  max={max(sizes)}  "
          f"avg={sum(sizes)//total}")
    over = sum(1 for s in sizes if s > MAX_CHARS)
    print(f"Chunks over the {MAX_CHARS}-char cap: {over} "
          f"({'within target 50-2000' if 50 <= total <= 2000 else 'OUTSIDE 50-2000 TARGET'})")

    print("\nChunks per source:")
    for src in sorted(per_source):
        print(f"  {per_source[src]:>4}  {src}")

    print("\n" + "=" * 70)
    print("SAMPLE CHUNKS (one from each of 5 different documents)")
    print("=" * 70)
    seen = set()
    shown = 0
    for c in chunks:
        src = c["metadata"]["source"]
        if src in seen:
            continue
        seen.add(src)
        shown += 1
        md = c["metadata"]
        print(f"\n[{shown}] source={md['source']}  section={md['section']!r}  "
              f"chars={len(c['text'])}  id={c['id']}")
        if "category" in md:
            print(f"    category={md['category']!r}")
        print("-" * 70)
        preview = c["text"] if len(c["text"]) <= 600 else c["text"][:600] + " …[truncated]"
        print(preview)
        if shown == 5:
            break


if __name__ == "__main__":
    _inspect()
