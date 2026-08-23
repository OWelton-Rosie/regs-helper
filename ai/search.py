from openai import OpenAI
from dotenv import load_dotenv

import json
import re
import numpy as np

from pathlib import Path


# -------------------------
# Paths
# -------------------------

DATA_DIR = Path(__file__).parent / "data"


# -------------------------
# OpenAI
# -------------------------

load_dotenv()

client = OpenAI()


# -------------------------
# Load embeddings
# -------------------------

with open(
    DATA_DIR / "embeddings.json",
    "r",
    encoding="utf-8"
) as f:

    chunks = json.load(f)


# -------------------------
# Similarity
# -------------------------

def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    denominator = (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )

    if denominator == 0:

        return 0.0

    return np.dot(a, b) / denominator


# -------------------------
# Regulation ID detection
# -------------------------

def detect_regulation_reference(query):
    """
    Detect an exact regulation ID mentioned in the question.

    This is much more reliable than asking embeddings to recognise
    things such as "what is A7B2?".
    """

    query_lower = query.lower()

    regulation_ids = sorted(
        (
            chunk["id"]
            for chunk in chunks
            if isinstance(chunk.get("id"), str)
        ),
        key=len,
        reverse=True
    )

    for regulation_id in regulation_ids:

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(regulation_id.lower())
            + r"(?![a-z0-9])"
        )

        if re.search(
            pattern,
            query_lower
        ):

            return regulation_id

    return None


# -------------------------
# Article / format detection
# -------------------------

def detect_article(query):

    query_lower = query.lower()


    # -------------------------
    # Event-format questions
    # -------------------------

    if any(
        term in query_lower
        for term in (
            "3bld",
            "3 bld",
            "3x3 blindfolded",
            "3x3x3 blindfolded"
        )
    ):

        if any(
            term in query_lower
            for term in (
                "average",
                "avg",
                "format",
                "solve",
                "solves",
                "attempt",
                "attempts",
                "round"
            )
        ):

            return "9"


    # -------------------------
    # Multi-Blind
    # -------------------------

    if any(
        term in query_lower
        for term in (
            "multi-blind",
            "multi blind",
            "multiblind"
        )
    ):

        return "H"


    # -------------------------
    # Fewest Moves
    # -------------------------

    if any(
        term in query_lower
        for term in (
            "fewest moves",
            "fewest move",
            "fmc"
        )
    ):

        return "E"


    # -------------------------
    # Dual Rounds
    # -------------------------

    if any(
        term in query_lower
        for term in (
            "dual rounds",
            "dual round"
        )
    ):

        return "9"


    # -------------------------
    # Head to Head
    # -------------------------

    if any(
        term in query_lower
        for term in (
            "head to head",
            "head-to-head"
        )
    ):

        return "I"


    # -------------------------
    # Blindfolded procedure
    # -------------------------

    if any(
        term in query_lower
        for term in (
            "blindfolded",
            "blindfold",
            "blind solve"
        )
    ):

        return "B"


    return None


def detect_format(query):

    query_lower = query.lower()


    if any(
        term in query_lower
        for term in (
            "dual rounds",
            "dual round"
        )
    ):

        return "dual_rounds"


    if any(
        term in query_lower
        for term in (
            "head to head",
            "head-to-head"
        )
    ):

        return "head_to_head"


    if any(
        term in query_lower
        for term in (
            "fewest moves",
            "fewest move",
            "fmc"
        )
    ):

        return "fewest_moves"


    if any(
        term in query_lower
        for term in (
            "multi-blind",
            "multi blind",
            "multiblind"
        )
    ):

        return "multi_blind"


    if any(
        term in query_lower
        for term in (
            "3bld",
            "3 bld",
            "3x3 blindfolded",
            "3x3x3 blindfolded"
        )
    ):

        return "3bld"


    return None


# -------------------------
# Intent detection
# -------------------------

