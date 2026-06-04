from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ask import ask

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/ask")
async def ask_question(question: str):

    result = ask(question)

    return result