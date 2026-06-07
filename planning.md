# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

My domain is **_Infinity Nikki_** (© Infold Games), the open-world dress-up adventure game. The system answers player questions about quests, game systems, currencies, gacha mechanics, outfits, and account/technical troubleshooting.

This knowledge is valuable and hard to find through official channels because Infold's official outlets (the website, in-game notices, and patch notes) publish _announcements and store listings_ — not practical, problem-solving answers. Players actually need things like "why won't this Forced Perspective quest register my photo," "where exactly do these materials spawn," "is this cutscene bugged," and "how does pity work on a limited banner" — none of which official sources address. That knowledge lives in community spaces: the official **Discord** (where hyper-specific guides and bot-command FAQs are maintained and questions are answered in real time), the **Fandom Wiki** (lore, quest, and item references), and **Reddit** (new-player advice and lived experience). It is also scattered across channels, inconsistently formatted, and sometimes version-specific — which is exactly why a single searchable, source-grounded Q&A system over it is genuinely useful.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

Sources span three origins (Fandom Wiki, the official Discord, and Reddit) and together cover lore/story, mechanics, progression, monetization, and real-time troubleshooting. Each was copied from its origin and cleaned into a plain-text file in `documents/` (boilerplate stripped, structure-banners added).

**Fandom Wiki pages** (base: `infinity-nikki.fandom.com/wiki/`)

