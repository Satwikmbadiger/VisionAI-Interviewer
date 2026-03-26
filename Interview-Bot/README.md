## Interview Bot (CLI)

`interview-bot` is a Python CLI application to help you prepare for exams/interviews. It can:

- **Use a topic or a PDF** as study material (extracts text from PDF)
- **Generate questions** with the Groq API (official Python SDK)
- **Evaluate your answers**, give feedback, and score results
- **Track** correct / partial / incorrect answers
- **Save sessions** to SQLite (history + resume)
- **Export reports** to `.txt` and `.json`

### Setup

1) Create an environment and install:

```bash
cd Interview-Bot
python -m venv .venv
. .venv/Scripts/activate
pip install -e ".[dev]"
```

2) Set your Groq key:

- **Option A (recommended)**: create `.env` with `GROQ_API_KEY=...`
- **Option B**: set an environment variable `GROQ_API_KEY`

### Usage

Start a new session:

```bash
interview-bot new --topic "Operating systems" --difficulty medium --num-questions 8
```

Or use a PDF:

```bash
interview-bot new --pdf "C:\path\to\notes.pdf" --difficulty hard --num-questions 10
```

Resume a prior session:

```bash
interview-bot resume --session-id 3
```

List history:

```bash
interview-bot history
```

Export reports for a session:

```bash
interview-bot export --session-id 3 --out-dir reports
```

### Tests

```bash
pytest
```


