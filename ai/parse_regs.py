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

# Regulation IDs can look like:
#
# 1a)
# 1a1)
# 1c+)
# 1c++)
# 1h1)
# 1h1a)
# A1)
# A1a)
# B2a)
# H1a1)
# 11e+++++++)
#
# The ID always occurs at the beginning
# of a line.
#
# Structure:
#
#   optional uppercase article letter
#   one or more digits
#   optional lowercase letter
#   optional additional digits
#   zero or more +
#
# Examples:
#
#   1a
#   1a1
#   1h1a
#   A1
#   A1a
#   H1a1
#   11e+++++++
#
# The lookahead ensures that each regulation
# becomes its own chunk.

REGULATION_ID = (
    r"[A-Z]?"
    r"\d+"
    r"[a-z]?"
    r"\d*"
    r"\+*"
)

pattern = (
    rf"^({REGULATION_ID})\)\s+"
    rf"(.*?)(?=^{REGULATION_ID}\)\s+|\Z)"
)


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