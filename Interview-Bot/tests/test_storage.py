from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from interview_bot.models import Difficulty, Evaluation, QAItem
from interview_bot.storage import Storage


def test_storage_create_add_and_report(tmp_path: Path):
    db = tmp_path / "t.sqlite3"
    st = Storage(db)

    session_id = st.create_session(
        topic="Test topic",
        pdf_path=None,
        difficulty="easy",
        model="fake-model",
        num_questions=2,
        context_text="context",
        include_hints=True,
        metadata={"x": 1},
    )

    ev = Evaluation(
        grade="partial",
        score=55,
        strengths=["a"],
        gaps=["b"],
        suggested_answer="better",
        follow_up_question="next?",
    )
    item = QAItem(
        question_id="q1",
        question="What is X?",
        difficulty=Difficulty.easy,
        hint="hint",
        answer="ans",
        evaluation=ev,
        asked_at=datetime.now(timezone.utc),
    )
    st.add_item(session_id, item)
    st.finish_session(session_id)

    report = st.build_report(session_id)
    assert report.session_id == session_id
    assert report.num_answered == 1
    assert report.partial == 1
    assert report.correct == 0
    assert report.incorrect == 0


