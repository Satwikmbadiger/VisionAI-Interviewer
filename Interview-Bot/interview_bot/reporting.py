from __future__ import annotations

import json
from pathlib import Path

from .models import SessionReport


def render_report_txt(report: SessionReport) -> str:
    lines: list[str] = []
    lines.append(f"Interview Bot - Session Report (id={report.session_id})")
    lines.append("")
    lines.append(f"Topic: {report.topic or '-'}")
    lines.append(f"PDF: {report.pdf_path or '-'}")
    lines.append(f"Difficulty: {report.difficulty.value}")
    lines.append(f"Model: {report.model}")
    lines.append(f"Started: {report.started_at.isoformat()}")
    lines.append(f"Finished: {report.finished_at.isoformat() if report.finished_at else '-'}")
    lines.append("")
    lines.append(
        f"Answered {report.num_answered}/{report.num_questions} | "
        f"correct={report.correct} partial={report.partial} incorrect={report.incorrect}"
    )
    lines.append("")

    for i, item in enumerate(report.items, start=1):
        lines.append(f"--- Q{i} ({item.difficulty.value}, {item.question_id}) ---")
        lines.append(item.question.strip())
        if item.hint:
            lines.append(f"Hint: {item.hint.strip()}")
        lines.append("")
        lines.append("Your answer:")
        lines.append(item.answer.strip())
        lines.append("")
        lines.append(f"Grade: {item.evaluation.grade} | Score: {item.evaluation.score}/100")
        if item.evaluation.strengths:
            lines.append("Strengths:")
            for s in item.evaluation.strengths:
                lines.append(f"- {s}")
        if item.evaluation.gaps:
            lines.append("Gaps:")
            for g in item.evaluation.gaps:
                lines.append(f"- {g}")
        lines.append("Suggested answer:")
        lines.append(item.evaluation.suggested_answer.strip())
        lines.append("Follow-up question:")
        lines.append(item.evaluation.follow_up_question.strip())
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_reports(report: SessionReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / f"session_{report.session_id}.txt"
    json_path = out_dir / f"session_{report.session_id}.json"

    txt_path.write_text(render_report_txt(report), encoding="utf-8")
    json_path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    return txt_path, json_path


