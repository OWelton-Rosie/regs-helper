import os
import json

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    Body
)

from fastapi.middleware.cors import CORSMiddleware

from ai.ask import ask

from ai.database import (
    initialize_database,
    log_question,
    get_recent_questions,
    log_report,
    get_recent_reports,
    import_questions,
    import_reports
)

from ai.rate_limit import is_rate_limited


# -------------------------
# Environment
# -------------------------

load_dotenv()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# -------------------------
# App
# -------------------------

app = FastAPI()

initialize_database()


# -------------------------
# CORS
# -------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://regs.oweltonrosie.com",
        "https://api.regs.oweltonrosie.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Main API
# -------------------------

@app.get("/ask")
async def ask_question(
    request: Request,
    question: str
):

    ip = request.client.host

    if is_rate_limited(ip):

        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

    result = ask(question)

    log_question(
        ip,
        question,
        result["answer"]
    )

    return result


# -------------------------
# Health
# -------------------------

@app.get("/health")
async def health():

    return {
        "status": "ok"
    }


# -------------------------
# Reports
# -------------------------

@app.post("/report")
async def report(
    data: dict = Body(...)
):

    question = data.get("question")
    answer = data.get("answer")
    sources = data.get("sources")
    comment = data.get("comment")

    if not question or not answer or not comment:

        raise HTTPException(
            status_code=400,
            detail="Missing required fields"
        )

    log_report(
        question,
        answer,
        json.dumps(sources or []),
        comment
    )

    return {
        "success": True
    }


# -------------------------
# Admin authentication
# -------------------------

@app.post("/login")
async def login(
    data: dict = Body(...)
):

    password = data.get("password")

    if password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    return {
        "success": True
    }


# -------------------------
# Admin questions
# -------------------------

@app.post("/questions")
async def questions(
    data: dict = Body(...)
):

    password = data.get("password")

    if password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    return {
        "questions": get_recent_questions()
    }


# -------------------------
# Admin reports
# -------------------------

@app.post("/reports")
async def reports(
    data: dict = Body(...)
):

    password = data.get("password")

    if password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    return {
        "reports": get_recent_reports()
    }


# -------------------------
# Import logs
# -------------------------

@app.post("/import-logs")
async def import_logs(
    data: dict = Body(...)
):

    password = data.get("password")
    log_type = data.get("type")
    rows = data.get("rows")


    # -------------------------
    # Authentication
    # -------------------------

    if password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )


    # -------------------------
    # Validate request
    # -------------------------

    if log_type not in (
        "questions",
        "reports"
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid log type"
        )

    if not isinstance(rows, list):

        raise HTTPException(
            status_code=400,
            detail="Invalid rows"
        )


    # -------------------------
    # Validate rows
    # -------------------------

    expected_columns = (
        4
        if log_type == "questions"
        else 5
    )

    valid_rows = []


    for row in rows:

        if not isinstance(row, list):

            raise HTTPException(
                status_code=400,
                detail="Invalid CSV row"
            )

        if len(row) != expected_columns:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid questions CSV"
                    if log_type == "questions"
                    else "Invalid reports CSV"
                )
            )

        # Ignore incomplete rows.
        if log_type == "questions":

            (
                timestamp,
                ip_address,
                question,
                answer
            ) = row

            if not question or not answer:
                continue

        else:

            (
                timestamp,
                question,
                answer,
                sources,
                comment
            ) = row

            if (
                not question
                or not answer
                or not comment
            ):
                continue

        valid_rows.append(row)


    # -------------------------
    # Import
    # -------------------------

    try:

        if log_type == "questions":

            imported = import_questions(
                valid_rows
            )

        else:

            imported = import_reports(
                valid_rows
            )


    except Exception as error:

        print(
            "Failed to import logs:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to import logs"
        )


    # -------------------------
    # Response
    # -------------------------

    return {
        "success": True,
        "imported": imported,
        "type": log_type
    }