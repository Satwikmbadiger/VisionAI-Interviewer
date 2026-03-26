from __future__ import annotations

import json
import logging
from typing import Any

from groq import Groq

from .models import Difficulty, Evaluation, GeneratedQuestion

logger = logging.getLogger("interview_bot.groq")


class GroqLLM:
    def __init__(self, api_key: str, model: str):
        self._client = Groq(api_key=api_key)
        self._model = model

    def _chat(self, messages: list[dict[str, str]], max_tokens: int = 800, temperature: float = 0.3) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    @staticmethod
    def _extract_json(text: str) -> Any:
        """
        Best-effort extraction of JSON from a model response.
        We first try full-text JSON parse, then try to find the first {...} or [...] block.
        """
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            pass

        # Find first JSON object/array
        for opener, closer in (("{", "}"), ("[", "]")):
            start = text.find(opener)
            end = text.rfind(closer)
            if start != -1 and end != -1 and end > start:
                candidate = text[start : end + 1]
                return json.loads(candidate)
        raise ValueError("Could not parse JSON from model output.")

    def generate_questions(
        self,
        *,
        topic: str | None,
        context_text: str | None,
        difficulty: Difficulty,
        num_questions: int,
        include_hints: bool,
    ) -> list[GeneratedQuestion]:
        ctx = (context_text or "").strip()
        topic_part = f"Topic: {topic}" if topic else "Topic: (derived from provided context)"
        ctx_part = ctx if ctx else "(no additional context)"

        schema = {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "question": {"type": "string"},
                            "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                            "hint": {"type": ["string", "null"]},
                            "rubric": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["id", "question", "difficulty", "rubric"],
                    },
                }
            },
            "required": ["questions"],
        }

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an interview/exam coach. "
                    "You must output ONLY valid JSON, with no commentary, no markdown."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"{topic_part}\n\n"
                    f"Context (may be study notes or extracted PDF text):\n{ctx_part}\n\n"
                    f"Generate exactly {num_questions} questions.\n"
                    f"Overall difficulty: {difficulty.value}\n"
                    f"Include hints: {str(include_hints).lower()}\n\n"
                    f"JSON schema (informal): {json.dumps(schema)}\n\n"
                    "Rules:\n"
                    "- Provide diverse questions (concepts, edge cases, tradeoffs).\n"
                    "- Keep each question concise.\n"
                    "- Use ids q1, q2, ...\n"
                    "- If include_hints is false, set hint to null.\n"
                ),
            },
        ]

        raw = self._chat(messages, max_tokens=1200, temperature=0.5)
        data = self._extract_json(raw)
        items = data.get("questions", [])
        return [GeneratedQuestion.model_validate(x) for x in items]

    def evaluate_answer(
        self,
        *,
        question: str,
        answer: str,
        context_text: str | None,
        difficulty: Difficulty,
        rubric: list[str] | None = None,
    ) -> Evaluation:
        ctx = (context_text or "").strip()
        rb = rubric or []

        schema = {
            "type": "object",
            "properties": {
                "grade": {"type": "string", "enum": ["correct", "partial", "incorrect"]},
                "score": {"type": "integer", "minimum": 0, "maximum": 100},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "gaps": {"type": "array", "items": {"type": "string"}},
                "suggested_answer": {"type": "string"},
                "follow_up_question": {"type": "string"},
            },
            "required": ["grade", "score", "strengths", "gaps", "suggested_answer", "follow_up_question"],
        }

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a strict evaluator. "
                    "You must output ONLY valid JSON, with no commentary, no markdown. "
                    "Use the provided context as the primary reference. If context is missing, grade based on general correctness."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Difficulty: {difficulty.value}\n\n"
                    f"Question:\n{question}\n\n"
                    f"Candidate answer:\n{answer}\n\n"
                    f"Reference context:\n{ctx if ctx else '(none)'}\n\n"
                    f"Rubric bullets:\n- " + "\n- ".join(rb) + "\n\n"
                    f"Return JSON matching this schema: {json.dumps(schema)}\n\n"
                    "Scoring guidance:\n"
                    "- correct: score >= 80\n"
                    "- partial: score 40-79\n"
                    "- incorrect: score < 40\n"
                ),
            },
        ]

        raw = self._chat(messages, max_tokens=900, temperature=0.2)
        data = self._extract_json(raw)
        return Evaluation.model_validate(data)


