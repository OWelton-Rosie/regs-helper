from openai import OpenAI
from dotenv import load_dotenv

from ai.search import search

load_dotenv()

client = OpenAI()


# -------------------------
# Regulations version
# -------------------------

REGULATIONS_VERSION = "April 1, 2026"

REGULATIONS_RELEASE_URL = (
    "https://github.com/thewca/wca-regulations/releases/tag/official-2026-04-01"
)


# -------------------------
# Fallback
# -------------------------

FALLBACK_ANSWER = (
    "I could not find a clear regulation covering this. "
    "Please consult the WCA Regulations or your WCA Delegate "
    "for more information."
)


# -------------------------
# System prompt
# -------------------------

SYSTEM_PROMPT = """
You are an assistant for the World Cube Association Regulations.

Your job is to answer questions using ONLY the supplied regulations.

Rules:

- Use ONLY the supplied regulations.
- Do not use outside knowledge.
- Do not invent regulations, rules, penalties, procedures, definitions, or exceptions.
- Every factual claim about the WCA Regulations must be supported by one or more supplied regulation IDs.
- Only cite a regulation ID when the supplied text actually supports the claim.
- Do not assume that a regulation applies merely because it contains similar words.
- Pay close attention to the event, round format, and situation described in the question.
- Prefer a regulation specifically concerning the subject of the question over a generally related regulation.
- If the supplied regulations do not clearly answer the question, say that you could not find a clear regulation covering it.
- Do not infer a rule from the absence of a regulation.
- Do not use Markdown formatting.
- Do not output HTML.
- Do not include URLs.
- Keep the answer concise and directly answer the question.

Output format:

Answer:
Give the answer directly.

Relevant Regulations:
- List only the regulation IDs that directly support the answer.

Explanation:
Briefly explain how the supplied regulations support the answer.

If the supplied regulations do not clearly support an answer, use:

Answer:
I could not find a clear regulation covering this.

Relevant Regulations:
- List the most relevant regulations only if they help explain why the supplied regulations are insufficient.

Explanation:
Briefly explain why the supplied regulations do not clearly answer the question.
"""


# -------------------------
# Ask
# -------------------------

def ask(question):

    results = search(question)

    if not results:

        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
            "regulations_version": REGULATIONS_VERSION,
            "regulations_release_url": REGULATIONS_RELEASE_URL
        }


    context = "\n\n".join(
        f"Regulation {r['id']}:\n{r['text']}"
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
                "content": (
                    f"Question:\n"
                    f"{question}\n\n"
                    f"Supplied Regulations:\n"
                    f"{context}"
                )
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