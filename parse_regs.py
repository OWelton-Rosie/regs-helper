import re
import json

with open("regulations.txt", "r", encoding="utf-8") as f:
    text = f.read()

pattern = r"([A-Z]?\d+[a-z]?)\)\s+(.*?)(?=\n[A-Z]?\d+[a-z]?\)|$)"

matches = re.findall(pattern, text, re.S)

chunks = []

for reg_id, reg_text in matches:
    chunks.append({
        "id": reg_id,
        "text": reg_text.strip()
    })

with open("chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2)