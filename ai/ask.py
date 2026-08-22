import json

from openai import OpenAI
from dotenv import load_dotenv

from ai.search import search


# -------------------------
# Environment
# -------------------------

load_dotenv()

client = OpenAI()


# -------------------------
# Regulations version
# -------------------------

REGULATIONS_VERSION = "April 1, 2026"

REGULATIONS_RELEASE_URL = (
    "https://github.com/thewca/wca-regulations/"
    "releases/tag/official-2026-04-01"
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
# Unsafe request detection
# -------------------------

def is_unsafe_request(question):

    query = question.lower()

    indicators = (
        # Cheating / exploitation
        "what loopholes",
        "which loopholes",
        "how can i exploit",
        "how could i exploit",
        "how do i exploit",
        "how can i cheat",
        "how could i cheat",
        "how do i cheat",
        "how to cheat",
        "exploit the regulations",
        "exploit a loophole",
        "exploit loopholes",

        # Detection / enforcement evasion
        "avoid getting caught",
        "avoid getting detected",
        "avoid detection",
        "evade detection",
        "get away with",

        # Penalty / DNF evasion
        "avoid getting a dnf",
        "avoid a dnf",
        "avoid getting dnf",
        "avoid disqualification",
        "avoid a disqualification",
        "evade a penalty",
        "avoid a penalty",
        "get out of a dnf",
        "get out of disqualification",

        # Unfair advantage
        "gain an unfair advantage",
        "get an unfair advantage",
        "gain an advantage by breaking",
        "gain an advantage from breaking",
    )

    return any(
        indicator in query
        for indicator in indicators
    )


# -------------------------
# System prompt
# -------------------------

SYSTEM_PROMPT = """
You answer questions about the World Cube Association Regulations.

Use ONLY the supplied regulation text.

The supplied regulations are the authoritative source for the answer.
Do not use outside knowledge.

Your task is to determine whether the supplied regulations contain
enough information to answer the question.

Rules:

1. Do not use outside knowledge.

2. Do not invent facts, rules, penalties, procedures, exceptions,
   definitions, or interpretations.

3. Do not infer a rule from the absence of a rule.

4. Do not treat a regulation as applicable merely because it contains
   similar words. The regulation must actually support the claim being
   made.

5. Preserve the exact meaning of "may", "should", "must", "must not",
   and "should not".

6. Do not combine regulations unless their text explicitly supports
   the combination.

7. Set "answerable" to false only when the supplied regulations genuinely
   lack enough information to answer the question.

8. A question is answerable when its answer can be obtained by directly
   reading or reasonably interpreting the supplied regulation text.

9. Do not require a regulation to use exactly the same wording as the
   question. If a regulation directly states the relevant rule using
   different wording, use that rule to answer the question.

10. Direct interpretation of supplied regulation text is permitted.
    Unsupported assumptions are not.

11. If a regulation explicitly specifies a condition, limit, procedure,
    penalty, or exception, that information may be used to answer a
    question asking about that condition, limit, procedure, penalty,
    or exception.

12. If the question contains a hypothetical scenario, answer only to
    the extent that the supplied regulations explicitly cover the
    scenario or allow a direct interpretation of it.

13. Do not assume that an official will exercise discretion in a
    particular way. If a regulation gives an official discretion,
    accurately describe that discretion.

14. Do not provide strategies for cheating, exploiting loopholes,
    evading detection, or avoiding penalties.

15. If a question asks about a potential loophole, do not explain how
    a competitor could exploit it. The application should refuse such
    requests rather than turning the request into an operational guide.

16. If answering the question requires information that is not present
    in the supplied regulations, set "answerable" to false.

17. Every regulation ID in the "regulations" array must directly support
    the answer.

18. The "regulations" array may contain ONLY regulation IDs supplied in
    the context.

19. Do not cite a regulation merely because it is related to the topic.
    It must support a factual claim actually made in the answer or
    explanation.

20. Do not include information from regulations that are not relevant
    to the question merely to make the answer more comprehensive.

21. Keep the answer concise and directly answer the question.

22. When one supplied regulation directly answers the question, prefer
    that regulation as the primary citation.

23. Do not omit a directly applicable regulation merely because other
    supplied regulations describe exceptions, related procedures, or
    consequences.

24. If a question asks whether a specific physical defect or equipment
    configuration is permitted, do not classify that specific defect
    yourself unless the supplied regulations explicitly establish that
    classification.

25. A general rule about damage, wear, differences, or puzzle
    requirements does not by itself establish that a particular physical
    defect is definitely permitted or prohibited.

26. If the regulations give an official discretion over whether a
    condition is acceptable, do not convert that discretion into a
    definite yes or no unless the supplied text explicitly does so.

27. If a question asks about a specific product, brand, edition,
    modification, or physical condition and the supplied regulations
    do not specifically establish its status, set "answerable" to false.

Return ONLY valid JSON in exactly this format:

{
  "answerable": true,
  "answer": "Direct answer to the question.",
  "regulations": ["A1", "A1a"],
  "explanation": "Brief explanation based only on those regulations."
}

For an unanswered question:

{
  "answerable": false,
  "answer": "I could not find a clear regulation covering this.",
  "regulations": [],
  "explanation": "Brief explanation of why the supplied regulations do not clearly answer the question."
}

Important:

- Do not output Markdown.
- Do not output HTML.
- Do not output URLs.
- Do not output additional JSON fields.
- Do not put regulation IDs in the answer unless they are also included
  in the "regulations" array.
"""


# -------------------------
# Fallback response
# -------------------------

def fallback_response():

    return {
        "answerable": False,
        "answer": FALLBACK_ANSWER,
        "regulations": [],
        "explanation": "",
        "sources": [],
        "regulations_version": REGULATIONS_VERSION,
        "regulations_release_url": REGULATIONS_RELEASE_URL
    }


# -------------------------
# Ask
# -------------------------

def ask(question):

    # Deterministically reject cheating,
    # exploitation, and penalty-evasion requests.
    if is_unsafe_request(question):

        return fallback_response()


    results = search(
        question
    )

    if not results:

        return fallback_response()


    # -------------------------
    # Build context
    # -------------------------

    context_parts = []

    for result in results:

        context_parts.append(
            f"Regulation {result['id']}:\n"
            f"{result['text']}"
        )

    context = "\n\n".join(
        context_parts
    )


    # -------------------------
    # Ask model
    # -------------------------

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


    raw_answer = (
        response.choices[0].message.content
        or ""
    ).strip()


    # -------------------------
    # Parse JSON
    # -------------------------

    try:

        parsed = json.loads(
            raw_answer
        )

    except json.JSONDecodeError:

        return fallback_response()


    # -------------------------
    # Validate response shape
    # -------------------------

    answerable = parsed.get(
        "answerable"
    )

    answer = parsed.get(
        "answer"
    )

    explanation = parsed.get(
        "explanation"
    )

    regulation_ids = parsed.get(
        "regulations"
    )


    if not isinstance(
        answerable,
        bool
    ):

        return fallback_response()


    if not isinstance(
        answer,
        str
    ):

        return fallback_response()


    if not isinstance(
        explanation,
        str
    ):

        explanation = ""


    if not isinstance(
        regulation_ids,
        list
    ):

        regulation_ids = []


    # -------------------------
    # Validate regulation IDs
    # -------------------------

    supplied_ids = {
        result["id"]
        for result in results
    }


    valid_regulation_ids = []

    for regulation_id in regulation_ids:

        if not isinstance(
            regulation_id,
            str
        ):

            continue

        if regulation_id not in supplied_ids:

            continue

        if regulation_id not in valid_regulation_ids:

            valid_regulation_ids.append(
                regulation_id
            )


    # -------------------------
    # Unsupported answer
    # -------------------------

    if not answerable:

        return {
            "answerable": False,
            "answer": FALLBACK_ANSWER,
            "regulations": [],
            "explanation": explanation,
            "sources": [],
            "regulations_version": REGULATIONS_VERSION,
            "regulations_release_url": REGULATIONS_RELEASE_URL
        }


    # -------------------------
    # Answer without citations
    # -------------------------

    if not valid_regulation_ids:

        return fallback_response()


    # -------------------------
    # Return structured result
    # -------------------------

    return {
        "answerable": True,
        "answer": answer,
        "regulations": valid_regulation_ids,
        "explanation": explanation,
        "sources": [
            result
            for result in results
            if result["id"]
            in valid_regulation_ids
        ],
        "regulations_version": REGULATIONS_VERSION,
        "regulations_release_url": REGULATIONS_RELEASE_URL
    }