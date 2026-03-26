import os
import json
import uuid
import tempfile
import sys

import ollama
import pdfplumber
from docx import Document
from flask import current_app

from database import db
from models import InterviewSession


# ─── Text extraction ──────────────────────────────────────────────────────────

def extract_text(file_storage) -> str:
    filename = file_storage.filename.lower()
    suffix = os.path.splitext(filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file_storage.save(tmp.name)
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            return _extract_pdf(tmp_path)
        elif suffix in (".docx", ".doc"):
            return _extract_docx(tmp_path)
        elif suffix == ".txt":
            with open(tmp_path, "r", errors="ignore") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    finally:
        os.unlink(tmp_path)


def _extract_pdf(path: str) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)


def _extract_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


# ─── Prompt builder ───────────────────────────────────────────────────────────

def build_prompt(resume_text: str, jd_text: str, settings: dict) -> str:
    parts = []

    if resume_text:
        parts.append(f"<resume>\n{resume_text}\n</resume>")
    if jd_text:
        parts.append(f"<job_description>\n{jd_text}\n</job_description>")

    focus_map = {
        "technical":     "Focus heavily on technical skills and domain knowledge.",
        "behavioral":    "Focus on STAR-format behavioral questions.",
        "balanced":      "Use an even mix of technical and behavioral questions.",
        "communication": "Focus on communication, presentation, and soft skills.",
    }
    difficulty_map = {
        "easy":   "Entry-level; keep questions straightforward.",
        "medium": "Mid-level; assume 2-4 years of experience.",
        "hard":   "Senior-level; expect deep, nuanced answers.",
        "expert": "Leadership/Staff level; include system design and strategy.",
    }

    instructions = f"""
        You are an expert technical interviewer.

        Generate exactly {settings.get('questionCount', 5)} interview questions based on the documents above.

        Rules:
        - Difficulty: {difficulty_map.get(settings.get('difficulty', 'medium'), '')}
        - {focus_map.get(settings.get('focusArea', 'balanced'), '')}
        - Each question must be specific to the candidate's background and/or the role.
        - You MUST return a valid JSON object. No explanation, no markdown, no conversational text.

        Return EXACTLY this JSON format:
        {{
        "questions": [
            {{
            "id": 1,
            "question": "...",
            "type": "technical | behavioral | situational",
            "difficulty": "easy | medium | hard",
            "hint": "What a strong answer should cover"
            }}
        ]
        }}
        """.strip()

    return "\n\n".join(parts) + "\n\n" + instructions




# ─── Ollama call ──────────────────────────────────────────────────────────────

def _call_ollama(prompt: str) -> list:
    model = current_app.config["OLLAMA_MODEL"]

    print(f"\n[⏳] Asking Ollama ({model}) to generate questions...\n")
    print("┌" + "─" * 78)

    response_stream = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        format="json",  # 👈 THIS IS THE MAGIC BULLET
        options={
            "temperature": current_app.config["OLLAMA_TEMPERATURE"],
            "num_predict": current_app.config["OLLAMA_NUM_PREDICT"],
        },
        stream=True
    )

    raw_output = ""
    
    for chunk in response_stream:
        content = chunk["message"]["content"]
        import sys
        sys.stdout.write(content)
        sys.stdout.flush()
        raw_output += content

    print("\n└" + "─" * 78 + "\n")

    # Because we used format="json", we can just load it directly!
    try:
        parsed_data = json.loads(raw_output.strip())
        
        # Extract our array from the JSON object
        questions_array = parsed_data.get("questions", [])
        
        if not questions_array:
            raise ValueError("JSON was valid, but the 'questions' array was empty.")
            
        return questions_array
        
    except json.JSONDecodeError as e:
        print(f"\n[❌] CRITICAL ERROR: Ollama JSON mode failed to produce valid JSON. Raw output:\n{raw_output}")
        raise ValueError(f"Ollama output was not valid JSON: {str(e)}")


# ─── Logic functions (called by routes.py) ────────────────────────────────────

def generate_questions_logic(raw_settings: str, document_choice: str, files: dict):
    """
    raw_settings    : request.form.get("settings", "{}")
    document_choice : request.form.get("document_choice", "both")
    files           : request.files  (the full ImmutableMultiDict)
    """
    try:
        settings = json.loads(raw_settings)

        resume_text, jd_text = "", ""

        if document_choice in ("resume", "both"):
            resume_file = files.get("resume")
            if not resume_file:
                return {"error": "Resume file is missing"}, 400
            resume_text = extract_text(resume_file)
            print("\n" + "─" * 60)
            print(f"  📄 File 1: {resume_file.filename}")
            print("─" * 60)
            print(resume_text)
            print("─" * 60 + "\n")

        if document_choice in ("jd", "both"):
            jd_file = files.get("jd")
            if not jd_file:
                return {"error": "Job description file is missing"}, 400
            jd_text = extract_text(jd_file)
            print("\n" + "─" * 60)
            print(f"  📄 File 2: {jd_file.filename}")
            print("─" * 60)
            print(jd_text)
            print("─" * 60 + "\n")

        prompt    = build_prompt(resume_text, jd_text, settings)
        questions = _call_ollama(prompt)

        print("\n" + "─" * 60)
        print(f"  Generated {len(questions)} Questions")
        print("─" * 60)
        for q in questions:
            print(f"\n  [{q.get('type','').upper()}] Q{q.get('id')}: {q.get('question')}")
            print(f"  Difficulty : {q.get('difficulty')}")
            print(f"  Hint       : {q.get('hint')}")
        print("\n" + "─" * 60 + "\n")

        session = InterviewSession(
            id               = str(uuid.uuid4()),
            document_choice  = document_choice,
            settings         = settings,
            questions        = questions,
        )
        db.session.add(session)
        db.session.commit()

        return session.to_dict(), 201
    except json.JSONDecodeError as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Model returned invalid JSON: {e}"}, 500
    except Exception as e:
        import traceback
        traceback.print_exc() # <--- This prints the red error trace to your terminal
        return {"error": str(e)}, 500


def get_session_logic(session_id: str):
    session = InterviewSession.query.get(session_id)
    if not session:
        return {"error": "Session not found"}, 404
    return session.to_dict(), 200


def ollama_health_logic():
    try:
        model  = current_app.config["OLLAMA_MODEL"]
        models = ollama.list()
        names  = [m["model"] for m in models.get("models", [])]
        ready  = model in names
        return {
            "status":           "ok" if ready else "model_not_pulled",
            "model":            model,
            "available_models": names,
            "hint": None if ready else f"Run: ollama pull {model}",
        }, 200
    except Exception as e:
        return {"status": "ollama_not_running", "error": str(e)}, 503