from openai import OpenAI
from dotenv import load_dotenv

import json
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
# Article / format detection
# -------------------------

def detect_article(query):

    query = query.lower()

    if any(term in query for term in (
        "multi-blind",
        "multi blind",
        "multiblind"
    )):

        return "H"

    if any(term in query for term in (
        "blindfolded",
        "blindfold",
        "blind solve"
    )):

        return "B"

    if any(term in query for term in (
        "fewest moves",
        "fewest move",
        "fmc"
    )):

        return "E"

    if any(term in query for term in (
        "dual rounds",
        "dual round"
    )):

        return "9"

    if any(term in query for term in (
        "head to head",
        "head-to-head"
    )):

        return "I"

    return None


def detect_format(query):

    query = query.lower()

    if any(term in query for term in (
        "dual rounds",
        "dual round"
    )):

        return "dual_rounds"

    if any(term in query for term in (
        "head to head",
        "head-to-head"
    )):

        return "head_to_head"

    if any(term in query for term in (
        "fewest moves",
        "fewest move",
        "fmc"
    )):

        return "fewest_moves"

    if any(term in query for term in (
        "multi-blind",
        "multi blind",
        "multiblind"
    )):

        return "multi_blind"

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


    # -------------------------
    # Puzzle condition
    # -------------------------

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
    # Timer
    # -------------------------

    asks_timer = any(
        term in query_lower
        for term in (
            "timer",
            "stopwatch",
            "stackmat"
        )
    )


    # -------------------------
    # Timer reset
    # -------------------------

    asks_timer_reset = (
        asks_timer
        and any(
            term in query_lower
            for term in (
                "reset",
                "resets",
                "resetting",
                "restart",
                "restarted"
            )
        )
    )


    # -------------------------
    # Reasonable wear
    # -------------------------

    asks_reasonable_wear = (
        "reasonable wear" in query_lower
        or (
            "reasonable" in query_lower
            and "wear" in query_lower
        )
    )


    # -------------------------
    # Clock-specific wear
    # -------------------------

    asks_clock_wear = (
        "clock" in query_lower
        and (
            "wear" in query_lower
            or "loose pin" in query_lower
            or "loose pins" in query_lower
            or "pin" in query_lower
            or "pins" in query_lower
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
        "asks_timer": asks_timer,
        "asks_timer_reset": asks_timer_reset,
        "asks_reasonable_wear": asks_reasonable_wear,
        "asks_clock_wear": asks_clock_wear
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

    scored = []

    query_lower = query.lower()

    target_article = detect_article(
        query
    )

    target_format = detect_format(
        query
    )

    intents = detect_intents(
        query
    )

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

    asks_timer = intents["asks_timer"]

    asks_timer_reset = (
        intents["asks_timer_reset"]
    )

    asks_reasonable_wear = (
        intents["asks_reasonable_wear"]
    )

    asks_clock_wear = (
        intents["asks_clock_wear"]
    )


    # -------------------------
    # Score regulations
    # -------------------------

    for chunk in chunks:

        text_lower = chunk["text"].lower()

        regulation_id = (
            chunk["id"].lower()
        )

        article = chunk.get(
            "article"
        )

        score = cosine_similarity(
            q_emb,
            chunk["embedding"]
        )


        # -------------------------
        # Article relevance
        # -------------------------

        if target_article:

            if article == target_article:

                score += 1.0

            else:

                score -= 0.15


        # -------------------------
        # Explicit format relevance
        # -------------------------

        if target_format == "dual_rounds":

            if regulation_id == "9v":

                score += 3.0

            if regulation_id == "9v4":

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

            if regulation_id == "h1":

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

                if regulation_id == "h1a":

                    score += 6.0

                if regulation_id == "h1a1":

                    score += 2.0

                if regulation_id not in {
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

                if regulation_id == "h1a1":

                    score += 7.0

                if regulation_id == "h1a":

                    score += 2.0

                if regulation_id not in {
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

                if regulation_id == "h1e":

                    score += 7.0

                if regulation_id == "h1":

                    score += 1.0

                if article == "B":

                    score -= 1.0


            # -------------------------
            # Disqualification
            # -------------------------

            if asks_disqualification:

                if regulation_id == "h1e":

                    score += 5.0

                if "disqualification" in text_lower:

                    score += 0.75

                if "dnf" in text_lower:

                    score += 0.75


        # -------------------------
        # Puzzle legality / condition
        # -------------------------

        if asks_equipment_legality:

            if article == "3":

                score += 1.25

            if regulation_id == "3j":

                score += 4.0

            if regulation_id == "3j1":

                score += 3.0

            if regulation_id == "3j1a":

                score += 2.0

            if regulation_id not in {
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
        # Timer relevance
        # -------------------------

        if asks_timer:

            if "timer" in text_lower:

                score += 0.5

            if "stopwatch" in text_lower:

                score += 0.5


        # -------------------------
        # Timer reset
        # -------------------------

        if asks_timer_reset:

            if regulation_id == "b2a":

                score += 8.0

            if regulation_id == "a3b":

                score += 5.0

            if regulation_id == "a3c3+":

                score += 2.0

            if regulation_id == "a6f":

                score += 1.0

            # B2a is the primary regulation for
            # the judge resetting the timer.
            if regulation_id not in {
                "b2a",
                "a3b",
                "a3c3+",
                "a6f"
            }:

                if (
                    "reset" in text_lower
                    or "timer" in text_lower
                ):

                    score -= 0.5


        # -------------------------
        # Reasonable wear
        # -------------------------

        if asks_reasonable_wear:

            if regulation_id == "3j1":

                score += 6.0

            if regulation_id == "3j":

                score += 2.0

            # 3h5 is a Clock-specific rule about
            # loose pins. It should not pollute a
            # general reasonable-wear query.
            if regulation_id == "3h5":

                if asks_clock_wear:

                    score += 4.0

                else:

                    score -= 4.0


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
        for result in scored[:top_k]
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