# `regs-helper`

A web application that answers questions about the WCA Regulations using semantic search and AI.

Frontend:
- SvelteKit
- Cloudflare Pages

Backend:
- FastAPI
- OpenAI API
- SQLite

Live site:
[https://regs.oweltonrosie.com](https://regs.oweltonrosie.com)
<br>
Dev site: [http://localhost:5713](http://localhost:5173)

## Requirements

Before running the app, you'll need:

- Python 3.13+
- Node.js
- npm
- [An OpenAI API key](https://platform.openai.com/signup/)

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

Populate `.env` with your OpenAI API key and admin password.

Start the app:

Backend:
```bash
uvicorn app:app --reload
```

Frontend (in a new terminal window):
```bash
cd frontend
npm run dev
```

Alternately, if your machine supports Unix-like commands, you can use the [dev script](https://github.com/OWelton-Rosie/regs-helper/blob/main/dev.sh):

```bash
./dev.sh
```

There's also a [build script](https://github.com/OWelton-Rosie/regs-helper/blob/main/build.sh) that simulates a production environment:
```bash
./build.sh
```

## Environment Variables

Backend (`.env`)

```env
OPENAI_API_KEY=your-api-key
ADMIN_PASSWORD=your-password
```

Frontend (`frontend/.env`)

```env
VITE_API_URL=http://127.0.0.1:8000
```

Copy the example files:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

## Project Structure

```text
├── ai/               Backend AI logic
├── frontend/         SvelteKit frontend
├── app.py            FastAPI application
├── requirements.txt
└── README.md
```


## Updating the app after regulation changes:
1. Copy and paste the latest relased version of the regs into `ai/data/regulations.txt`
2. Run:
```
python3 ai/parse_regs.py
```
3. Check `ai/data/chunks.json` and `ai/data/embeddings.json` and ask some questions to check that it worked
4. Commit and push to GH as normal
5. Let Render and CF pages do their thing


## Status updates
Check [https://api.regs.oweltonrosie.com/health](https://api.regs.oweltonrosie.com/health). You should see `{"status":"ok"}`. The local equivalent is [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

## Assorted notes
- The production backend is hosted on Render's free tier. After periods of inactivity, the backend may take up to a minute to wake up and answer the first request.
- If you ever see the following when doing local testing:
```bash
[Errno 48] Address already in use
```
Run:
```bash
lsof -i :8000
```

If it's uvicorn:
```bash
pkill -f uvicorn
```
