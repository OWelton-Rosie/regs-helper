# `regs-helper`

![Tests](https://github.com/OWelton-Rosie/regs-helper/actions/workflows/test.yml/badge.svg)

A web application that answers questions about the WCA Regulations using semantic search and AI.

**Frontend:**

* SvelteKit
* Cloudflare Pages

**Backend:**

* FastAPI
* OpenAI API
* Render Postgres

**Live site:**

https://regs.oweltonrosie.com

<br>

**Dev site:** http://localhost:5173

## Requirements

Before running the app, you'll need:

* Python 3.13+
* Node.js
* npm
* [An OpenAI API key](https://platform.openai.com/signup/)
* A Render Postgres database

## Quick Start

Clone the repository:

```bash
git clone https://github.com/OWelton-Rosie/regs-helper

cd regs-helper
```

Create a virtual environment:

```bash
python -m venv venv

source venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend

npm install

cd ..
```

Copy the example environment files:

```bash
cp .env.example .env

cp frontend/.env.example frontend/.env
```

Populate `.env` with your OpenAI API key, admin password, OpenAI model, and database URL.

Start the app:

**Backend:**

```bash
uvicorn app:app --reload
```

**Frontend** (in a new terminal window):

```bash
cd frontend

npm run dev
```

Alternatively, if your machine supports Unix-like commands, you can use the [dev script](https://github.com/OWelton-Rosie/regs-helper/blob/main/dev.sh):

```bash
./dev.sh
```

There's also a [build script](https://github.com/OWelton-Rosie/regs-helper/blob/main/build.sh) that simulates a production environment:

```bash
./build.sh
```

Both scripts will need to be made executable with:

```bash
chmod +x [script name]
```

## Environment Variables

### Backend (`.env`)

```env
OPENAI_API_KEY=Your_OpenAI_API_Key_Here
ADMIN_PASSWORD=Your_Admin_Password_Here
OPENAI_MODEL=Your_OpenAI_Model_Here
DATABASE_URL=Your_Database_URL_Here
```

* `OPENAI_API_KEY` — OpenAI API key used for AI responses and embeddings.
* `ADMIN_PASSWORD` — Password for the admin interface.
* `OPENAI_MODEL` — OpenAI model used to generate answers.
* `DATABASE_URL` — PostgreSQL database connection URL.

### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://127.0.0.1:8000
```

Copy the example files with:

```bash
cp .env.example .env

cp frontend/.env.example frontend/.env
```

## Project Structure

```text
├── ai/                  Backend AI logic
│   ├── data/            Regulations, chunks, and embeddings
│   ├── ask.py           Answer generation
│   ├── embed.py         Embedding generation
│   ├── parse_regs.py    Regulations parser
│   ├── search.py        Semantic search
│   ├── system_prompt.txt
│   └── test.py          Regression tests
├── frontend/            SvelteKit frontend
├── app.py               FastAPI application
├── requirements.txt
└── README.md
```

## Updating the app after regulation changes

When a new version of the WCA Regulations is released:

1. Copy and paste the latest released version of the regulations into `ai/data/regulations.txt`.

2. Regenerate the regulation chunks and embeddings:

```bash
python3 ai/parse_regs.py && python3 ai/embed.py
```

3. Check `ai/data/chunks.json` and `ai/data/embeddings.json`, then ask some questions to verify that the updated regulations were parsed and embedded correctly.

4. Run the regression tests:

```bash
python3 -m ai.test
```

5. Commit and push to GitHub as normal.

6. Let Render and Cloudflare Pages deploy the updated application.

## Status updates

Check the production backend health endpoint:

https://api.regs.oweltonrosie.com/health

You should see:

```json
{"status":"ok"}
```

The local equivalent is:

http://127.0.0.1:8000/health

## Assorted notes

* The production backend is hosted on Render's free tier. After periods of inactivity, the backend may take up to a minute to wake up and answer the first request.
* The production database is hosted using Render Postgres.
* If you ever see the following when doing local testing:

```text
[Errno 48] Address already in use
```

Run:

```bash
lsof -i :8000
```

If it's an existing uvicorn process:

```bash
pkill -f uvicorn
```

* I might add authentication through WCA OAuth at some point. No promises, though.
