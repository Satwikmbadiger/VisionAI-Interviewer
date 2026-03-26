from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

from .models import QAItem, SessionReport


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _dt_to_str(dt: datetime) -> str:
    # ISO-8601 with timezone
    return dt.astimezone(timezone.utc).isoformat()


def _str_to_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  topic TEXT,
  pdf_path TEXT,
  difficulty TEXT NOT NULL,
  model TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  num_questions INTEGER NOT NULL,
  context_text TEXT,
  include_hints INTEGER NOT NULL DEFAULT 0,
  metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS qa_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  question_id TEXT NOT NULL,
  question TEXT NOT NULL,
  difficulty TEXT NOT NULL,
  hint TEXT,
  answer TEXT NOT NULL,
  evaluation_json TEXT NOT NULL,
  asked_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id)
);
"""


class Storage:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(SCHEMA_SQL)

    def create_session(
        self,
        *,
        topic: Optional[str],
        pdf_path: Optional[str],
        difficulty: str,
        model: str,
        num_questions: int,
        context_text: Optional[str],
        include_hints: bool,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO sessions(topic, pdf_path, difficulty, model, started_at, num_questions, context_text, include_hints, metadata_json)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    topic,
                    pdf_path,
                    difficulty,
                    model,
                    _dt_to_str(_utc_now()),
                    num_questions,
                    context_text,
                    1 if include_hints else 0,
                    json.dumps(metadata or {}),
                ),
            )
            return int(cur.lastrowid)

    def finish_session(self, session_id: int) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE sessions SET finished_at = ? WHERE id = ?",
                (_dt_to_str(_utc_now()), session_id),
            )

    def add_item(self, session_id: int, item: QAItem) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO qa_items(session_id, question_id, question, difficulty, hint, answer, evaluation_json, asked_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    item.question_id,
                    item.question,
                    item.difficulty.value,
                    item.hint,
                    item.answer,
                    item.evaluation.model_dump_json(),
                    _dt_to_str(item.asked_at),
                ),
            )

    def list_sessions(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT s.id, s.topic, s.pdf_path, s.difficulty, s.model, s.started_at, s.finished_at,
                       s.num_questions, COUNT(q.id) AS answered
                FROM sessions s
                LEFT JOIN qa_items q ON q.session_id = s.id
                GROUP BY s.id
                ORDER BY s.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_session_row(self, session_id: int) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            return dict(row) if row else None

    def get_items(self, session_id: int) -> list[QAItem]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM qa_items WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            ).fetchall()
        items: list[QAItem] = []
        for r in rows:
            data = dict(r)
            eval_obj = json.loads(data["evaluation_json"])
            items.append(
                QAItem.model_validate(
                    {
                        "question_id": data["question_id"],
                        "question": data["question"],
                        "difficulty": data["difficulty"],
                        "hint": data["hint"],
                        "answer": data["answer"],
                        "evaluation": eval_obj,
                        "asked_at": _str_to_dt(data["asked_at"]),
                    }
                )
            )
        return items

    def build_report(self, session_id: int) -> SessionReport:
        s = self.get_session_row(session_id)
        if not s:
            raise KeyError(f"Unknown session_id={session_id}")
        items = self.get_items(session_id)

        correct = sum(1 for it in items if it.evaluation.grade == "correct")
        partial = sum(1 for it in items if it.evaluation.grade == "partial")
        incorrect = sum(1 for it in items if it.evaluation.grade == "incorrect")

        metadata = json.loads(s["metadata_json"] or "{}")

        return SessionReport(
            session_id=session_id,
            topic=s.get("topic"),
            pdf_path=s.get("pdf_path"),
            difficulty=s["difficulty"],
            started_at=_str_to_dt(s["started_at"]),
            finished_at=_str_to_dt(s["finished_at"]) if s.get("finished_at") else None,
            model=s["model"],
            num_questions=int(s["num_questions"]),
            num_answered=len(items),
            correct=correct,
            partial=partial,
            incorrect=incorrect,
            items=items,
            metadata=metadata,
        )


