from openai import OpenAI
import json
import numpy as np
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Load embeddings database
with open("embeddings.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search(query, top_k=5):

    # 1. Embed the query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )

    query_embedding = response.data[0].embedding

    # 2. Score all chunks
    scored = []

    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk["embedding"])

        scored.append({
            "score": score,
            "id": chunk["id"],
            "text": chunk["text"]
        })

    # 3. Sort by best match
    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:top_k]


# Quick test (this is just for now)
if __name__ == "__main__":
    results = search("Can I bring my own timer?")
    for r in results:
        print(r["score"], r["id"])
        print(r["text"])
        print("-" * 40)