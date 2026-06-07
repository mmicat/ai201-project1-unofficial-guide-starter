"""
Milestone 5 — Query interface (Gradio).

Input:  a plain-language question about Infinity Nikki.
Output: a grounded answer (with inline source citations) plus the list of source
        documents the answer was retrieved from.

Run:
    python app.py
then open http://localhost:7860
"""

import gradio as gr

from rag import ask

EXAMPLES = [
    "How do I stop the Choo-Choo Train?",
    "How does pity work on a 5-star limited resonance banner?",
    "Where do I find Silver Petals?",
    "What are the total rewards for Itzaland Chapter 1?",
]


def handle_query(question):
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = ask(question.strip())
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — Infinity Nikki") as demo:
    gr.Markdown(
        "# The Unofficial Guide — Infinity Nikki\n"
        "Ask a question about quests, systems, currencies, outfits, or troubleshooting. "
        "Answers are grounded in community-sourced documents and cite where they came from."
    )
    question = gr.Textbox(label="Your question", placeholder="e.g. How does pity work?")
    ask_btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    gr.Examples(examples=EXAMPLES, inputs=question)
    ask_btn.click(handle_query, inputs=question, outputs=[answer, sources])
    question.submit(handle_query, inputs=question, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
