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

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


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
        "head-to-head",
        "head to head round"
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

    for chunk in chunks:

        text_lower = chunk["text"].lower()

        score = cosine_similarity(
            q_emb,
            chunk["embedding"]
        )

        article = chunk.get("article")

        # -------------------------
        # Article relevance
        # -------------------------

        if target_article and article == target_article:
            score += 0.75

        # -------------------------
        # Explicit format relevance
        # -------------------------

        if target_format == "dual_rounds":

            if "dual rounds" in text_lower:
                score += 1.5

            elif "dual round" in text_lower:
                score += 1.25

        elif target_format == "head_to_head":

            if "head to head" in text_lower:
                score += 1.5

            elif "head-to-head" in text_lower:
                score += 1.5

        elif target_format == "fewest_moves":

            if "fewest moves" in text_lower:
                score += 1.0

        elif target_format == "multi_blind":

            if "multi-blind" in text_lower:
                score += 1.0

            elif "multi blind" in text_lower:
                score += 1.0

        # -------------------------
        # Exact keyword boosts
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