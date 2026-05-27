from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables from .env
load_dotenv()

# Create OpenAI client
client = OpenAI()

# Load regulation chunks
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Extract just the regulation text
texts = [chunk["text"] for chunk in chunks]

# Generate embeddings in ONE request
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

embedded_chunks = []

# Combine original chunk data with embeddings
for chunk, embedding_data in zip(chunks, response.data):

    embedded_chunks.append({
        "id": chunk["id"],
        "text": chunk["text"],
        "embedding": embedding_data.embedding
    })

# Save embeddings to file
with open("embeddings.json", "w", encoding="utf-8") as f:
    json.dump(embedded_chunks, f)

print("Embeddings generated successfully.")