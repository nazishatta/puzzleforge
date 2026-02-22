from __future__ import annotations

THEMES = {
    "classic": {
        "name": "Classic PuzzleForge",
        "intro": "Welcome to the puzzle arena.",
        "round_label": "Round",
        "hint_label": "Hint",
        "success_text": "Vault solved.",
        "fail_text": "Lock remains closed.",
    },
    "detective": {
        "name": "PuzzleForge: Detective Files",
        "intro": "You are solving evidence locks in a detective archive.",
        "round_label": "Case",
        "hint_label": "Clue",
        "success_text": "Case clue decrypted.",
        "fail_text": "The evidence stays sealed.",
    },
    "scifi": {
        "name": "PuzzleForge: Star Vault",
        "intro": "You are unlocking encrypted modules aboard a drifting station.",
        "round_label": "Module",
        "hint_label": "Signal",
        "success_text": "Module unlocked.",
        "fail_text": "System remains locked.",
    },
    "fantasy": {
        "name": "PuzzleForge: Arcane Trials",
        "intro": "You are solving enchanted locks in a forgotten tower.",
        "round_label": "Trial",
        "hint_label": "Rune Hint",
        "success_text": "Seal broken.",
        "fail_text": "The rune seal persists.",
    },
}

DEFAULT_THEME = "scifi"

MAX_ATTEMPTS = 3
LEADERBOARD_FILE = "leaderboard.json"