from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import json
import tiktoken


# -------------------------
# Paths
# -------------------------

DATA_DIR = Path(__file__).parent / "data"

CHUNKS_FILE = DATA_DIR / "chunks.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.json"


# -------------------------
# Configuration
# -------------------------

MODEL = "text-embedding-3-small"

# Stay comfortably below the 8192-token limit.
MAX_TOKENS = 7000


# -------------------------
# OpenAI
# -------------------------

load_dotenv()

client = OpenAI()

encoding = tiktoken.get_encoding("cl100k_base")


# -------------------------
# Load chunks
# -------------------------

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)


# -------------------------
# Split oversized chunks
# -------------------------

embedding_chunks = []

for chunk in chunks:

    regulation_id = chunk["id"]
    tokens = encoding.encode(chunk["text"])

    if len(tokens) <= MAX_TOKENS:

        embedding_chunks.append({
            "id": regulation_id,
            "regulation": regulation_id,
            "text": chunk["text"]
        })

        continue

    print(
        f"Regulation {regulation_id} is "
        f"{len(tokens)} tokens long. Splitting..."
    )

    for start in range(0, len(tokens), MAX_TOKENS):

        part_tokens = tokens[start:start + MAX_TOKENS]
        part_text = encoding.decode(part_tokens)

        part_number = (start // MAX_TOKENS) + 1

        embedding_chunks.append({
            "id": f"{regulation_id}-{part_number}",
            "regulation": regulation_id,
            "text": part_text
        })


# -------------------------
# Generate embeddings
# -------------------------

texts = [
    chunk["text"]
    for chunk in embedding_chunks
]

print(
    f"Generating embeddings for "
    f"{len(embedding_chunks)} chunks..."
)

response = client.embeddings.create(
    model=MODEL,
    input=texts
)


# -------------------------
# Combine chunks + embeddings
# -------------------------

embedded = []

for chunk, emb in zip(
    embedding_chunks,
    response.data
):

    embedded.append({
        "id": chunk["id"],
        "regulation": chunk["regulation"],
        "text": chunk["text"],
        "embedding": emb.embedding
    })


# -------------------------
# Save embeddings
# -------------------------

with open(
    EMBEDDINGS_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        embedded,
        f
    )


print(
    f"Generated embeddings for "
    f"{len(embedded)} chunks."
)

print(
    f"Output written to {EMBEDDINGS_FILE}"
)