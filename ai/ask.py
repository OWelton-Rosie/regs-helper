from openai import OpenAI
from dotenv import load_dotenv

from ai.search import search

load_dotenv()

client = OpenAI()

SYSTEM_PROMPT = """
You are an assistant for the World Cube Association Regulations.

Rules:
- Use ONLY the supplied regulations.
- Do not use outside knowledge.
- Always cite regulation IDs.
- If the answer is not supported by the supplied regulations, say:
  "I could not find a clear regulation covering this."

Output format:

Answer:
<answer>

Relevant Regulations:
- IDs

Explanation:
<brief explanation>
"""


def ask(question):

    results = search(question)

    context = "\n\n".join(
    f"{r['id']}: {r['text']}"
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
"""
            }
        ]
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": results
    }