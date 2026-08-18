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

    # Multi-Blind
    if any(term in query for term in (
        "multi-blind",
        "multi blind",
        "multiblind"
    )):
        return "H"

    # Blindfolded
    if any(term in query for term in (
        "blindfolded",
        "blindfold",
        "blind solve"
    )):
        return "B"

    # Fewest Moves
    if any(term in query for term in (
        "fewest moves",
        "fewest move",
        "fmc"
    )):
        return "E"

    # Dual Rounds
    if any(term in query for term in (
        "dual rounds",
        "dual round"
    )):
        return "9"

    # Head to Head
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

    target_article = detect_article(query)
    target_format = detect_format(query)


    # -------------------------
    # Intent detection
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

    asks_number = (
        not asks_change
        and any(term in query_lower for term in (
            "minimum number",
            "maximum number",
            "number of cubes",
            "how many cubes",
            "minimum",
            "maximum",
            "at least",
            "at most"
        ))
    )

    asks_disqualification = any(term in query_lower for term in (
        "disqualified",
        "disqualification",
        "dnf",
        "penalty"
    ))

    asks_equipment_problem = any(term in query_lower for term in (
        "falls off",
        "fell off",
        "fall off",
        "center cap",
        "centre cap",
        "cap falls",
        "cap fell",
        "damaged",
        "broken",
        "breaks",
        "piece falls",
        "piece fell"
    ))


    # -------------------------
    # Score regulations
    # -------------------------

    for chunk in chunks:

        text_lower = chunk["text"].lower()
        regulation_id = chunk["id"].lower()
        article = chunk.get("article")

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

            # H1 is the parent regulation establishing that
            # Multi-Blind follows blindfolded procedures.

            if regulation_id == "h1":

                score += 1.0


            # H regulations are substantially more relevant than
            # regulations from other articles for Multi-Blind queries.

            if article == "H":

                score += 1.0


            # Prefer text explicitly discussing Multi-Blind.

            if "multi-blind" in text_lower:

                score += 1.25

            elif "multi blind" in text_lower:

                score += 1.25


            # -------------------------
            # Number of puzzles
            # -------------------------

            if asks_number:

                # H1a contains the actual minimum requirement.

                if regulation_id == "h1a":

                    score += 6.0


                # H1a1 is about changing the submitted number,
                # not the minimum itself.

                if regulation_id == "h1a1":

                    score += 2.0


                # Penalise unrelated regulations that merely mention
                # a number of puzzles/cubes.

                if regulation_id not in {
                    "h1a",
                    "h1a1",
                    "h1a2",
                    "h1a3"
                }:

                    if any(term in text_lower for term in (
                        "at most",
                        "at least",
                        "number of",
                        "number"
                    )):

                        score -= 0.5


            # -------------------------
            # Changing submitted number
            # -------------------------

            if asks_change:

                if regulation_id == "h1a1":

                    score += 7.0

                if regulation_id == "h1a":

                    score += 2.0


                # H1a1 is specifically the rule being asked about.

                if regulation_id not in {
                    "h1",
                    "h1a",
                    "h1a1",
                    "h1a2"
                }:

                    score -= 0.5


            # -------------------------
            # Equipment problems / caps
            # -------------------------

            if asks_equipment_problem:

                # H1e is the relevant Multi-Blind disqualification
                # provision for individual-puzzle issues.

                if regulation_id == "h1e":

                    score += 7.0

                if regulation_id == "h1":

                    score += 1.0


                # Other blindfolded regulations should not dominate
                # simply because the question mentions blindfolding.

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
        # General keyword boosts
        # -------------------------

        if "+2" in query_lower and "+2" in text_lower:

            score += 1.0

        if "dnf" in query_lower and "dnf" in text_lower:

            score += 1.0

        if "penalty" in query_lower and "penalty" in text_lower:

            score += 0.5

        if "inspection" in query_lower and "inspection" in text_lower:

            score += 0.5

        if "timer" in query_lower and "timer" in text_lower:

            score += 0.5

        if "stopwatch" in query_lower and "stopwatch" in text_lower:

            score += 0.5

        if "delegate" in query_lower and "delegate" in text_lower:

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
            "id": r["id"],
            "text": r["text"]
        }
        for r in scored[:top_k]
    ]


# -------------------------
# Command-line testing
# -------------------------

if __name__ == "__main__":

    while True:

        q = input("Search > ")

        if not q.strip():

            continue

        results = search(q)

        print()

        for r in results:

            print(r["id"])
            print(r["text"][:500])
            print("-" * 40)