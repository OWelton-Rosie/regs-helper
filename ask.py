from openai import OpenAI
from dotenv import load_dotenv
from search import search

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """
You are an assistant for the World Cube Association Regulations.

CRITICAL RULES:
- Use ONLY the provided regulations.
- Do NOT use outside knowledge.
- FMC, Blindfolded, and Head-to-Head regulations only apply if explicitly relevant.
- Prefer standard speedsolving regulations unless the question specifically concerns special event formats.
- Always cite regulation IDs.
- Be concise and factual.
- Do NOT invent rules.

If the answer is not explicitly supported by the provided regulations, say:
"I could not find a clear regulation covering this."

OUTPUT FORMAT:

Answer:
<direct answer>

Relevant Regulations:
- <rule IDs>

Explanation:
<brief explanation grounded in the regulations>
"""


def ask(question: str):

    # Retrieve relevant rules
    results = search(question)

    # Build context block
    context = "\n\n".join(
        f"[Article {r['article']}] {r['id']}: {r['text']}"
        for r in results
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Question:
{question}

Relevant Regulations:
{context}

Answer ONLY using these regulations.
"""
            }
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    while True:

        q = input("Type a question here > ")

        print("\n" + ask(q))