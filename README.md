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
To verify that this works, check your console. The text `(venv)` should appear at the start of your shell, eg: `(venv) oscarwelton-rosie@Oscars-MacBook-Air regs-helper % `.

Run the app:
```bash
uvicorn app:app --reload
```

Then visit:
```bash
http://127.0.0.1:8000
```

Running the app requires you to have an OpenAI API key and an admin password to access the logs. [.env.example](https://github.com/OWelton-Rosie/regs-helper/blob/main/.env.example) contains the required fields. Create a file named `.env` and populate the values with your own ones. `OPENAI_API_KEY` must be a valid OpenAI API key but `ADMIN_PASSWORD` can be anything. 

You can sign up to the OpenAI API [here](https://openai.com/api/)