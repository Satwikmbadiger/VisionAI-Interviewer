from __future__ import annotations

from pathlib import Path
from rich.console import Console

from interview_bot.engine import SessionEngine
from interview_bot.models import Difficulty, Evaluation, GeneratedQuestion
from interview_bot.storage import Storage


class FakeLLM:
    def __init__(self):
        self._model = "fake"

    def generate_questions(self, *, topic, context_text, difficulty, num_questions, include_hints):
        return [
            GeneratedQuestion(
                id=f"q{i+1}",
                question=f"Question {i+1}?",
                difficulty=difficulty,
                hint="hint" if include_hints else None,
                rubric=["a", "b"],
            )
            for i in range(num_questions)
        ]

    def evaluate_answer(self, *, question, answer, context_text, difficulty, rubric=None):
        if "good" in answer.lower():
            return Evaluation(
                grade="correct",
                score=90,
                strengths=["ok"],
                gaps=[],
                suggested_answer="...",
                follow_up_question="...",
            )
        return Evaluation(
            grade="incorrect",
            score=10,
            strengths=[],
            gaps=["missing"],
            suggested_answer="...",
            follow_up_question="...",
        )


def test_engine_persists_answers(tmp_path: Path, monkeypatch):
    # Arrange storage + engine
    st = Storage(tmp_path / "db.sqlite3")
    out_fp = open(Path(tmp_path / "out.txt"), "w", encoding="utf-8")
    engine = SessionEngine(llm=FakeLLM(), storage=st, console=Console(file=out_fp))

    # Monkeypatch Prompt.ask to avoid interactive input.
    answers = iter(["good answer", "bad answer"])

    def fake_ask(*args, **kwargs):
        return next(answers)

    monkeypatch.setattr("interview_bot.engine.Prompt.ask", fake_ask)

    # Act
    session_id = engine.run_new_session(
        topic="t",
        pdf_path=None,
        context_text="ctx",
        difficulty=Difficulty.easy,
        num_questions=2,
        include_hints=False,
    )

    # Assert
    report = st.build_report(session_id)
    assert report.num_answered == 2
    assert report.correct == 1
    assert report.incorrect == 1

    out_fp.close()