| #   | Source                               | Description                                                                                                           | Local file                           |
| --- | ------------------------------------ | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | Wiki — Main Quest                    | Overview of the full main questline; detailed Wishfield-arc quest synopses (Itzaland kept as a list, pointing to #2). | `documents/wiki-mainquest.txt`       |
| 2   | Wiki — Itzaland Arc (Prologue–Ch. 5) | Per-chapter synopses, total rewards, and character lists for the v2.0 Itzaland story arc.                             | `documents/wiki-itzalandarc.txt`     |
| 3   | Wiki — Outfits                       | List of 657 outfits with rarity, style, labels, and Compendium category.                                              | `documents/wiki-outfits.txt`         |
| 4   | Wiki — Ability                       | World / collecting / area / fun abilities and their Ability Outfits.                                                  | `documents/wiki-ability.txt`         |
| 5   | Wiki — Mira Level                    | Player leveling system; per-level rewards (100 levels) and Mira EXP tables.                                           | `documents/wiki-miralevel.txt`       |
| 6   | Wiki — Heart of Infinity             | The three Shards, progression trees, and node-unlock currencies.                                                      | `documents/wiki-heartofinfinity.txt` |
| 7   | Wiki — Pear-Pal                      | The in-game tablet hub: profile and every app's function.                                                             | `documents/wiki-pearpal.txt`         |
| 8   | Wiki — Compendium                    | Collection-point rating system and the 19 Outfit Compendium categories.                                               | `documents/wiki-compendium.txt`      |

**Official Discord — bot commands & guide threads** (`discord.gg/infinitynikki`)

| #   | Source                                                  | Description                                                                                                          | Local file                                     |
| --- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 9   | `bot-playground` FAQ commands — Quests & Challenges     | 12 command answers for quest/challenge troubleshooting (e.g. `-stoptrain`, `-dqtrails`, `-kindled`).                 | `documents/FAQs-quests-and-challenges.txt`     |
| 10  | `bot-playground` FAQ commands — General Gameplay        | 50 command answers on systems, currencies, gacha pity, and monetization (e.g. `-pity`, `-shop`, `-blings`).          | `documents/FAQs-general-gameplay.txt`          |
| 11  | `bot-playground` FAQ commands — Misc & Customer Support | 10 command answers on accounts, bug reports, redeem codes, and support (e.g. `-account`, `-blackscreen`, `-photos`). | `documents/FAQs-misc-and-customer-support.txt` |
| 12  | Discord master guide thread                             | Compiled community guides: Silvergale materials, housing/animal codes, Behemoth Fawnlings, etc.                      | `documents/guides-masterthread.txt`            |
| 13  | "Realm Challenges 101" (Pear-fect Guides)               | The Vital Energy system plus all six Realm Challenge types — unlocks, costs, and rewards.                            | `documents/pearfect-realms.txt`                |

**Reddit** (`reddit.com/r/InfinityNikki/`)

| #   | Source                                                    | Description                                                                                      | Local file                       |
| --- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------- |
| 14  | r/InfinityNikki — "Just Downloaded!" thread (11 Jan 2025) | Community new-player advice: pacing, spending priorities, Pear-Pal walkthrough, late-story prep. | `documents/reddit-newplayer.txt` |

> Note: `documents/guides-quests.txt` is currently **empty (0 bytes)** — populate it or remove it before ingestion so it isn't counted as a source.

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** Structure-first, with a soft cap of ~800 characters (≈ 200 tokens) per chunk.

**Overlap:** None between structural units (each is self-contained); ~120 characters (1–2 sentences) only when a long section must be sub-split.

**Reasoning:**
The corpus has three natural structures I built in during cleaning, so I split on those boundaries instead of using blind fixed-width windows:

- **FAQ files** are delimited by lines containing only `---`, and each entry is a complete, self-contained Q&A (`COMMAND` + question + answer). One entry → one chunk. This makes the retrieval unit match the query unit: a user question maps to exactly one command's answer, and the `---` boundary never cuts an answer in half the way a 400-character window would.
- **Wiki/guide files** use `===` section banners, so each chunk is one coherent topic (e.g. "Vital Energy System", "Itzaland Chapter 1").
- **Markdown-structured guides** (e.g. `pearfect-realms.txt`) use `#`/`##` headings; splitting on level-1/2 headings keeps each section together with its `###` sub-headings rather than fragmenting them.

The ~800-character cap exists because the embedding model, `all-MiniLM-L6-v2`, **truncates input at 256 tokens** — anything longer is silently dropped and becomes unretrievable. English averages ~4 characters per token (≈1,000 chars for 256 tokens), but the Discord docs contain emoji shortcodes (`:zBling_in:`) and URLs that tokenize into many tokens per "word," so capping at ~800 chars keeps essentially every chunk fully embedded with margin. Most FAQ entries and wiki sections already fall under the cap and are kept whole; only oversized ones (e.g. `-shop`, `-pity`, and the large `wiki-outfits` / `wiki-miralevel` tables) get sub-split — on internal sub-headings/blank lines first, then by the character cap.

Overlap is applied **surgically**: it only helps when continuous prose is force-cut, so it's used on secondary splits but _not_ between whole `---`/`===` units (where overlap would merely duplicate a complete answer and pollute retrieval). When a long section is sub-split, each continuation piece is prepended with its `COMMAND:`/section title so it stays attached to its topic instead of being orphaned.

> **Implementation note (diverged from initial plan):** I originally intended to split very wide tables "per logical group with the header row repeated." In practice, the big tables (`wiki-outfits`, `wiki-miralevel`) have no blank lines between rows, so they fall through to fixed-window character splitting with overlap and the header row is **not** repeated onto each piece. This is a known limitation (see Anticipated Challenges #3), accepted because none of the five eval questions target an individual table row.

Measured total: **463 chunks** across the 14 documents (within the brief's 50–2,000 target), produced by `pipeline.py` with `MAX_CHARS=800`, `OVERLAP=120`. Each chunk carries metadata `{source, source_title, section, category?, chunk_index}`.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers` (384-dim embeddings, runs locally, no API cost), stored and queried in **ChromaDB** (local persistent vector store), ranked by cosine similarity.

**Top-k:** 5 chunks per query.

**Production tradeoff reflection:**
`all-MiniLM-L6-v2` is the right call for this project — small, fast, free, and local, which suits a student-scale English corpus. If I were deploying for real users and cost weren't a constraint, I'd weigh:

- **Context length / truncation:** MiniLM's 256-token limit is its biggest weakness here (it's what forces my ~800-char cap). A longer-context model (e.g. OpenAI `text-embedding-3` or BGE-M3) could embed whole long FAQ entries and tables without sub-splitting, improving recall on multi-part answers.
- **Multilingual support:** _Infinity Nikki_ is a Chinese-developed global game with a multilingual player base, so queries may arrive in other languages. A multilingual model (BGE-M3, multilingual-E5) would serve non-English players that English-centric MiniLM does not.
- **Domain accuracy:** Game jargon ("Whimstar," "Sovereign," "Realm of the Dark") is out-of-distribution for general models. A larger or fine-tuned model would embed these terms more faithfully, raising retrieval precision.
- **Latency & cost vs. local:** API-hosted models add per-call latency and cost but remove local compute/memory needs and scale better; a local model has zero marginal cost but must be hosted and can bottleneck under load. For a small project, local MiniLM wins; at scale, a hosted model with batching/caching is usually worth it.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

Each question targets a specific chunk in a different document, so retrieval and accuracy can both be judged objectively.

| #   | Question                                                                                                            | Expected answer                                                                                                                                                                               | Source chunk               |
| --- | ------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| 1   | How do I stop the Choo-Choo Train for the "Junior Conductor, Set Off!" quest?                                       | Stop the first red carriage inside the golden box; if you overshoot, reverse until the train's nose is in the box. You only need to disembark 1 passenger to pass, then may exit immediately. | `-stoptrain` (FAQs-quests) |
| 2   | On a 5-star Limited Resonance banner, how many pulls guarantee a 5-star, and what's the max to complete a full set? | A 5-star is guaranteed every 20 pulls (a 4-star or higher every 10). Max to complete a set = 20 × the number of pieces (e.g. a 10-piece set = 200 pulls).                                     | `-pity` (FAQs-general)     |
| 3   | What is the diamond cost to buy Vital Energy, and how many times per day?                                           | 80 Vital Energy up to 6 times/day; the diamond cost rises each time: 50 → 100 → 100 → 150 → 200 → 200.                                                                                        | pearfect-realms            |
| 4   | What are the total rewards for Itzaland Chapter 1: A Place Blessed by the Mothershroom?                             | Mira EXP 2K, Resonite Crystal ×2, Diamond 100, Bling 40K, Thread of Purity 200, Shiny Bubbles 200, Rayplume (Head/Hands/Feet), plus the Quirky Shroomling and Shroomling Curiosity sketches.  | wiki-itzalandarc           |
| 5   | Where are my saved photos on PC if I play through Steam?                                                            | install location › SteamLibrary › steamapps › common › InfinityNikki › InfinityNikki › X6Game › ScreenShot.                                                                                   | `-photos` (FAQs-misc)      |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Discord-formatting noise in embeddings and answers.** The FAQ and guide files retain emoji shortcodes (`:zBling_in:`, `:thread:`, `:zRevelationCrystal_in:`) and raw Discord image URLs. These tokens carry no semantic meaning but still get embedded, diluting the vector for a chunk, and they can leak verbatim into generated answers (e.g. the model echoing `:zBling_in:` to the user). _Mitigation: an optional preprocessing pass to strip/normalize shortcodes and URLs before embedding._

2. **Cross-document overlap returning near-duplicate chunks.** The same topic appears in multiple files — the Itzaland story is in both `wiki-itzalandarc` and `wiki-mainquest`; energy/pity mechanics recur across the FAQs and `pearfect-realms`. A top-k retrieval may fill several slots with redundant chunks, wasting context budget and biasing the answer toward whichever phrasing repeats. _Mitigation: de-duplicate retrieved chunks, or keep one canonical source per topic._

3. **Wide tables split across chunk boundaries.** `wiki-outfits` (657 rows) and `wiki-miralevel` (100-row reward/EXP tables) are far larger than one chunk. A query about a single outfit or level may retrieve a chunk that no longer contains the table's header row — or that omits the specific row entirely — so the model answers from incomplete data. _Status: only partially mitigated — prose sections split on natural boundaries, but these dense tables (no blank lines between rows) currently fall back to fixed-window character splitting **without** header repetition. A row-level or header-repeating table chunker is the planned fix; for now it's an accepted limitation since the eval set doesn't probe individual rows._

4. **Time-sensitive / version-gated facts going stale.** Server reset times, event windows (e.g. the Twitch Drops dated 29 May–22 June 2026), and patch-specific shop-pack resets are only correct for a moment in time. The system has no concept of the "current" patch, so it may confidently state outdated specifics. _Mitigation: surface source attribution so users can sanity-check, and flag dated content during ingestion._

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```text
┌──────────────────────┐
│  documents/*.txt      │  14 cleaned source files (wiki, Discord, Reddit)
└───────────┬──────────┘
            │  load  (Python open())
            ▼
┌──────────────────────┐
│  Ingestion + Clean    │  normalize whitespace; optionally strip emoji
│                       │  shortcodes
└───────────┬──────────┘
            ▼
┌──────────────────────┐
│  Structure-aware      │  split on --- (FAQ entries) and === (wiki sections);
│  Chunker (custom)     │  ~800-char cap + 120-char overlap on oversized splits;
│                       │  attach metadata {source, category}
└───────────┬──────────┘
            ▼
┌──────────────────────┐
│  Embedding            │  sentence-transformers · all-MiniLM-L6-v2 (local)
└───────────┬──────────┘
            ▼
┌──────────────────────┐
│  Vector Store         │  ChromaDB (local persistent): text + vector + metadata
└───────────┬──────────┘
            │  query: embed question → cosine top-k (k=5)
            ▼
┌──────────────────────┐
│  Retrieval            │  returns top-5 chunks + their source metadata
└───────────┬──────────┘
            │  inject chunks into grounding prompt
            ▼
┌──────────────────────┐
│  Generation           │  Groq · llama-3.3-70b-versatile, grounded prompt
│                       │  ("answer ONLY from context, else refuse")
└───────────┬──────────┘
            ▼
┌──────────────────────┐
│  Gradio UI            │  question in → answer + retrieved sources out
└──────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

I'm using **Claude (Claude Code)** as the primary AI collaborator. For each milestone I give it the relevant section of this `planning.md` plus `requirements.txt`, then review and test every output against the spec before accepting it.

**Milestone 3 — Ingestion and chunking:** Give Claude the **Chunking Strategy** section and ask it to implement a custom `load_documents()` and `chunk_document()` — splitting on `---` / `===`, applying the ~800-char cap with 120-char overlap on oversized sections, and attaching `{source, category}` metadata. Verify by printing 5 sample chunks per document type, confirming each is a readable standalone unit with no truncated tails, and checking the total chunk count lands in the 50–2,000 range.

**Milestone 4 — Embedding and retrieval:** Give Claude the **Retrieval Approach** section and ask it to implement embedding with `all-MiniLM-L6-v2`, storage in ChromaDB, and a `retrieve(query, k=5)` function. Verify by running 3 of my 5 eval questions and checking the returned chunks are relevant (cosine distance < ~0.5) and come from the expected source files.

**Milestone 5 — Generation and interface:** Give Claude the grounding requirement and ask it to implement `ask(question)` (Groq `llama-3.3-70b-versatile` with a context-only prompt that refuses when context is insufficient) plus a Gradio UI exposing a question input and an answer + sources output. Verify by asking an in-scope question (expect a cited answer) and an out-of-scope question (expect the "I don't have enough information" refusal).
