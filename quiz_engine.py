"""Question generation and text-chunking utilities for the quiz app."""

from __future__ import annotations

import json
import re
import time
from math import ceil

from groq import Groq

MODEL = "llama-3.3-70b-versatile"
MAX_CHUNK_CHARS = 2_500


def prepare_text_chunks(text: str, question_count: int) -> list[str]:
    """Create evenly distributed source excerpts for varied quiz questions."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        raise ValueError("The uploaded file does not contain readable text.")

    if len(cleaned) <= MAX_CHUNK_CHARS:
        return [cleaned]

    # Prefer a distinct excerpt per question while keeping each excerpt large enough
    # to contain useful context.
    chunk_count = min(question_count, max(1, len(cleaned) // 800))
    window_size = min(MAX_CHUNK_CHARS, max(900, ceil(len(cleaned) / chunk_count)))
    last_start = max(0, len(cleaned) - window_size)

    if chunk_count == 1:
        starts = [0]
    else:
        starts = [round(index * last_start / (chunk_count - 1)) for index in range(chunk_count)]

    chunks = []
    for start in starts:
        end = min(len(cleaned), start + window_size)
        if start > 0:
            next_space = cleaned.find(" ", start)
            if next_space != -1 and next_space < start + 80:
                start = next_space + 1
        if end < len(cleaned):
            previous_space = cleaned.rfind(" ", start, end)
            if previous_space != -1:
                end = previous_space
        chunk = cleaned[start:end].strip()
        if chunk and chunk not in chunks:
            chunks.append(chunk)

    return chunks or [cleaned[:MAX_CHUNK_CHARS]]


def _validate_question(payload: dict) -> dict:
    options = payload.get("options")
    answer = str(payload.get("answer", "")).upper().strip()

    if not isinstance(payload.get("question"), str) or not payload["question"].strip():
        raise ValueError("The model returned a question without text.")
    if not isinstance(options, dict) or set(options) != {"A", "B", "C", "D"}:
        raise ValueError("The model did not return four labelled answer options.")
    if answer not in options:
        raise ValueError("The model returned an invalid correct-answer label.")

    return {
        "question": payload["question"].strip(),
        "options": {label: str(options[label]).strip() for label in ("A", "B", "C", "D")},
        "answer": answer,
    }


def generate_question(text: str, api_key: str, max_retries: int = 3) -> dict:
    """Generate one validated multiple-choice question from a source excerpt."""
    client = Groq(api_key=api_key.strip())
    messages = [
        {
            "role": "system",
            "content": (
                "You are an educational quiz assistant. Respond with one valid JSON object "
                "and no markdown or extra text."
            ),
        },
        {
            "role": "user",
            "content": (
                "Create one factual multiple-choice question based only on the source text. "
                "Return JSON with: question (string), options (an object with exactly A, B, C, "
                "and D keys), and answer (the correct option letter).\n\n"
                f"Source text:\n{text}"
            ),
        },
    ]

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                response_format={"type": "json_object"},
                messages=messages,
                timeout=30,
            )
            return _validate_question(json.loads(response.choices[0].message.content))
        except Exception as error:
            last_error = error
            if attempt < max_retries - 1:
                time.sleep(2**attempt)

    raise RuntimeError("Unable to generate this question. Please try again.") from last_error


def generate_quiz(text: str, question_count: int, api_key: str) -> list[dict]:
    """Generate a quiz from chunks spread throughout the uploaded document."""
    chunks = prepare_text_chunks(text, question_count)
    return [
        generate_question(chunks[index % len(chunks)], api_key)
        for index in range(question_count)
    ]
