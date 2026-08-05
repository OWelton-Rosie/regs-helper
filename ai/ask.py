from openai import OpenAI
from dotenv import load_dotenv

from ai.search import search

load_dotenv()

client = OpenAI()

# prompt for ai agent
SYSTEM_PROMPT = """
You are an assistant for the World Cube Association Regulations.

Rules:
- Use ONLY the supplied regulations.
- Do not use outside knowledge.
- Always cite regulation IDs.
- If the answer is not supported by the supplied regulations, say:
  "I could not find a clear regulation covering this. Please consult the <a href="https://www.worldcubeassociation.org/regulations/" target="_blank" rel="noopener noreferrer"> or your <a href="https://www.worldcubeassociation.org/delegates" target="_blank" rel="noopener noreferrer">WCA Delegate</a> for more information."

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
        model="gpt-5.6-terra", # upgrate from gpt 4.0-mini
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