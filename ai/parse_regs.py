import re
import json

from pathlib import Path


# -------------------------
# Paths
# -------------------------

DATA_DIR = Path(__file__).parent / "data"

REGULATIONS_FILE = DATA_DIR / "regulations.txt"
CHUNKS_FILE = DATA_DIR / "chunks.json"


# -------------------------
# Load regulations
# -------------------------

with open(
    REGULATIONS_FILE,
    "r",
    encoding="utf-8"
) as f:

    text = f.read()


# -------------------------
# Parse regulations
# -------------------------

# Regulation IDs look like:
#
# 1a)
# 1a1)
# 1c+)
# 1c++)
# A1)
# B2a)
# etc.
#
# The important part is that the ID occurs
# at the beginning of a line.

pattern = r"^([A-Z]?\d+[a-z]?\+*)\)\s+(.*?)(?=^[A-Z]?\d+[a-z]?\+*\)\s+|\Z)"

matches = re.findall(
    pattern,
    text,
    re.MULTILINE | re.DOTALL
)


# -------------------------
# Build chunks
# -------------------------

chunks = []

for reg_id, reg_text in matches:

    article_match = re.match(
        r"([A-Z]|\d+)",
        reg_id
    )

    article = (
        article_match.group(1)
        if article_match
        else ""
    )

    chunks.append({
        "id": reg_id,
        "article": article,
        "text": reg_text.strip()
    })


# -------------------------
# Save chunks
# -------------------------

with open(
    CHUNKS_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        chunks,
        f,
        indent=2,
        ensure_ascii=False
    )


print(
    f"Parsed {len(chunks)} regulations."
)

print(
    f"Output written to {CHUNKS_FILE}"
)