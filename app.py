import os

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    Request,
    Form
)

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ai.ask import ask

from ai.database import (
    initialize_database,
    log_question,
    get_recent_questions
)

# NOTE:
# This file contains FastAPI routing and Jinja template configuration.
#
# If template rendering suddenly starts throwing bizarre errors,
# check Starlette and Jinja versions before changing any code.
#
# A Starlette/Jinja version mismatch previously caused template
# rendering to fail with obscure errors despite valid templates.

load_dotenv()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

app = FastAPI()

initialize_database()

# Serve CSS, JS and images
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/legal.html", response_class=HTMLResponse)
async def legal(request: Request):

    return templates.TemplateResponse(
        "legal.html",
        {"request": request}
    )


@app.get("/about.html", response_class=HTMLResponse)
async def about(request: Request):

    return templates.TemplateResponse(
        "about.html",
        {"request": request}
    )


# API endpoint used by frontend JavaScript
@app.get("/ask")
async def ask_question(question: str):

    result = ask(question)

    log_question(
        question,
        result["answer"]
    )

    return result


@app.get("/admin", response_class=HTMLResponse)
async def admin_login(request: Request):

    return templates.TemplateResponse(
        "admin_login.html",
        {
            "request": request
        }
    )


@app.post("/admin", response_class=HTMLResponse)
async def admin_questions(
    request: Request,
    password: str = Form(...)
):

    if password != ADMIN_PASSWORD:

        return templates.TemplateResponse(
            "admin_login.html",
            {
                "request": request,
                "error": "Incorrect password"
            }
        )

    questions = get_recent_questions()

    return templates.TemplateResponse(
        "questions.html",
        {
            "request": request,
            "questions": questions
        }
    )