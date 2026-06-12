# `regs-helper`
This app runs on a Python backend and a SvelteKit frontend.

Clone the project and navigate to it:
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
To verify that this works, check your console. The text `(venv)` should appear at the start of your shell, eg: `(venv) oscarwelton-rosie@Oscars-MacBook-Air regs-helper % `.

Run the backend:
```bash
uvicorn app:app --reload
```

In a new terminal window (make sure you're cd'd to the `regs-helper` directory) get the SvelteKit frontend going:
```bash
cd frontend
```

```bash
npm install && npm run dev
```

To view the app, navigate to:
```bash
http://localhost:5173/
```


Running the app requires you to have an OpenAI API key and an admin password to access the logs. [.env.example](https://github.com/OWelton-Rosie/regs-helper/blob/main/.env.example) contains the required fields. Create a file named `.env` and populate the values with your own ones. `OPENAI_API_KEY` must be a valid OpenAI API key but `ADMIN_PASSWORD` can be anything. 

You can sign up to the OpenAI API [here](https://openai.com/api/).


## Updating the app after regulation changes:
- Copy and paste the latest relased version of the regs into `ai/data/regulations.txt`
- Run `python3 ai/parse_regs.py`
- Check `ai/data/chunks.json` and `ai/data/embeddings.json` to verify that it worked