def detect_intents(query):

    query_lower = query.lower()


    # -------------------------
    # Changing submitted number
    # -------------------------

    asks_change = (
        "change my mind" in query_lower
        or "change the number" in query_lower
        or "change how many" in query_lower
        or "change their number" in query_lower
        or "change the number of cubes" in query_lower
        or "change the number of puzzles" in query_lower
        or (
            "change" in query_lower
            and (
                "number of cubes" in query_lower
                or "number of puzzles" in query_lower
                or "number of puzzle" in query_lower
                or "number" in query_lower
            )
        )
    )


    # -------------------------
    # Number of puzzles
    # -------------------------

    asks_number = (
        not asks_change
        and any(
            term in query_lower
            for term in (
                "minimum number",
                "maximum number",
                "number of cubes",
                "number of puzzles",
                "how many cubes",
                "minimum",
                "maximum",
                "at least",
                "at most"
            )
        )
    )


    # -------------------------
    # Disqualification
    # -------------------------

    asks_disqualification = any(
        term in query_lower
        for term in (
            "disqualified",
            "disqualification",
            "dnf",
            "penalty"
        )
    )


    # -------------------------
    # Equipment incident
    # -------------------------

    asks_equipment_problem = any(
        term in query_lower
        for term in (
            "falls off",
            "fell off",
            "fall off",
            "cap falls",
            "cap fell",
            "piece falls",
            "piece fell",
            "breaks",
            "broke",
            "break off",
            "comes off",
            "came off"
        )
    )


    # -------------------------
    # Puzzle legality
    # -------------------------

    asks_legality = any(
        term in query_lower
        for term in (
            "legal",
            "allowed",
            "permitted",
            "can i use",
            "can i compete with",
            "allowed to use",
            "permitted to use",
            "okay to use",
            "ok to use"
        )
    )


    asks_damage_or_condition = any(
        term in query_lower
        for term in (
            "missing",
            "damaged",
            "damage",
            "broken",
            "cracked",
            "loose",
            "worn",
            "wear",
            "centre cap",
            "center cap",
            "cap missing",
            "piece missing",
            "piece damaged",
            "sticker missing",
            "sticker damaged",
            "marking",
            "markings"
        )
    )


    asks_equipment_legality = (
        asks_legality
        and asks_damage_or_condition
    )


    # -------------------------
    # Timer reset
    # -------------------------

    asks_timer_reset = (
        "timer" in query_lower
        and "reset" in query_lower
    )


    # -------------------------
    # +2
    # -------------------------

    asks_plus_two = any(
        term in query_lower
        for term in (
            "+2",
            "plus 2",
            "plus two"
        )
    )


    # -------------------------
    # Official events
    # -------------------------

    asks_official_events = (
        "official events" in query_lower
        or (
            "what events" in query_lower
            and "official" in query_lower
        )
    )


    # -------------------------
    # 3BLD format
    # -------------------------

    asks_3bld_format = (
        any(
            term in query_lower
            for term in (
                "3bld",
                "3 bld",
                "3x3 blindfolded",
                "3x3x3 blindfolded"
            )
        )
        and any(
            term in query_lower
            for term in (
                "average",
                "avg",
                "format",
                "solve",
                "solves",
                "attempt",
                "attempts",
                "round"
            )
        )
    )


    # -------------------------
    # Scramble correction
    # -------------------------

    asks_scramble_correction = (
        any(
            term in query_lower
            for term in (
                "scrambler",
                "scramble"
            )
        )
        and any(
            term in query_lower
            for term in (
                "misscramble",
                "miscramble",
                "wrong state",
                "wrong scramble",
                "messed up",
                "mess up",
                "mess up scrambling",
                "incorrect state",
                "incorrect scramble",
                "rescramble",
                "re-scramble",
                "correct it"
            )
        )
    )


    # -------------------------
    # Extra attempt
    # -------------------------

    asks_extra_attempt = (
        "extra attempt" in query_lower
        or "extra attempts" in query_lower
        or (
            "can i get an extra" in query_lower
        )
        or (
            "get an extra" in query_lower
        )
    )


    # -------------------------
    # Black Square-1
    # -------------------------

    asks_black_square_one = (
        "black" in query_lower
        and (
            "square-1" in query_lower
            or "square 1" in query_lower
            or "square one" in query_lower
        )
    )


    # -------------------------
    # Reasonable wear
    # -------------------------

    asks_reasonable_wear = (
        "reasonable wear" in query_lower
        or (
            "what counts as reasonable wear"
            in query_lower
        )
    )


    return {
        "asks_change": asks_change,
        "asks_number": asks_number,
        "asks_disqualification": asks_disqualification,
        "asks_equipment_problem": asks_equipment_problem,
        "asks_legality": asks_legality,
        "asks_damage_or_condition": asks_damage_or_condition,
        "asks_equipment_legality": asks_equipment_legality,
        "asks_timer_reset": asks_timer_reset,
        "asks_plus_two": asks_plus_two,
        "asks_official_events": asks_official_events,
        "asks_3bld_format": asks_3bld_format,
        "asks_scramble_correction": asks_scramble_correction,
        "asks_extra_attempt": asks_extra_attempt,
        "asks_black_square_one": asks_black_square_one,
        "asks_reasonable_wear": asks_reasonable_wear
    }


