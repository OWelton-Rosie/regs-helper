from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [c["text"] for c in chunks]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

embedded = []

for chunk, emb in zip(chunks, response.data):
    embedded.append({
        "id": chunk["id"],
        "text": chunk["text"],
        "embedding": emb.embedding
    })

with open("embeddings.json", "w", encoding="utf-8") as f:
    json.dump(embedded, f)

print("Embeddings generated successfully.")