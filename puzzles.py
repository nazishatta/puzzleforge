from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List

from llm_generator import generate_ai_puzzle


@dataclass
class Puzzle:
    category: str
    question: str
    answer: str
    hints: List[str]
    explanation: str
    difficulty: str = "easy"


class PuzzleProvider:
    def __init__(self, fallback_path: str = "fallback_puzzles.json") -> None:
        self.fallback_path = Path(fallback_path)
        self._fallback_puzzles = self._load_fallback_puzzles()

    def _load_fallback_puzzles(self) -> List[Puzzle]:
        if not self.fallback_path.exists():
            raise FileNotFoundError(f"Missing fallback puzzle file: {self.fallback_path.resolve()}")

        with self.fallback_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        puzzles: List[Puzzle] = []
        for item in raw:
            puzzles.append(
                Puzzle(
                    category=item["category"],
                    question=item["question"],
                    answer=str(item["answer"]),
                    hints=item["hints"],
                    explanation=item["explanation"],
                    difficulty=item.get("difficulty", "easy"),
                )
            )
        return puzzles

    def get_puzzle(
        self,
        difficulty: str = "easy",
        use_ai: bool = False,
        demo_mode: bool = False,
        round_index: int = 1,
    ) -> Puzzle:
        filtered = [p for p in self._fallback_puzzles if p.difficulty == difficulty]
        if not filtered:
            filtered = self._fallback_puzzles

        if demo_mode:
            idx = (round_index - 1) % len(filtered)
            return filtered[idx]

        if use_ai:
            ai_puzzle = generate_ai_puzzle(difficulty=difficulty)
            if ai_puzzle is not None:
                return Puzzle(
                    category=ai_puzzle["category"],
                    question=ai_puzzle["question"],
                    answer=str(ai_puzzle["answer"]),
                    hints=ai_puzzle["hints"],
                    explanation=ai_puzzle["explanation"],
                    difficulty=ai_puzzle.get("difficulty", difficulty),
                )

        return random.choice(filtered)