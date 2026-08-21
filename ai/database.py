import os

from datetime import datetime

import psycopg

from dotenv import load_dotenv


# -------------------------
# Environment
# -------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set."
    )


# -------------------------
# Connection
# -------------------------

def get_connection():

    return psycopg.connect(
        DATABASE_URL
    )


# -------------------------
# Initialise database
# -------------------------

def initialize_database():

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id SERIAL PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    sources TEXT NOT NULL,
                    comment TEXT NOT NULL
                )
            """)


# -------------------------
# Questions
# -------------------------

def log_question(
    ip_address: str,
    question: str,
    answer: str
):

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO questions
                (
                    timestamp,
                    ip_address,
                    question,
                    answer
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    datetime.now().isoformat(),
                    ip_address,
                    question,
                    answer
                )
            )


def import_questions(rows):

    if not rows:
        return 0

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.executemany(
                """
                INSERT INTO questions
                (
                    timestamp,
                    ip_address,
                    question,
                    answer
                )
                VALUES (%s, %s, %s, %s)
                """,
                rows
            )

    return len(rows)


def get_recent_questions(limit=50):

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    timestamp,
                    ip_address,
                    question,
                    answer
                FROM questions
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,)
            )

            rows = cursor.fetchall()

    return rows


# -------------------------
# Reports
# -------------------------

def log_report(
    question: str,
    answer: str,
    sources: str,
    comment: str
):

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO reports
                (
                    timestamp,
                    question,
                    answer,
                    sources,
                    comment
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    datetime.now().isoformat(),
                    question,
                    answer,
                    sources,
                    comment
                )
            )


def import_reports(rows):

    if not rows:
        return 0

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.executemany(
                """
                INSERT INTO reports
                (
                    timestamp,
                    question,
                    answer,
                    sources,
                    comment
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                rows
            )

    return len(rows)


def get_recent_reports(limit=50):

    with get_connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    timestamp,
                    question,
                    answer,
                    sources,
                    comment
                FROM reports
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,)
            )

            rows = cursor.fetchall()

    return rows