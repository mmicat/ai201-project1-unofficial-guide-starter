# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

My domain of choice is _Infinity Nikki_ (© Infold Games, ALL RIGHTS RESERVED).
While unofficial wiki/s exist, numerous pages within may not be as complete as they are elsewhere, like on the official Infinity Nikki Discord server, where media, lore, and hyper-specific guides are shared and maintained, and player questions of all kinds can be answered in real time. On channels like Reddit, ... (enhance this)

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

Sources span three origins (Fandom Wiki, the official Discord, and Reddit) and together cover lore/story, mechanics, progression, monetization, and real-time troubleshooting. Each was copied from its origin and cleaned into a plain-text file in `documents/` (boilerplate stripped, structure-banners added).

**Fandom Wiki pages** (base: `infinity-nikki.fandom.com/wiki/`)

| #   | Source | Description | Local file |
| --- | ------ | ----------- | ---------- |
| 1 | Wiki — Main Quest | Overview of the full main questline; detailed Wishfield-arc quest synopses (Itzaland kept as a list, pointing to #2). | `documents/wiki-mainquest.txt` |
| 2 | Wiki — Itzaland Arc (Prologue–Ch. 5) | Per-chapter synopses, total rewards, and character lists for the v2.0 Itzaland story arc. | `documents/wiki-itzalandarc.txt` |
| 3 | Wiki — Outfits | List of 657 outfits with rarity, style, labels, and Compendium category. | `documents/wiki-outfits.txt` |
| 4 | Wiki — Ability | World / collecting / area / fun abilities and their Ability Outfits. | `documents/wiki-ability.txt` |
| 5 | Wiki — Mira Level | Player leveling system; per-level rewards (100 levels) and Mira EXP tables. | `documents/wiki-miralevel.txt` |
| 6 | Wiki — Heart of Infinity | The three Shards, progression trees, and node-unlock currencies. | `documents/wiki-heartofinfinity.txt` |
| 7 | Wiki — Pear-Pal | The in-game tablet hub: profile and every app's function. | `documents/wiki-pearpal.txt` |
| 8 | Wiki — Compendium | Collection-point rating system and the 19 Outfit Compendium categories. | `documents/wiki-compendium.txt` |

**Official Discord — bot commands & guide threads** (`discord.gg/infinitynikki`)

| #   | Source | Description | Local file |
| --- | ------ | ----------- | ---------- |
| 9 | `bot-playground` FAQ commands — Quests & Challenges | 12 command answers for quest/challenge troubleshooting (e.g. `-stoptrain`, `-dqtrails`, `-kindled`). | `documents/FAQs-quests-and-challenges.txt` |
| 10 | `bot-playground` FAQ commands — General Gameplay | 50 command answers on systems, currencies, gacha pity, and monetization (e.g. `-pity`, `-shop`, `-blings`). | `documents/FAQs-general-gameplay.txt` |
| 11 | `bot-playground` FAQ commands — Misc & Customer Support | 10 command answers on accounts, bug reports, redeem codes, and support (e.g. `-account`, `-blackscreen`, `-photos`). | `documents/FAQs-misc-and-customer-support.txt` |
| 12 | Discord master guide thread | Compiled community guides: Silvergale materials, housing/animal codes, Behemoth Fawnlings, etc. | `documents/guides-masterthread.txt` |
| 13 | "Realm Challenges 101" (Pear-fect Guides) | The Vital Energy system plus all six Realm Challenge types — unlocks, costs, and rewards. | `documents/pearfect-realms.txt` |

**Reddit** (`reddit.com/r/InfinityNikki/`)

| #   | Source | Description | Local file |
| --- | ------ | ----------- | ---------- |
| 14 | r/InfinityNikki — "Just Downloaded!" thread (11 Jan 2025) | Community new-player advice: pacing, spending priorities, Pear-Pal walkthrough, late-story prep. | `documents/reddit-newplayer.txt` |

> Note: `documents/guides-quests.txt` is currently **empty (0 bytes)** — populate it or remove it before ingestion so it isn't counted as a source.

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

Each question targets a specific chunk in a different document, so retrieval and accuracy can both be judged objectively.

| #   | Question | Expected answer | Source chunk |
| --- | -------- | --------------- | ------------ |
| 1 | How do I stop the Choo-Choo Train for the "Junior Conductor, Set Off!" quest? | Stop the first red carriage inside the golden box; if you overshoot, reverse until the train's nose is in the box. You only need to disembark 1 passenger to pass, then may exit immediately. | `-stoptrain` (FAQs-quests) |
| 2 | On a 5-star Limited Resonance banner, how many pulls guarantee a 5-star, and what's the max to complete a full set? | A 5-star is guaranteed every 20 pulls (a 4-star or higher every 10). Max to complete a set = 20 × the number of pieces (e.g. a 10-piece set = 200 pulls). | `-pity` (FAQs-general) |
| 3 | What is the diamond cost to buy Vital Energy, and how many times per day? | 80 Vital Energy up to 6 times/day; the diamond cost rises each time: 50 → 100 → 100 → 150 → 200 → 200. | pearfect-realms |
| 4 | What are the total rewards for Itzaland Chapter 1: A Place Blessed by the Mothershroom? | Mira EXP 2K, Resonite Crystal ×2, Diamond 100, Bling 40K, Thread of Purity 200, Shiny Bubbles 200, Rayplume (Head/Hands/Feet), plus the Quirky Shroomling and Shroomling Curiosity sketches. | wiki-itzalandarc |
| 5 | Where are my saved photos on PC if I play through Steam? | install location › SteamLibrary › steamapps › common › InfinityNikki › InfinityNikki › X6Game › ScreenShot. | `-photos` (FAQs-misc) |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Discord-formatting noise in embeddings and answers.** The FAQ and guide files retain emoji shortcodes (`:zBling_in:`, `:thread:`, `:zRevelationCrystal_in:`) and raw Discord image URLs. These tokens carry no semantic meaning but still get embedded, diluting the vector for a chunk, and they can leak verbatim into generated answers (e.g. the model echoing `:zBling_in:` to the user). *Mitigation: an optional preprocessing pass to strip/normalize shortcodes and URLs before embedding.*

2. **Cross-document overlap returning near-duplicate chunks.** The same topic appears in multiple files — the Itzaland story is in both `wiki-itzalandarc` and `wiki-mainquest`; energy/pity mechanics recur across the FAQs and `pearfect-realms`. A top-k retrieval may fill several slots with redundant chunks, wasting context budget and biasing the answer toward whichever phrasing repeats. *Mitigation: de-duplicate retrieved chunks, or keep one canonical source per topic.*

3. **Wide tables split across chunk boundaries.** `wiki-outfits` (657 rows) and `wiki-miralevel` (100-row reward/EXP tables) are far larger than one chunk. A query about a single outfit or level may retrieve a chunk that no longer contains the table's header row — or that omits the specific row entirely — so the model answers from incomplete data. *Mitigation: structure-aware chunking that keeps headers with rows, or row-level records.*

4. **Time-sensitive / version-gated facts going stale.** Server reset times, event windows (e.g. the Twitch Drops dated 29 May–22 June 2026), and patch-specific shop-pack resets are only correct for a moment in time. The system has no concept of the "current" patch, so it may confidently state outdated specifics. *Mitigation: surface source attribution so users can sanity-check, and flag dated content during ingestion.*

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
