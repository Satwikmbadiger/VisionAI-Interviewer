from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import load_settings
from .engine import SessionEngine
from .groq_client import GroqLLM
from .logging_utils import setup_logging
from .models import Difficulty
from .pdf_utils import clip_text, extract_text_from_pdf, normalize_text
from .reporting import write_reports
from .storage import Storage

app = typer.Typer(add_completion=False, help="Interview Bot - Groq-powered interview/exam practice CLI.")
console = Console()


def _build_deps():
    settings = load_settings()
    setup_logging(settings.log_level)
    storage = Storage(settings.db_path)
    llm = GroqLLM(api_key=settings.groq_api_key, model=settings.model)
    engine = SessionEngine(llm=llm, storage=storage, console=console)
    return settings, storage, llm, engine


@app.command()
def new(
    topic: Optional[str] = typer.Option(None, help="Study topic (e.g., 'Operating systems')."),
    pdf: Optional[Path] = typer.Option(None, exists=True, dir_okay=False, help="Path to a PDF to ingest."),
    difficulty: Difficulty = typer.Option(Difficulty.medium, case_sensitive=False),
    num_questions: int = typer.Option(8, min=1, max=50),
    include_hints: bool = typer.Option(True, help="Allow ':hint' during questions."),
    max_context_chars: int = typer.Option(12000, help="Max characters of context to send to the model."),
):
    """
    Start a new practice session.
    """
    if not topic and not pdf:
        raise typer.BadParameter("Provide either --topic or --pdf.")
    if topic and pdf:
        console.print("[yellow]Both --topic and --pdf were provided. Using both for context.[/yellow]")

    settings, storage, _, engine = _build_deps()

    context_text: Optional[str] = None
    pdf_path_str: Optional[str] = None

    if pdf:
        pdf_path_str = str(pdf)
        raw = extract_text_from_pdf(pdf)
        raw = normalize_text(raw)
        context_text = clip_text(raw, max_context_chars)
        if not context_text:
            raise typer.BadParameter("Could not extract any text from the PDF.")

    session_id = engine.run_new_session(
        topic=topic,
        pdf_path=pdf_path_str,
        context_text=context_text,
        difficulty=difficulty,
        num_questions=num_questions,
        include_hints=include_hints,
    )
    console.print("")
    console.print(f"[bold]Session created:[/bold] {session_id}")
    console.print("Use 'interview-bot export --session-id ...' to generate reports.")


@app.command()
def resume(session_id: int = typer.Option(..., min=1, help="Session id to resume.")):
    """
    Resume an unfinished session.
    """
    _, _, _, engine = _build_deps()
    engine.resume_session(session_id)


@app.command()
def history(limit: int = typer.Option(20, min=1, max=200)):
    """
    List session history.
    """
    _, storage, _, _ = _build_deps()
    rows = storage.list_sessions(limit=limit)
    table = Table(title="Interview Bot Sessions")
    table.add_column("id", style="bold")
    table.add_column("topic")
    table.add_column("difficulty")
    table.add_column("answered/total")
    table.add_column("started")
    table.add_column("finished")

    for r in rows:
        table.add_row(
            str(r["id"]),
            (r.get("topic") or Path(r["pdf_path"]).name) if (r.get("topic") or r.get("pdf_path")) else "-",
            r["difficulty"],
            f'{r.get("answered", 0)}/{r.get("num_questions", "-")}',
            r["started_at"],
            r.get("finished_at") or "-",
        )
    console.print(table)


@app.command()
def export(
    session_id: int = typer.Option(..., min=1),
    out_dir: Path = typer.Option(Path("reports"), help="Output directory for report files."),
):
    """
    Export a session report to .txt and .json.
    """
    _, storage, _, _ = _build_deps()
    report = storage.build_report(session_id)
    txt_path, json_path = write_reports(report, out_dir)
    console.print(f"Wrote: {txt_path}")
    console.print(f"Wrote: {json_path}")


def main():
    app()


if __name__ == "__main__":
    main()


