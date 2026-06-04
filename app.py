from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ai.ask import ask

app = FastAPI()

# Serve CSS, JS, images, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/legal.html")
async def legal(request: Request):
    return templates.TemplateResponse(
        "legal.html",
        {"request": request}
    )

@app.get("/about.html")
async def legal(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {"request": request}
    )


@app.get("/ask")
async def ask_question(question: str):

    return ask(question)