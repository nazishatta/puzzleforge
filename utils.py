from __future__ import annotations

import json
import os
import platform
import time
from pathlib import Path
from typing import Any, List

# Optional color support (safe fallback if colorama is missing)
try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init(autoreset=True)
    _COLOR_ENABLED = True
except Exception:
    _COLOR_ENABLED = False

    class _Dummy:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = ""
        RESET_ALL = ""

    Fore = Style = _Dummy()  # type: ignore


def clear_screen() -> None:
    command = "cls" if platform.system().lower().startswith("win") else "clear"
    os.system(command)


def normalize_answer(text: str) -> str:
    return " ".join(text.strip().lower().split())


def safe_int_input(prompt: str, default: int, min_value: int, max_value: int) -> int:
    raw = input(prompt).strip()
    if not raw:
        return default
    try:
        value = int(raw)
        if value < min_value or value > max_value:
            return default
        return value
    except ValueError:
        return default


def safe_choice_input(prompt: str, valid_choices: List[str], default: str) -> str:
    raw = input(prompt).strip().lower()
    if not raw:
        return default
    return raw if raw in valid_choices else default


def print_banner(title: str = "PuzzleForge") -> None:
    print(
        rf"""
██████╗ ██╗   ██╗███████╗███████╗██╗     ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
██╔══██╗██║   ██║╚══███╔╝╚══███╔╝██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
██████╔╝██║   ██║  ███╔╝   ███╔╝ ██║     █████╗  ██║   ██║██████╔╝██║  ███╗█████╗
██╔═══╝ ██║   ██║ ███╔╝   ███╔╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
██║     ╚██████╔╝███████╗███████╗███████╗███████╗╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝

                                  {title}
"""
    )


def divider(char: str = "-", width: int = 76) -> None:
    print(char * width)


def start_timer() -> float:
    return time.perf_counter()


def elapsed_seconds(start_time: float) -> int:
    return max(0, int(time.perf_counter() - start_time))


def load_json_file(path: str, default: Any) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json_file(path: str, data: Any) -> None:
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def wait() -> None:
    input("\nPress Enter to continue...")


# ---------- Color helpers ----------
def color_text(text: str, color: str) -> str:
    color_map = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "cyan": Fore.CYAN,
        "magenta": Fore.MAGENTA,
        "white": Fore.WHITE,
    }
    return f"{color_map.get(color.lower(), Fore.WHITE)}{text}{Style.RESET_ALL}"


def success_text(text: str) -> str:
    return color_text(text, "green")


def error_text(text: str) -> str:
    return color_text(text, "red")


def info_text(text: str) -> str:
    return color_text(text, "cyan")


def warning_text(text: str) -> str:
    return color_text(text, "yellow")


# ---------- Optional sound helpers ----------
def _bell() -> None:
    # terminal bell fallback (works in some terminals)
    print("\a", end="")


def play_success_sound() -> None:
    try:
        if platform.system().lower().startswith("win"):
            import winsound

            winsound.Beep(880, 140)
        else:
            _bell()
    except Exception:
        _bell()


def play_error_sound() -> None:
    try:
        if platform.system().lower().startswith("win"):
            import winsound

            winsound.Beep(240, 180)
        else:
            _bell()
    except Exception:
        _bell()