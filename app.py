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
    get_recent_reports
)

from ai.rate_limit import is_rate_limited


load_dotenv()


ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


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
# Admin API
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