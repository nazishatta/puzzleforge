from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

# Optional env support
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None  # type: ignore


def _load_env() -> None:
    if load_dotenv is not None:
        try:
            load_dotenv()
        except Exception:
            pass


def generate_ai_puzzle(difficulty: str = "easy") -> Optional[Dict[str, Any]]:
    """
    Returns a puzzle dict or None if AI generation is unavailable/fails.
    This keeps the game stable for demos.
    """
    _load_env()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    if not api_key:
        return None

    # Try modern OpenAI SDK
    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None

    prompt = f"""
Generate ONE puzzle game entry as strict JSON only.

Requirements:
- difficulty: "{difficulty}"
- category: short category string
- question: clear puzzle question
- answer: short answer string
- hints: exactly 3 progressive hints (array of strings)
- explanation: concise explanation
- Keep it solvable and family-friendly.
- No markdown, no code fences, JSON only.

Expected JSON shape:
{{
  "category": "Logic",
  "question": "...",
  "answer": "...",
  "hints": ["...", "...", "..."],
  "explanation": "...",
  "difficulty": "{difficulty}"
}}
""".strip()

    try:
        client = OpenAI(api_key=api_key)

        # Works with recent SDKs
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You generate clean puzzle JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )
        content = resp.choices[0].message.content if resp.choices else None
        if not content:
            return None

        data = json.loads(content)
        if not isinstance(data, dict):
            return None

        # Basic validation
        required = ["category", "question", "answer", "hints", "explanation"]
        if not all(k in data for k in required):
            return None
        if not isinstance(data["hints"], list) or len(data["hints"]) < 1:
            return None

        data["difficulty"] = str(data.get("difficulty", difficulty))
        data["answer"] = str(data["answer"])
        data["hints"] = [str(h) for h in data["hints"]][:3]

        return data

    except Exception:
        return None