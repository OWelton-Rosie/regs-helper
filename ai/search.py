from openai import OpenAI
from dotenv import load_dotenv
import json
import numpy as np

load_dotenv()
client = OpenAI()

from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"

with open(
    DATA_DIR / "embeddings.json",
    "r",
    encoding="utf-8"
) as f:
    chunks = json.load(f)


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def search(query, top_k=5):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )

    q_emb = response.data[0].embedding

    scored = []

    query_lower = query.lower()

    for chunk in chunks:

        text_lower = chunk["text"].lower()

        score = cosine_similarity(
            q_emb,
            chunk["embedding"]
        )

        # Keyword boosts to improve relevance for certain terms - this is a bit of a bitch but seems to work
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
            "text": chunk["text"],
            "score": score
        })

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return [
        {
            "id": r["id"],
            "text": r["text"]
        }
        for r in scored[:top_k]
    ]


if __name__ == "__main__":

    while True:

        q = input("Search > ")

        results = search(q)

        print()

        for r in results:

            print(r["id"])
            print(r["text"][:500])
            print("-" * 40)