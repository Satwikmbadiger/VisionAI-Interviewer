from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt

from .groq_client import GroqLLM
from .models import Difficulty, QAItem
from .storage import Storage

logger = logging.getLogger("interview_bot.engine")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SessionEngine:
    def __init__(self, *, llm: GroqLLM, storage: Storage, console: Optional[Console] = None):
        self.llm = llm
        self.storage = storage
        self.console = console or Console()

    def run_new_session(
        self,
        *,
        topic: str | None,
        pdf_path: str | None,
        context_text: str | None,
        difficulty: Difficulty,
        num_questions: int,
        include_hints: bool,
    ) -> int:
        session_id = self.storage.create_session(
            topic=topic,
            pdf_path=pdf_path,
            difficulty=difficulty.value,
            model=self.llm._model,  # ok for reporting
            num_questions=num_questions,
            context_text=context_text,
            include_hints=include_hints,
            metadata={"version": "0.1.0"},
        )
        self._run_session_loop(
            session_id=session_id,
            topic=topic,
            context_text=context_text,
            difficulty=difficulty,
            num_questions=num_questions,
            include_hints=include_hints,
        )
        return session_id

    def resume_session(self, session_id: int) -> int:
        s = self.storage.get_session_row(session_id)
        if not s:
            raise KeyError(f"Unknown session_id={session_id}")
        items = self.storage.get_items(session_id)
        answered = len(items)
        if s.get("finished_at"):
            self.console.print("[yellow]Session is already finished. Export it or start a new one.[/yellow]")
            return session_id

        self._run_session_loop(
            session_id=session_id,
            topic=s.get("topic"),
            context_text=s.get("context_text"),
            difficulty=Difficulty(s["difficulty"]),
            num_questions=int(s["num_questions"]),
            include_hints=bool(int(s.get("include_hints", 0))),
            start_index=answered,
        )
        return session_id

    def _run_session_loop(
        self,
        *,
        session_id: int,
        topic: str | None,
        context_text: str | None,
        difficulty: Difficulty,
        num_questions: int,
        include_hints: bool,
        start_index: int = 0,
    ) -> None:
        self.console.print(f"[bold]Session {session_id}[/bold] starting. Type ':quit' to stop, ':hint' for a hint.")

        questions = self.llm.generate_questions(
            topic=topic,
            context_text=context_text,
            difficulty=difficulty,
            num_questions=num_questions,
            include_hints=include_hints,
        )

        for idx in range(start_index, len(questions)):
            q = questions[idx]
            self.console.print("")
            self.console.print(f"[cyan]Q{idx+1}/{num_questions}[/cyan] {q.question}")
            if include_hints and q.hint:
                self.console.print("[dim]Hint available: type :hint[/dim]")

            while True:
                ans = Prompt.ask("Your answer").strip()
                if ans.lower() in {":quit", "quit", "exit"}:
                    self.console.print("[yellow]Stopping session (not finished). You can resume later.[/yellow]")
                    return
                if ans.lower() == ":hint":
                    if q.hint:
                        self.console.print(f"[magenta]Hint:[/magenta] {q.hint}")
                    else:
                        self.console.print("[dim]No hint for this question.[/dim]")
                    continue
                if not ans:
                    self.console.print("[dim]Please enter an answer (or :quit).[/dim]")
                    continue
                break

            try:
                evaluation = self.llm.evaluate_answer(
                    question=q.question,
                    answer=ans,
                    context_text=context_text,
                    difficulty=q.difficulty,
                    rubric=q.rubric,
                )
            except Exception as e:
                logger.exception("Evaluation failed")
                self.console.print(f"[red]Evaluation failed:[/red] {e}")
                self.console.print("[yellow]Saving as incorrect with zero score.[/yellow]")
                from .models import Evaluation

                evaluation = Evaluation(
                    grade="incorrect",
                    score=0,
                    strengths=[],
                    gaps=["Evaluation failed; please check logs/config."],
                    suggested_answer="(unavailable)",
                    follow_up_question="(unavailable)",
                )

            item = QAItem(
                question_id=q.id,
                question=q.question,
                difficulty=q.difficulty,
                hint=q.hint,
                answer=ans,
                evaluation=evaluation,
                asked_at=_utc_now(),
            )
            self.storage.add_item(session_id, item)

            self.console.print(
                f"[green]Grade:[/green] {evaluation.grade}  "
                f"[green]Score:[/green] {evaluation.score}/100"
            )
            if evaluation.gaps:
                self.console.print("[yellow]Key gaps:[/yellow]")
                for g in evaluation.gaps[:3]:
                    self.console.print(f"- {g}")

        self.storage.finish_session(session_id)
        self.console.print("[bold green]Session finished![/bold green]")


