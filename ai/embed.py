from openai import OpenAI
from dotenv import load_dotenv

import json

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
# Load chunks
# -------------------------

with open(
    DATA_DIR / "chunks.json",
    "r",
    encoding="utf-8"
) as f:

    chunks = json.load(f)


# -------------------------
# Generate embeddings
# -------------------------

embedded = []

for index, chunk in enumerate(chunks, start=1):

    print(
        f"Embedding {index}/{len(chunks)}: "
        f"{chunk['id']}"
    )

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk["text"]
    )

    embedded.append({
        "id": chunk["id"],
        "article": chunk.get("article"),
        "text": chunk["text"],
        "embedding": response.data[0].embedding
    })


# -------------------------
# Save embeddings
# -------------------------

with open(
    DATA_DIR / "embeddings.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        embedded,
        f
    )


print()
print(
    f"Generated embeddings for {len(embedded)} regulations."
)
print(
    f"Output written to "
    f"{DATA_DIR / 'embeddings.json'}"
)