# parse regulations.txt into chunks.json for embedding and searching

import re
import json

with open("regulations.txt", "r", encoding="utf-8") as f:
    text = f.read()

pattern = r"([A-Z]\d*[a-z]?)\)\s+(.*?)(?=\n[A-Z]\d*[a-z]?\)|$)"

matches = re.findall(pattern, text, re.S)

chunks = []

for reg_id, reg_text in matches:

    article = reg_id[0]  # A, B, C, E, etc.

    chunks.append({
        "id": reg_id,
        "article": article,
        "text": reg_text.strip()
    })

with open("chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2)