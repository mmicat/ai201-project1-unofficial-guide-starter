# The Unofficial Guide — Project 1

A retrieval-augmented (RAG) Q&A system for the game **Infinity Nikki**. Ask a
plain-language question and get an answer grounded in community-sourced
documents, with the source files cited in the response.

**Pipeline:** `documents/*.txt` → clean + structure-aware chunk (`pipeline.py`) →
embed with `all-MiniLM-L6-v2` into ChromaDB (`index.py`) → top-5 retrieval →
grounded generation via Groq `llama-3.3-70b-versatile` (`rag.py`) → Gradio UI (`app.py`).

**Run it:**
```bash
pip install -r requirements.txt          # then add your Groq key to .env
python index.py     # build the vector store (one time)
python app.py       # launch the UI at http://localhost:7860
python evaluate.py  # run the 5 eval questions
```

---

## Domain

This system covers **Infinity Nikki** (© Infold Games), an open-world dress-up
adventure game — specifically the practical, problem-solving knowledge players
need: quests, game systems, currencies, gacha mechanics, outfits/abilities, and
account/technical troubleshooting.

This knowledge is **hard to find through official channels** because Infold's
official outlets (website, in-game notices, patch notes) publish announcements
and store listings, not answers to questions like *"why won't this Forced
Perspective quest register my photo,"* *"how does pity work on a limited
banner,"* or *"is this cutscene bugged."* That knowledge lives in community
spaces — the official Discord (maintained guides and bot-command FAQs), the
Fandom Wiki (lore/quest/item references), and Reddit (new-player advice) — where
it is scattered, inconsistently formatted, and sometimes version-specific. A
single searchable, source-grounded system over that material is genuinely useful.

---

## Document Sources

14 cleaned documents drawn from three origins, covering lore/story, mechanics,
progression, monetization, and troubleshooting. (One starter file,
`documents/guides-quests.txt`, was left empty and is excluded from ingestion.)

| # | Source | Type | URL or file path |
|---|--------|------|------------------|
| 1 | Fandom Wiki — Main Quest | Wiki | `infinity-nikki.fandom.com/wiki/` → `documents/wiki-mainquest.txt` |
| 2 | Fandom Wiki — Itzaland Arc (Prologue–Ch. 5) | Wiki | `documents/wiki-itzalandarc.txt` |
| 3 | Fandom Wiki — Outfits | Wiki | `documents/wiki-outfits.txt` |
| 4 | Fandom Wiki — Ability | Wiki | `documents/wiki-ability.txt` |
| 5 | Fandom Wiki — Mira Level | Wiki | `documents/wiki-miralevel.txt` |
| 6 | Fandom Wiki — Heart of Infinity | Wiki | `documents/wiki-heartofinfinity.txt` |
| 7 | Fandom Wiki — Pear-Pal | Wiki | `documents/wiki-pearpal.txt` |
| 8 | Fandom Wiki — Compendium | Wiki | `documents/wiki-compendium.txt` |
| 9 | Official Discord `bot-playground` FAQ — Quests & Challenges | Discord | `discord.gg/infinitynikki` → `documents/FAQs-quests-and-challenges.txt` |
| 10 | Official Discord `bot-playground` FAQ — General Gameplay | Discord | `documents/FAQs-general-gameplay.txt` |
| 11 | Official Discord `bot-playground` FAQ — Misc & Customer Support | Discord | `documents/FAQs-misc-and-customer-support.txt` |
| 12 | Official Discord — master guide thread | Discord | `documents/guides-masterthread.txt` |
| 13 | "Realm Challenges 101" (Pear-fect Guides) | Discord/community | `documents/pearfect-realms.txt` |
| 14 | r/InfinityNikki — "Just Downloaded!" new-player thread | Reddit | `reddit.com/r/InfinityNikki/` → `documents/reddit-newplayer.txt` |

---

## Chunking Strategy

**Chunk size:** Structure-first, with a soft cap of **~800 characters (≈200 tokens)** per chunk.

**Overlap:** **None** between whole structural units (each is self-contained);
**~120 characters** only when a long section must be force-split.

**Preprocessing:** Each raw source was cleaned (Fandom/Reddit boilerplate, nav
menus, language tables, and footers stripped) and given consistent structural
markers — `---` between FAQ entries, `===` banners around wiki sections. At chunk
time, `pipeline.py` normalizes whitespace and collapses blank lines but
preserves those markers.

**Why these choices fit the documents:** The corpus has three natural
structures, so I split on those boundaries instead of blind fixed-width windows:
- **FAQ files** — `---`-delimited entries, each a complete Q&A (`COMMAND` +
  question + answer). One entry → one chunk, so the retrieval unit matches the
  query unit; a `---` boundary never cuts an answer in half.
