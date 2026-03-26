from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


GradeLabel = Literal["correct", "partial", "incorrect"]


class GeneratedQuestion(BaseModel):
    id: str = Field(..., description="Stable question id within a session, e.g. q1")
    question: str
    difficulty: Difficulty
    hint: Optional[str] = None
    rubric: list[str] = Field(default_factory=list, description="What a good answer should include")


class Evaluation(BaseModel):
    grade: GradeLabel
    score: int = Field(..., ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    suggested_answer: str
    follow_up_question: str


class QAItem(BaseModel):
    question_id: str
    question: str
    difficulty: Difficulty
    hint: Optional[str] = None
    answer: str
    evaluation: Evaluation
    asked_at: datetime


class SessionReport(BaseModel):
    session_id: int
    topic: Optional[str] = None
    pdf_path: Optional[str] = None
    difficulty: Difficulty
    started_at: datetime
    finished_at: Optional[datetime] = None
    model: str
    num_questions: int
    num_answered: int
    correct: int
    partial: int
    incorrect: int
    items: list[QAItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


