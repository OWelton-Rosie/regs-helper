# Parse regulations.txt into chunks.json for embedding and searching

import re
import json
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"

REGULATIONS_FILE = DATA_DIR / "regulations.txt"
CHUNKS_FILE = DATA_DIR / "chunks.json"


with open(REGULATIONS_FILE, "r", encoding="utf-8") as f:
    text = f.read()


pattern = r"([A-Z]\d*[a-z]?)\)\s+(.*?)(?=\n[A-Z]\d*[a-z]?\)|$)"

matches = re.findall(pattern, text, re.S)


chunks = []

for reg_id, reg_text in matches:

    article = reg_id[0]

    chunks.append({
        "id": reg_id,
        "article": article,
        "text": reg_text.strip()
    })


with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2)


print(f"Parsed {len(chunks)} regulations.")
print(f"Output written to {CHUNKS_FILE}")