# -------------------------
# Search
# -------------------------

def search(query, top_k=5):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )

    q_emb = response.data[0].embedding

    query_lower = query.lower()

    target_article = detect_article(query)
    target_format = detect_format(query)
    target_regulation = detect_regulation_reference(query)

    intents = detect_intents(query)

    asks_change = intents["asks_change"]
    asks_number = intents["asks_number"]
    asks_disqualification = (
        intents["asks_disqualification"]
    )
    asks_equipment_problem = (
        intents["asks_equipment_problem"]
    )
    asks_equipment_legality = (
        intents["asks_equipment_legality"]
    )
    asks_timer_reset = (
        intents["asks_timer_reset"]
    )
    asks_plus_two = (
        intents["asks_plus_two"]
    )
    asks_official_events = (
        intents["asks_official_events"]
    )
    asks_3bld_format = (
        intents["asks_3bld_format"]
    )
    asks_scramble_correction = (
        intents["asks_scramble_correction"]
    )
    asks_extra_attempt = (
        intents["asks_extra_attempt"]
    )
    asks_black_square_one = (
        intents["asks_black_square_one"]
    )
    asks_reasonable_wear = (
        intents["asks_reasonable_wear"]
    )


    # -------------------------
    # Dynamic result count
    # -------------------------

    effective_top_k = top_k

    if asks_plus_two:
        effective_top_k = max(
            effective_top_k,
            10
        )

    if asks_official_events:
        effective_top_k = max(
            effective_top_k,
            10
        )

    if asks_3bld_format:
        effective_top_k = max(
            effective_top_k,
            7
        )

    if asks_scramble_correction:
        effective_top_k = max(
            effective_top_k,
            7
        )

    if asks_extra_attempt:
        effective_top_k = max(
            effective_top_k,
            7
        )

    if target_regulation:
        effective_top_k = max(
            effective_top_k,
            3
        )


    # -------------------------
    # Score regulations
    # -------------------------

    scored = []

    for chunk in chunks:

        text_lower = chunk["text"].lower()

        regulation_id = chunk["id"]
        regulation_id_lower = regulation_id.lower()

        article = chunk.get(
            "article"
        )

        score = cosine_similarity(
            q_emb,
            chunk["embedding"]
        )


        # -------------------------
        # Exact regulation lookup
        # -------------------------

        if target_regulation:

            if regulation_id_lower == (
                target_regulation.lower()
            ):

                score += 20.0

            else:

                score -= 0.5


        # -------------------------
        # Article relevance
        # -------------------------

        if target_article:

            if article == target_article:

                score += 1.5

            else:

                score -= 0.15


        # -------------------------
        # Explicit format relevance
        # -------------------------

        if target_format == "dual_rounds":

            if regulation_id_lower == "9v":
                score += 3.0

            if regulation_id_lower == "9v4":
                score += 4.0

            if "dual rounds" in text_lower:
                score += 1.5

            elif "dual round" in text_lower:
                score += 1.25


        elif target_format == "head_to_head":

            if "head to head" in text_lower:
                score += 1.5

            if "head-to-head" in text_lower:
                score += 1.5


        elif target_format == "fewest_moves":

            if "fewest moves" in text_lower:
                score += 1.0


        elif target_format == "multi_blind":

            if regulation_id_lower == "h1":
                score += 1.0

            if article == "H":
                score += 1.0

            if "multi-blind" in text_lower:
                score += 1.25

            elif "multi blind" in text_lower:
                score += 1.25


            # -------------------------
            # Number of puzzles
            # -------------------------

            if asks_number:

                if regulation_id_lower == "h1a":
                    score += 6.0

                if regulation_id_lower == "h1a1":
                    score += 2.0

                if regulation_id_lower not in {
                    "h1a",
                    "h1a1",
                    "h1a2",
                    "h1a3"
                }:

                    if any(
                        term in text_lower
                        for term in (
                            "at most",
                            "at least",
                            "number of",
                            "number"
                        )
                    ):

                        score -= 0.5


            # -------------------------
            # Changing submitted number
            # -------------------------

            if asks_change:

                if regulation_id_lower == "h1a1":
                    score += 7.0

                if regulation_id_lower == "h1a":
                    score += 2.0

                if regulation_id_lower not in {
                    "h1",
                    "h1a",
                    "h1a1",
                    "h1a2"
                }:

                    score -= 0.5


            # -------------------------
            # Equipment incidents
            # -------------------------

            if asks_equipment_problem:

                if regulation_id_lower == "h1e":
                    score += 7.0

                if regulation_id_lower == "h1":
                    score += 1.0

                if article == "B":
                    score -= 1.0


            # -------------------------
            # Disqualification
            # -------------------------

            if asks_disqualification:

                if regulation_id_lower == "h1e":
                    score += 5.0

                if "disqualification" in text_lower:
                    score += 0.75

                if "dnf" in text_lower:
                    score += 0.75


        # -------------------------
        # Timer reset
        # -------------------------

        if asks_timer_reset:

            if regulation_id_lower == "b2a":
                score += 7.0

            if regulation_id_lower == "a3b":
                score += 7.0

            if regulation_id_lower == "a3c3+":
                score += 2.0

            if regulation_id_lower == "a6f":
                score += 2.0


        # -------------------------
        # +2 penalty
        # -------------------------

        if asks_plus_two:

            plus_two_ids = {
                "10e3",
                "a3d",
                "a4b",
                "a4b1",
                "a4d1",
                "a4d1+",
                "a6c",
                "a6d",
                "a6e2",
                "b2b",
                "b2c"
            }

            if regulation_id_lower in plus_two_ids:

                score += 7.0


            if (
                "+2" in text_lower
                or "plus 2" in text_lower
                or "time penalty (+2 seconds)"
                in text_lower
            ):

                score += 1.5


        # -------------------------
        # Official events
        # -------------------------

        if asks_official_events:

            if regulation_id_lower == "9b":
                score += 10.0

            if regulation_id_lower.startswith("9b"):
                score += 5.0

            if "official events" in text_lower:
                score += 5.0


        # -------------------------
        # 3BLD event format
        # -------------------------

        if asks_3bld_format:

            if regulation_id_lower in {
                "9b3",
                "9b3a",
                "9b3b"
            }:

                score += 8.0

            if (
                "3x3x3 blindfolded"
                in text_lower
            ):

                score += 3.0

            if "average of 5" in text_lower:
                score += 2.0

            if "best of 5" in text_lower:
                score += 2.0


        # -------------------------
        # Scramble correction
        # -------------------------

        if asks_scramble_correction:

            if regulation_id_lower == "4g":
                score += 8.0

            if regulation_id_lower == "4g1":
                score += 5.0

            if regulation_id_lower == "4g1a":
                score += 7.0

            if regulation_id_lower == "4g1a+":
                score += 5.0

            if regulation_id_lower == "4g1a++":
                score += 3.0

            if regulation_id_lower == "4g2":
                score += 3.0


        # -------------------------
        # Extra attempts
        # -------------------------

        if asks_extra_attempt:

            if regulation_id_lower == "11e":
                score += 9.0

            if regulation_id_lower == "11e+":
                score += 4.0

            if regulation_id_lower == "11e1":
                score += 3.0

            if regulation_id_lower == "11e2":
                score += 3.0

            if regulation_id_lower == "11e2+":
                score += 3.0

            if regulation_id_lower == "11e3":
                score += 3.0

            if "extra attempt" in text_lower:
                score += 2.0


        # -------------------------
        # Black Square-1
        # -------------------------

        if asks_black_square_one:

            if regulation_id_lower == "4d+":
                score += 8.0

            if regulation_id_lower == "4d3":
                score += 5.0

            if "black" in text_lower:
                score += 2.0

            if "square-1" in text_lower:
                score += 2.0


        # -------------------------
        # Reasonable wear
        # -------------------------

        if asks_reasonable_wear:

            if regulation_id_lower == "3j1":
                score += 8.0

            if regulation_id_lower == "3j1a":
                score += 7.0

            if regulation_id_lower == "3j":
                score += 3.0

            # 3h5 is a Clock-specific exception.
            # It should not pollute a generic reasonable-wear query.

            if (
                regulation_id_lower == "3h5"
                and "clock" not in query_lower
            ):

                score -= 8.0


        # -------------------------
        # Equipment legality
        # -------------------------

        if asks_equipment_legality:

            if article == "3":
                score += 1.25

            if regulation_id_lower == "3j":
                score += 4.0

            if regulation_id_lower == "3j1":
                score += 3.0

            if regulation_id_lower == "3j1a":
                score += 2.0

            if regulation_id_lower not in {
                "3j",
                "3j1",
                "3j1a"
            }:

                if (
                    "centre cap" in text_lower
                    or "center cap" in text_lower
                ):

                    score -= 1.0


        # -------------------------
        # General keyword boosts
        # -------------------------

        if (
            "+2" in query_lower
            and "+2" in text_lower
        ):

            score += 1.0


        if (
            "dnf" in query_lower
            and "dnf" in text_lower
        ):

            score += 1.0


        if (
            "penalty" in query_lower
            and "penalty" in text_lower
        ):

            score += 0.5


        if (
            "inspection" in query_lower
            and "inspection" in text_lower
        ):

            score += 0.5


        if (
            "timer" in query_lower
            and "timer" in text_lower
        ):

            score += 0.5


        if (
            "stopwatch" in query_lower
            and "stopwatch" in text_lower
        ):

            score += 0.5


        if (
            "delegate" in query_lower
            and "delegate" in text_lower
        ):

            score += 0.5


        scored.append({
            "id": chunk["id"],
            "article": article,
            "text": chunk["text"],
            "score": score
        })


    # -------------------------
    # Sort
    # -------------------------

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )


    # -------------------------
    # Return results
    # -------------------------

    return [
        {
            "id": result["id"],
            "text": result["text"]
        }
        for result in scored[:effective_top_k]
    ]


# -------------------------
# Command-line testing
# -------------------------

if __name__ == "__main__":

    while True:

        query = input(
            "Search > "
        )

        if not query.strip():
            continue

        results = search(
            query
        )

        print()

        for result in results:

            print(
                result["id"]
            )

            print(
                result["text"][:500]
            )

            print(
                "-" * 40
            )