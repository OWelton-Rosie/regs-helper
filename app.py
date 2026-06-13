import os

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
    get_recent_questions
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
        "https://regs.oweltonrosie.com"
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


@app.get("/questions")
async def questions():

    rows = get_recent_questions()

    return {
        "questions": rows
    }