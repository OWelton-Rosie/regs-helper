# `regs-helper`

Clone the project:
```bash
git clone https://github.com/OWelton-Rosie/regs-helper && cd regs-helper
```

Install the dependencies with pip:
```bash
pip install -r requirements.txt
```

Activate the virtual environment (if not already activated):

```bash
source venv/bin/activate
```

Run the app:
```bash
uvicorn app:app --reload
```

Then visit:
```bash
http://127.0.0.1:8000
```

Running the app requires you to have an OpenAI API key and an admin password to access the logs. .env.test contains an example of the syntax. Copy the file, rename it to `.env`, and populate the values with your own ones.