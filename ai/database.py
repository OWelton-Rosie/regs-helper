import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "questions.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def log_question(
    ip_address: str,
    question: str,
    answer: str
):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO questions
        (
            timestamp,
            ip_address,
            question,
            answer
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            ip_address,
            question,
            answer
        )
    )

    conn.commit()
    conn.close()


def get_recent_questions(limit=50):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            timestamp,
            ip_address,
            question,
            answer
        FROM questions
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    conn.close()

    return rows