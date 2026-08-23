import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from ai.search import search


# ============================================================
# Paths
# ============================================================

AI_DIR = Path(__file__).resolve().parent

SYSTEM_PROMPT_PATH = (
    AI_DIR / "system_prompt.txt"
)


# ============================================================
# Environment
# ============================================================

load_dotenv()

client = OpenAI()


# ============================================================
# System prompt
# ============================================================

if not SYSTEM_PROMPT_PATH.exists():

    raise FileNotFoundError(
        f"System prompt not found: "
        f"{SYSTEM_PROMPT_PATH}"
    )


with open(
    SYSTEM_PROMPT_PATH,
    "r",
    encoding="utf-8"
) as f:

    SYSTEM_PROMPT = f.read().strip()


if not SYSTEM_PROMPT:

    raise RuntimeError(
        f"System prompt is empty: "
        f"{SYSTEM_PROMPT_PATH}"
    )


# ============================================================
# Regulations version
# ============================================================

REGULATIONS_VERSION = "April 1, 2026"

REGULATIONS_RELEASE_URL = (
    "https://github.com/thewca/wca-regulations/"
    "releases/tag/official-2026-04-01"
)


# ============================================================
# Fallback
# ============================================================

FALLBACK_ANSWER = (
    "I could not find a clear regulation covering this. "
    "Please consult the WCA Regulations or your WCA Delegate "
    "for more information."
)


# ============================================================
# Hard refusal detection
# ============================================================

def is_disallowed_request(question):

    question_lower = question.lower()

    indicators = (
        "loophole",
        "loopholes",
        "exploit",
        "exploits",
        "exploit a rule",
        "exploit the rules",
        "gain an advantage",
        "gain a competitive advantage",
        "avoid getting a dnf",
        "avoid a dnf",
        "evade a penalty",
        "avoid a penalty",
        "bypass a penalty",
        "cheat",
        "cheating",
        "manipulate the rules",
        "manipulate a regulation",
        "get around the rules",
        "get around a regulation"
    )

    return any(
        indicator in question_lower
        for indicator in indicators
    )


# ============================================================
# Obviously non-regulation requests
# ============================================================

def is_obviously_non_regulation_request(question):

    question_lower = (
        question
        .lower()
        .strip()
    )

    if question_lower in {
        "test",
        "testing",
        "hello",
        "hi",
        "hey"
    }:

        return True

    if question_lower in {
        "i want to ask you a question",
        "i want to ask a question",
        "can i ask you a question"
    }:

        return True

    if (
        "favorite regulation"
        in question_lower
    ):

        return True

    if (
        "favourite regulation"
        in question_lower
    ):

        return True

    if (
        "banana bread" in question_lower
        and "regulation" not in question_lower
    ):

        return True

    # Very short unrelated messages.

    if (
        len(question_lower.split()) <= 2
        and not any(
            term in question_lower
            for term in (
                "regulation",
                "reg",
                "cube",
                "puzzle",
                "penalty",
                "dnf",
                "+2",
                "plus 2",
                "allowed",
                "legal"
            )
        )
    ):

        return True

    return False


# ============================================================
# Fallback response
# ============================================================

def fallback_response(
    explanation=""
):

    return {
        "answerable": False,
        "answer": FALLBACK_ANSWER,
        "regulations": [],
        "explanation": explanation,
        "sources": [],
        "regulations_version": REGULATIONS_VERSION,
        "regulations_release_url": REGULATIONS_RELEASE_URL
    }


# ============================================================
# Ask
# ============================================================

def ask(question):

    question = (
        question
        if isinstance(question, str)
        else str(question)
    ).strip()

    if not question:

        return fallback_response(
            "No question was supplied."
        )

    # --------------------------------------------------------
    # Hard gates
    # --------------------------------------------------------

    if is_disallowed_request(
        question
    ):

        return fallback_response(
            "The question asks for a way to exploit "
            "or evade the WCA Regulations."
        )

    if is_obviously_non_regulation_request(
        question
    ):

        return fallback_response(
            "The question does not ask for information "
            "about the WCA Regulations."
        )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    results = search(
        question
    )

    if not results:

        return fallback_response()

    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context_parts = []

    for result in results:

        context_parts.append(
            f"Regulation {result['id']}:\n"
            f"{result['text']}"
        )

    context = "\n\n".join(
        context_parts
    )

    # --------------------------------------------------------
    # Ask model
    # --------------------------------------------------------

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
        response
        .choices[0]
        .message
        .content
        or ""
    ).strip()

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        parsed = json.loads(
            raw_answer
        )

    except json.JSONDecodeError:

        return fallback_response(
            "The model did not return valid JSON."
        )

    # --------------------------------------------------------
    # Validate response shape
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Validate regulation IDs
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Unsupported answer
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Answer without citations
    # --------------------------------------------------------

    if not valid_regulation_ids:

        return fallback_response(
            "The model marked the question as answerable "
            "but did not cite any supplied regulations."
        )

    # --------------------------------------------------------
    # Return structured result
    # --------------------------------------------------------

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