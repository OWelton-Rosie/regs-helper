from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ai.ask import ask

# This file contains FastAPI routing and Jinja template config
# If template rendering suddenly starts throwing bizarre errors, check Starlette and Jinja versions before changing any code.
# A Starlette/Jinja version mismatch previously caused template rendering to cack out

app = FastAPI()

# Serve shit in static dir
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

LOG_FILE = Path("logs/questions.log")


def log_question(question: str):
    """
    Log submitted questions for debugging and improvement.
    """

    timestamp = datetime.now().isoformat()

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"{timestamp} | {question}\n"
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

    log_question(question)

    return ask(question)