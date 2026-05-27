from openai import OpenAI
from dotenv import load_dotenv
import json
import numpy as np

load_dotenv()
client = OpenAI()

# Load embeddings database
with open("embeddings.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


# -----------------------------
# Detect likely regulation area
# -----------------------------
def guess_article(query: str):

    q = query.lower()

    # FMC
    if any(x in q for x in [
        "fmc",
        "fewest moves"
    ]):
        return ["C", "E"]

    # Blindfolded
    if any(x in q for x in [
        "blind",
        "blindfold",
        "bld"
    ]):
        return ["B"]

    # Head to head
    if any(x in q for x in [
        "head to head",
        "head-to-head"
    ]):
        return ["H"]

    # Standard speedsolving
    return ["A", "1", "2", "3", "4", "5", "7", "9"]


# -----------------------------
# Hybrid semantic + keyword search
# -----------------------------
def search(query, top_k=5):

    allowed_articles = guess_article(query)

    # Embed query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )

    q_emb = response.data[0].embedding

    scored = []

    query_lower = query.lower()

    for chunk in chunks:

        article = chunk.get("article")

        # Skip unrelated regulation groups
        if article not in allowed_articles:
            continue

        text_lower = chunk["text"].lower()

        # Base semantic score
        score = cosine_similarity(
            q_emb,
            chunk["embedding"]
        )

        # -----------------------------
        # Keyword / symbol boosts
        # -----------------------------

        if "+2" in query_lower and "+2" in text_lower:
            score += 0.5

        if "dnf" in query_lower and "dnf" in text_lower:
            score += 0.5

        if "penalty" in query_lower and "penalty" in text_lower:
            score += 0.2

        if "inspection" in query_lower and "inspection" in text_lower:
            score += 0.2

        if "timer" in query_lower and "timer" in text_lower:
            score += 0.2

        if "stopwatch" in query_lower and "stopwatch" in text_lower:
            score += 0.2

        if "delegate" in query_lower and "delegate" in text_lower:
            score += 0.2

        scored.append({
            "id": chunk["id"],
            "article": article,
            "text": chunk["text"],
            "score": score
        })

    # Sort highest score first
    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Return cleaned results
    return [
        {
            "id": r["id"],
            "article": r["article"],
            "text": r["text"]
        }
        for r in scored[:top_k]
    ]