- **Wiki/guide files** — `===` section banners → one coherent topic per chunk.
- **Markdown guides** (`pearfect-realms.txt`) — split on `#`/`##` headings.

The ~800-char cap exists because `all-MiniLM-L6-v2` **truncates input at 256
tokens** — anything longer is silently dropped and unretrievable. ~800 chars
(emoji shortcodes and URLs tokenize densely) keeps chunks under that limit with
margin. Oversized sections are sub-split on paragraph boundaries, then hard-split
with overlap; continuation pieces are prepended with their `COMMAND:`/section
title so they aren't orphaned. Overlap is used *only* on forced splits, never
between whole units (where it would just duplicate a complete answer).

**Final chunk count:** **463 chunks** across the 14 documents (`MAX_CHARS=800`,
`OVERLAP=120`); min 40 / max 800 / avg 578 chars.

### Sample chunks (with source)

```
[FAQs-quests-and-challenges.txt :: -aperture/-perspective]
COMMAND: -aperture/-perspective
CATEGORY: Quests and Challenges
DESCRIPTION: Help with Forced Perspective quests not working
CONTENT: Why aren't the Forced Perspective quests working?
You will need to get a gold box surrounding the target. If it's not showing up,
please try resetting your camera to default settings and/or make sure aperture is
set to f/16. ...

[pearfect-realms.txt :: 1. Overview of Realm Challenges]
1. Overview of Realm Challenges
### What are Realm Challenges?
Realm Challenges are special game modes located within the various Warp Spires ...
### Vital Energy System
- Cap: All players have a maximum Vital Energy cap of 350. ...

[wiki-itzalandarc.txt :: ARC OVERVIEW: The Itzaland Arc]
ARC OVERVIEW: The Itzaland Arc
The Itzaland arc is the main questline introduced in Version 2.0. It consists of
a prologue followed by nine chapters. ...

[FAQs-misc-and-customer-support.txt :: -account]
COMMAND: -account
CATEGORY: Misc and Customer Support
DESCRIPTION: How to bind a third party account to Infold
CONTENT: I have a third party account, how do I bind to Infold? ...

[wiki-outfits.txt :: OVERVIEW]
OVERVIEW
Outfits is a clothing category in Infinity Nikki. They are clothing sets
comprised of wardrobe items. Once a suit is completed, the user receives a gift. ...
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (384-dim, runs
locally, no API cost), stored in **ChromaDB** (local persistent vector store)
and ranked by **cosine** similarity. Retrieval returns the **top-5** chunks.

**Production tradeoff reflection:** MiniLM is right for a student-scale English
project — small, fast, free, local. For a real deployment with no cost
constraint I'd weigh:
- **Context length / truncation:** MiniLM's 256-token cap is its biggest
  limitation here (it forces the 800-char chunk cap). A longer-context model
  (OpenAI `text-embedding-3`, BGE-M3) could embed whole long FAQ entries/tables.
- **Multilingual support:** Infinity Nikki is a Chinese-developed global game; a
  multilingual model (BGE-M3, multilingual-E5) would serve non-English queries.
- **Domain accuracy:** game jargon ("Whimstar," "Sovereign") is out-of-distribution
  for general models; a larger/fine-tuned model would embed it more faithfully.
- **Latency & cost vs. local:** hosted models add latency/cost but scale better;
  local has zero marginal cost but must be hosted. Local wins at this scale.

### Retrieval test examples (top-3 chunks, cosine distance)

**Query 1 — "How do I stop the Choo-Choo Train?"**
```
0.185  FAQs-quests-and-challenges.txt :: -stoptrain
0.408  FAQs-general-gameplay.txt :: -train
0.509  wiki-mainquest.txt :: WISHFIELD ARC
```
*Why relevant:* The top hit is the exact `-stoptrain` FAQ entry (very low
distance, 0.185). Ranks 2–3 are topically adjacent train content (how to access
the train; the Ghost Train story quest) — correctly related but not the precise
"how to stop it" answer, which is why the gap from 0.185 → 0.408 is large.

**Query 2 — "Where are my saved photos on PC if I play through Steam?"**
```
0.285  FAQs-misc-and-customer-support.txt :: -photos
0.536  FAQs-misc-and-customer-support.txt :: -photos
0.679  FAQs-misc-and-customer-support.txt :: -uid
```
*Why relevant:* Both top chunks come from the `-photos` entry, which lists the
per-platform screenshot file paths (including the Steam path). Rank 3 is `-uid`,
which is relevant because it also discusses locating PC file paths/folders — a
sensible near-miss the embedding picks up on.

**Query 3 — "How does pity work on a 5-star limited resonance banner?"**
```
0.333  FAQs-general-gameplay.txt :: -pity
0.384  FAQs-general-gameplay.txt :: -pity
0.501  FAQs-general-gameplay.txt :: -pity
```
All three top chunks are from the correct `-pity` entry — but see the Failure
Case Analysis: the entry was split such that the "5-Star Limited" *heading* and
its *rule bullets* landed in different chunks.

---

## Grounded Generation

**System prompt grounding instruction** (`rag.py`):
> "You are The Unofficial Guide... Answer the user's question using ONLY the
> information in the provided sources. Do not use outside or prior knowledge. If
> the sources do not contain enough information to answer, reply exactly: *'I
> don't have enough information on that.'* When you do answer, cite the source
> file(s) you used in square brackets, e.g. `[FAQs-general-gameplay.txt]`."

**Structural choices that enforce grounding:**
- Retrieved chunks are formatted into a **numbered, source-labeled context
  block** (`[1] (source: file — section) ...`) injected into the user message,
  so the model sees exactly which text came from where.
- Generation runs at **temperature 0.2** to minimize improvisation.
- A **fixed refusal string** lets us detect out-of-scope answers programmatically.

**How source attribution is surfaced:** the model cites source files inline in
square brackets, *and* the app separately lists the retrieved source files in a
"Retrieved from" panel.

### Example responses (attribution visible)

**In-scope #1 — "How do I stop the Choo-Choo Train?"**
> To stop the Choo-Choo Train... you must stop the first red carriage within the
> golden box. If you overshoot, reverse and pause until the nose of the train is
> inside the box. **[FAQs-quests-and-challenges.txt]**

**In-scope #2 — "What are the total rewards for Itzaland Chapter 1?"**
> Mira EXP: 2K, Resonite Crystal: 2, Diamond: 100, Bling: 40K, Thread of Purity:
> 200, Shiny Bubbles: 200, Rayplume: Head/Hands/Feet, plus Quirky Shroomling and
> Shroomling Curiosity sketches. **[wiki-itzalandarc.txt — ITZALAND CHAPTER 1]**

**Out-of-scope — "What is the best pizza topping in New York City?"**
> I don't have enough information on that.

(The retriever still returned its nearest chunks — `-blings`, `-kindled`,
abilities — but none answer the question, so the grounding prompt forced a refusal.)

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How do I stop the Choo-Choo Train (Junior Conductor)? | Stop first red carriage in the golden box; reverse if overshot; only 1 passenger needs to disembark. | Correctly explained the golden-box stop + reverse, cited `-stoptrain`. (Omitted the 1-passenger detail.) | Relevant (top 0.185) | Accurate |
| 2 | On a 5★ Limited banner, pulls to guarantee a 5★ and max to complete a set? | 5★ every 20 pulls; max = 20 × pieces (10-piece = 200). | **Refused** ("I don't have enough information on that") despite retrieving `-pity` chunks. | Partially relevant (right doc, fragmented) | **Inaccurate** |
| 3 | Diamond cost to buy Vital Energy, and how often? | 80 energy up to 6×/day: 50 → 100 → 100 → 150 → 200 → 200. | Gave the full progression and 6×/day, cited `-shop` + `pearfect-realms`. | Relevant | Accurate |
| 4 | Total rewards for Itzaland Chapter 1? | Mira EXP 2K, Resonite ×2, Diamond 100, Bling 40K, Purity 200, Bubbles 200, Rayplume ×3, 2 sketches. | Listed all rewards exactly, cited `wiki-itzalandarc`. | Relevant | Accurate |
| 5 | Saved photos path on PC via Steam? | SteamLibrary › steamapps › common › InfinityNikki › InfinityNikki › X6Game › ScreenShot. | Gave the exact Steam path, cited `-photos`. | Relevant (top 0.285) | Accurate |

**Result: 4/5 accurate, 1 inaccurate (Q2).**
**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Q2 — *"On a 5-star Limited Resonance banner, how many
pulls guarantee a 5-star, and what's the max to complete a full set?"*

**What the system returned:** *"I don't have enough information on that."* — a
refusal, even though the `-pity` document contains the exact answer and four
`-pity` chunks were retrieved in the top 5.

**Root cause (tied to the chunking stage):** The `-pity` FAQ entry is longer than
the 800-char cap, so `pipeline.py` sub-split it on paragraph boundaries. The cut
fell **between the sub-heading "5-Star Limited Resonance Pity Rules:" and its
bullet list**. As a result:
- One retrieved chunk was the **heading alone** (`...5-Star Limited Resonance Pity Rules:`) with no content beneath it.
- Another retrieved chunk held the **answer bullets** ("Every 20 pulls, you are guaranteed a 5-star item"; "max = 20 × the number of pieces"; "10-piece set = 200 pulls") **but stripped of the "5-Star Limited" heading** — the continuation-header logic re-attaches the `COMMAND:` name, not the sub-heading.

So the bullets were present but no longer attributable to the *Limited* banner
(vs. Permanent / 4-star rules, which were also in context). Faced with that
ambiguity and a strict grounding prompt, the model chose to refuse rather than
risk mis-attributing the rule. This is a "relevant info split across a chunk
boundary" failure: retrieval found the right document, but chunking severed the
heading–content link the model needed.

**What I would change to fix it:** Make the chunker **heading-aware** — when a
section is force-split, detach a trailing heading line and attach it to the
*following* chunk (so a heading is never orphaned from its content), and prepend
the nearest preceding sub-heading (not just the `COMMAND:` name) to continuation
pieces. Alternatively, raise the cap for short entries or use a model with a
larger token window so the whole `-pity` entry stays in one chunk.

---

## Spec Reflection

**One way the spec helped me during implementation:** Deciding the chunking
approach in `planning.md` *before* coding — structure-first splitting on `---`/`===`
plus an ~800-char cap justified by MiniLM's 256-token truncation limit —
translated almost directly into `pipeline.py`. Because I'd already reasoned out
*why* 800 characters (token limit, dense emoji/URL tokenization), I avoided the
classic bug of embedding oversized chunks that get silently truncated, and the
implementation was a faithful build of the spec rather than guesswork.

**One way my implementation diverged from the spec, and why:** The spec said
wide tables would be "split per logical group with the header row repeated." In
practice the big tables (`wiki-outfits`, `wiki-miralevel`) have no blank lines
between rows, so they fall through to fixed-window character splitting *without*
header repetition. I accepted this because none of the five eval questions target
an individual table row, and it was better to ship a working honest pipeline than
to over-engineer table handling. I also *added* two things the spec didn't
mention — a third structural mode (markdown headings, for `pearfect-realms.txt`)
and a continuation context-header — once the documents made the need obvious.

---

## AI Usage

I used **Claude (Claude Code)** throughout, directing it section by section and
reviewing/testing every output. Selected instances:

**Instance 1 — Document cleaning & corpus design**
- *What I gave the AI:* Raw copy-pasted Fandom Wiki / Discord / Reddit pages and
  the instruction to clean them into RAG-ready `.txt` files (strip boilerplate,
  keep substance, add consistent structure).
- *What it produced:* Cleaned files with `Source:` headers and `===` section
  banners; it converted smushed wiki tables into proper markdown and flagged
  issues (e.g. an empty `guides-quests.txt`, LaTeX in `pearfect-realms.txt`).
- *What I changed or overrode:* I directed it to **split** the one large FAQ file
  into three category files (and later weighed keeping it as one); I decided to
  flatten the LaTeX to plain text; and I had it preserve specific data (URLs,
  emoji tokens) rather than strip everything.

**Instance 2 — Structure-aware chunker (`pipeline.py`)**
- *What I gave the AI:* My Chunking Strategy section from `planning.md` (split on
  `---`/`===`, ~800-char cap, 120-char overlap, token-limit reasoning).
- *What it produced:* A custom chunker (no langchain dependency) plus an inspector
  printing counts and sample chunks.
- *What I changed or overrode:* The first run produced chunks **over** the 800-char
  cap and long FAQ entries lost context when split. I directed adding a
  **char budget that reserves room for a prepended `COMMAND:`/title context
  header** on continuation pieces, which fixed both (max chunk dropped to exactly
  800). I also pushed to reconcile `planning.md` with what we actually built.

**Instance 3 — Evaluation & honest failure analysis**
- *What I gave the AI:* My 5 planning.md test questions and the request to run
  them end-to-end and analyze results.
- *What it produced:* `evaluate.py` and a run showing 4/5 accurate with Q2 refusing.
- *What I changed or overrode:* Rather than tune the pipeline to force a perfect
  5/5, I chose to **keep the Q2 failure and document its real cause** (heading
  split from content), since an explained failure is more valuable than a
  suspiciously perfect score.

---

## Query Interface

Built with **Gradio** (`app.py`).
- **Input:** a single text box, *"Your question"* (also triggers on Enter).
- **Outputs:** an **"Answer"** box (the grounded response with inline `[source]`
  citations) and a **"Retrieved from"** box listing the source documents the
  answer drew on. Example questions are provided as clickable presets.

**Sample interaction transcript:**
```
Your question:  How do I stop the Choo-Choo Train?

Answer:
  To stop the Choo-Choo Train for the "Junior Conductor, Set Off!" quest, you
  must stop the first red carriage within the golden box. If you overshoot,
  reverse and pause until the nose of the train is inside the box.
  [FAQs-quests-and-challenges.txt]

Retrieved from:
  • FAQs-quests-and-challenges.txt — -stoptrain
  • FAQs-general-gameplay.txt — -train
  • wiki-mainquest.txt — WISHFIELD ARC
```
