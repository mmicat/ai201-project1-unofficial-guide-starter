"""
Milestone 6 — Evaluation harness.

Runs the 5 planning.md test questions through ask() and prints, for each:
the question, the expected answer, the system's actual answer, the cited sources,
and the top-k retrieved chunks (with cosine distances) for failure analysis.

    python evaluate.py
"""

from rag import ask

EVAL = [
    (
        "How do I stop the Choo-Choo Train for the \"Junior Conductor, Set Off!\" quest?",
        "Stop the first red carriage inside the golden box; if you overshoot, reverse "
        "until the train's nose is in the box. Only 1 passenger needs to disembark to pass.",
    ),
    (
        "On a 5-star Limited Resonance banner, how many pulls guarantee a 5-star, "
        "and what's the max to complete a full set?",
        "A 5-star is guaranteed every 20 pulls (a 4-star+ every 10). Max to complete a "
        "set = 20 x number of pieces (e.g. a 10-piece set = 200 pulls).",
    ),
    (
        "What is the diamond cost to buy Vital Energy, and how many times per day?",
        "80 Vital Energy up to 6 times/day; diamond cost rises each time: "
        "50, 100, 100, 150, 200, 200.",
    ),
    (
        "What are the total rewards for Itzaland Chapter 1: A Place Blessed by the Mothershroom?",
        "Mira EXP 2K, Resonite Crystal x2, Diamond 100, Bling 40K, Thread of Purity 200, "
        "Shiny Bubbles 200, Rayplume (Head/Hands/Feet), plus Quirky Shroomling and "
        "Shroomling Curiosity sketches.",
    ),
    (
        "Where are my saved photos on PC if I play through Steam?",
        "SteamLibrary > steamapps > common > InfinityNikki > InfinityNikki > X6Game > ScreenShot.",
    ),
]


def main():
    for i, (q, expected) in enumerate(EVAL, 1):
        result = ask(q)
        print("\n" + "#" * 78)
        print(f"Q{i}: {q}")
        print("#" * 78)
        print(f"\nEXPECTED:\n  {expected}")
        print(f"\nSYSTEM ANSWER:\n  {result['answer']}")
        print("\nCITED / RETRIEVED SOURCES:")
        for s in result["sources"]:
            print(f"  - {s}")
        print("\nTOP-5 RETRIEVED (distance | source | section):")
        for h in result["hits"]:
            md = h["metadata"]
            print(f"  {h['distance']:.3f}  {md['source']}  {md.get('section', '')}")


if __name__ == "__main__":
    main()
