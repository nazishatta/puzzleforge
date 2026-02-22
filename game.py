from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from puzzles import PuzzleProvider, Puzzle
from settings import THEMES, DEFAULT_THEME, MAX_ATTEMPTS, LEADERBOARD_FILE
from utils import (
    clear_screen,
    print_banner,
    normalize_answer,
    safe_int_input,
    safe_choice_input,
    divider,
    start_timer,
    elapsed_seconds,
    load_json_file,
    save_json_file,
    wait,
    success_text,
    error_text,
    info_text,
    warning_text,
    play_success_sound,
    play_error_sound,
)


@dataclass
class GameConfig:
    rounds: int = 5
    use_ai: bool = False
    difficulty: str = "easy"
    theme: str = DEFAULT_THEME
    timer_mode: bool = True
    player_name: str = "Player"
    demo_mode: bool = False
    sound_mode: bool = False


class PuzzleForgeGame:
    def __init__(self) -> None:
        self.provider = PuzzleProvider()
        self.config = GameConfig()
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.round_index = 0
        self.round_times: List[int] = []

    def run(self) -> None:
        while True:
            clear_screen()
            theme_pack = THEMES.get(self.config.theme, THEMES[DEFAULT_THEME])
            print_banner(theme_pack["name"])
            self._print_main_menu()
            choice = input("\nChoose an option: ").strip().lower()

            if choice == "1":
                self._setup_game()
                self._play_session()
                self._save_leaderboard_score()
                self._post_game_menu()
            elif choice == "2":
                self._how_to_play()
            elif choice == "3":
                self._show_leaderboard()
            elif choice == "4":
                self._about()
            elif choice in {"5", "q", "quit", "exit"}:
                print("\nThanks for playing PuzzleForge. Good luck at the hackathon! 🧩")
                break
            else:
                print(error_text("\nInvalid choice. Try again."))
                wait()

    def _print_main_menu(self) -> None:
        print(info_text("=== MAIN MENU ==="))
        print("1) Start Game")
        print("2) How to Play")
        print("3) Leaderboard")
        print("4) About")
        print("5) Quit")

    def _setup_game(self) -> None:
        clear_screen()
        print_banner("PuzzleForge Setup")
        print(info_text("=== GAME SETUP ==="))
        self.config.player_name = input("Player name (default Player): ").strip() or "Player"
        rounds = safe_int_input("How many rounds? (default 5): ", default=5, min_value=1, max_value=20)
        difficulty_choice = safe_choice_input(
            "Difficulty [easy/medium/hard] (default easy): ",
            ["easy", "medium", "hard"],
            "easy",
        )
        ai_choice = input("Use AI puzzle generation if available? [y/N]: ").strip().lower()
        use_ai = ai_choice in {"y", "yes"}

        theme_choice = safe_choice_input(
            "Theme [classic/detective/scifi/fantasy] (default scifi): ",
            ["classic", "detective", "scifi", "fantasy"],
            DEFAULT_THEME,
        )

        timer_choice = input("Timer mode ON? [Y/n]: ").strip().lower()
        timer_mode = timer_choice not in {"n", "no"}

        demo_choice = input("Demo mode (judge-safe predictable flow)? [y/N]: ").strip().lower()
        demo_mode = demo_choice in {"y", "yes"}

        sound_choice = input("Sound mode ON? [y/N]: ").strip().lower()
        sound_mode = sound_choice in {"y", "yes"}

        self.config = GameConfig(
            rounds=rounds,
            use_ai=use_ai,
            difficulty=difficulty_choice,
            theme=theme_choice,
            timer_mode=timer_mode,
            player_name=self.config.player_name,
            demo_mode=demo_mode,
            sound_mode=sound_mode,
        )

        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.round_index = 0
        self.round_times = []

        print(success_text("\nSetup complete."))
        wait()

    def _play_session(self) -> None:
        theme_pack = THEMES.get(self.config.theme, THEMES[DEFAULT_THEME])

        for i in range(1, self.config.rounds + 1):
            self.round_index = i
            clear_screen()
            print_banner(theme_pack["name"])
            print(info_text(theme_pack["intro"]))
            divider("=")
            label = theme_pack["round_label"]
            print(f"{label} {i}/{self.config.rounds} | Score: {self.score} | Streak: {self.streak}")
            print(
                f"Difficulty: {self.config.difficulty} | "
                f"AI Mode: {'ON' if self.config.use_ai else 'OFF'} | "
                f"Timer: {'ON' if self.config.timer_mode else 'OFF'} | "
                f"Sound: {'ON' if self.config.sound_mode else 'OFF'}"
            )
            print(f"Player: {self.config.player_name} | Demo Mode: {'ON' if self.config.demo_mode else 'OFF'}")
            divider()

            puzzle = self.provider.get_puzzle(
                difficulty=self.config.difficulty,
                use_ai=self.config.use_ai,
                demo_mode=self.config.demo_mode,
                round_index=i,
            )

            solved = self._play_single_puzzle(puzzle, theme_pack)
            if solved:
                self.streak += 1
                self.max_streak = max(self.max_streak, self.streak)
            else:
                self.streak = 0

            wait()

        self._show_results()

    def _play_single_puzzle(self, puzzle: Puzzle, theme_pack: Dict[str, str]) -> bool:
        hint_level = 0
        max_attempts = MAX_ATTEMPTS
        attempts_used = 0

        print(f"\nCategory: {puzzle.category}")
        print(f"Puzzle: {puzzle.question}")

        timer_start = start_timer() if self.config.timer_mode else None

        while attempts_used < max_attempts:
            print("\nOptions: [answer] Submit answer | [hint] Get hint | [skip] Skip puzzle")
            user_input = input("Your move: ").strip()

            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd == "hint":
                if hint_level < len(puzzle.hints):
                    hint_word = theme_pack["hint_label"]
                    print(info_text(f"\n{hint_word} {hint_level + 1}: {puzzle.hints[hint_level]}"))
                    hint_level += 1
                else:
                    print(warning_text("\nNo more hints available."))
                continue

            if cmd == "skip":
                round_time = elapsed_seconds(timer_start) if timer_start else 0
                self.round_times.append(round_time)
                if self.config.sound_mode:
                    play_error_sound()
                print(warning_text(f"\n⏭️  Skipped. {theme_pack['fail_text']}"))
                print(f"Answer: {puzzle.answer}")
                print(f"Explanation: {puzzle.explanation}")
                return False

            attempts_used += 1
            if normalize_answer(user_input) == normalize_answer(puzzle.answer):
                round_time = elapsed_seconds(timer_start) if timer_start else 0
                self.round_times.append(round_time)
                round_points = self._calculate_points(
                    attempts_used=attempts_used,
                    hints_used=hint_level,
                    seconds_used=round_time,
                )
                self.score += round_points
                if self.config.sound_mode:
                    play_success_sound()
                print(success_text(f"\n✅ Correct! {theme_pack['success_text']}"))
                print(success_text(f"+{round_points} points"))
                if self.config.timer_mode:
                    print(info_text(f"⏱️ Time: {round_time}s"))
                print(f"Explanation: {puzzle.explanation}")
                return True
            else:
                remaining = max_attempts - attempts_used
                if self.config.sound_mode:
                    play_error_sound()
                print(error_text("\n❌ Not correct."))
                if remaining > 0:
                    print(f"Attempts remaining: {remaining}")
                else:
                    round_time = elapsed_seconds(timer_start) if timer_start else 0
                    self.round_times.append(round_time)
                    print(error_text(f"\nNo attempts left. {theme_pack['fail_text']}"))
                    print(f"Answer: {puzzle.answer}")
                    print(f"Explanation: {puzzle.explanation}")
                    return False

        return False

    def _calculate_points(self, attempts_used: int, hints_used: int, seconds_used: int) -> int:
        base = 120
        attempt_penalty = (attempts_used - 1) * 20
        hint_penalty = hints_used * 15
        time_penalty = min(seconds_used // 10, 20) if self.config.timer_mode else 0
        streak_bonus = min(self.streak * 5, 25)
        return max(20, base - attempt_penalty - hint_penalty - time_penalty + streak_bonus)

    def _show_results(self) -> None:
        clear_screen()
        print_banner("PuzzleForge Results")
        print(info_text("=== FINAL RESULTS ==="))
        print(f"Player: {self.config.player_name}")
        print(f"Rounds played: {self.config.rounds}")
        print(f"Final score: {self.score}")
        print(f"Max streak: {self.max_streak}")

        if self.round_times:
            avg_time = sum(self.round_times) / len(self.round_times)
            print(f"Average round time: {avg_time:.1f}s")

        perfect = self.score >= self.config.rounds * 90
        strong = self.score >= self.config.rounds * 65

        if perfect:
            print(success_text("🏆 Outstanding run! Judge-ready performance."))
        elif strong:
            print(success_text("🔥 Strong game! Nice balance of skill and hints."))
        else:
            print(warning_text("🧠 Good run! Tune strategy and hints for a better score."))

    def _post_game_menu(self) -> None:
        while True:
            print(info_text("\n=== POST GAME ==="))
            print("1) Play Again (new setup)")
            print("2) Main Menu")
            choice = input("Choose: ").strip()
            if choice == "1":
                self._setup_game()
                self._play_session()
                self._save_leaderboard_score()
            elif choice == "2":
                break
            else:
                print(error_text("Invalid choice."))

    def _how_to_play(self) -> None:
        clear_screen()
        print_banner("How to Play")
        print(info_text("=== HOW TO PLAY ==="))
        print("- You receive one puzzle per round.")
        print("- Type your answer directly to submit.")
        print("- Type 'hint' to reveal progressive hints (costs points).")
        print("- Type 'skip' to move on.")
        print("- Score is based on accuracy, hints used, attempts, and time (if timer mode is ON).")
        print("- Theme mode changes the flavor text for a more immersive experience.")
        print("- Demo mode gives predictable puzzle order for judge-safe live demos.")
        wait()

    def _about(self) -> None:
        clear_screen()
        print_banner("About PuzzleForge")
        print(info_text("=== ABOUT ==="))
        print("PuzzleForge is a terminal-based puzzle game built for hackathon judging.")
        print("Design goals:")
        print("- Replayability")
        print("- Adaptive hints")
        print("- Reliable live demo")
        print("- Optional AI generation with safe local fallback")
        print("- Fast, colorful, polished terminal UX")
        wait()

    def _save_leaderboard_score(self) -> None:
        data = load_json_file(LEADERBOARD_FILE, default=[])
        if not isinstance(data, list):
            data = []

        record = {
            "player": self.config.player_name,
            "score": self.score,
            "rounds": self.config.rounds,
            "difficulty": self.config.difficulty,
            "theme": self.config.theme,
            "timer_mode": self.config.timer_mode,
            "demo_mode": self.config.demo_mode,
        }
        data.append(record)
        data = sorted(data, key=lambda x: x.get("score", 0), reverse=True)[:10]
        save_json_file(LEADERBOARD_FILE, data)

    def _show_leaderboard(self) -> None:
        clear_screen()
        print_banner("Leaderboard")
        print(info_text("=== TOP SCORES ==="))
        data = load_json_file(LEADERBOARD_FILE, default=[])
        if not data:
            print(warning_text("No scores yet. Play a game first!"))
            wait()
            return

        for idx, row in enumerate(data, start=1):
            print(
                f"{idx:>2}. {row.get('player','Player'):<12} "
                f"Score: {row.get('score',0):>4} | "
                f"{row.get('difficulty','easy'):<6} | "
                f"{row.get('theme','classic'):<9} | "
                f"Rounds: {row.get('rounds',0)}"
            )
        wait()