from openai import OpenAI
from dotenv import load_dotenv

from ai.search import search

load_dotenv()

client = OpenAI()


# Update these when the regs change!
REGULATIONS_VERSION = "April 1, 2026"
REGULATIONS_RELEASE_URL = (
    "https://github.com/thewca/wca-regulations/releases/tag/official-2026-04-01"
)


SYSTEM_PROMPT = """
You are an assistant for the World Cube Association Regulations.

Rules:
- Use ONLY the supplied regulations.
- Do not use outside knowledge.
- Always cite regulation IDs.
- Do not invent regulations, rules, penalties, or procedures.
- Do not use Markdown formatting.
- If the supplied regulations do not clearly support an answer, say:
  "I could not find a clear regulation covering this. Please consult the <a href="https://www.worldcubeassociation.org/regulations/" target="_blank" rel="noopener noreferrer">WCA Regulations</a> or your <a href="https://www.worldcubeassociation.org/delegates" target="_blank" rel="noopener noreferrer">WCA Delegate</a> for more information."

Output format:

Give the answer directly.

Relevant Regulations:
- IDs

Explanation:
Brief explanation
"""


def ask(question):

    results = search(question)

    if not results:
        return {
            "answer": (
                'I could not find a clear regulation covering this. '
                'Please consult the <a href="https://www.worldcubeassociation.org/regulations/" '
                'target="_blank" rel="noopener noreferrer">WCA Regulations</a> '
                'or your <a href="https://www.worldcubeassociation.org/delegates" '
                'target="_blank" rel="noopener noreferrer">WCA Delegate</a> '
                'for more information.'
            ),
            "sources": [],
            "regulations_version": REGULATIONS_VERSION,
            "regulations_release_url": REGULATIONS_RELEASE_URL
        }

    context = "\n\n".join(
        f"{r['id']}: {r['text']}"
        for r in results
    )

    response = client.chat.completions.create(
        model="gpt-5.6-terra",
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
        "sources": results,
        "regulations_version": REGULATIONS_VERSION,
        "regulations_release_url": REGULATIONS_RELEASE_URL
    }