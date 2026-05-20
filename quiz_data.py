import json
import os
import logging
logger = logging.getLogger(__name__)
QUESTIONS_FILE = "questions.json"
SCORES_FILE = "scores.json"
class QuizData:
    def __init__(self, questions_file: str = QUESTIONS_FILE, scores_file: str = SCORES_FILE):
        self.questions_file = questions_file
        self.scores_file = scores_file
        self._questions: dict = {}
        self._scores: dict = {}
        self._load_questions()
        self._load_scores()
    def _load_questions(self) -> None:
        try:
            with open(self.questions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._questions = data.get("categories", {})
            logger.info("Loaded %d categories from %s", len(self._questions), self.questions_file)
        except FileNotFoundError:
            logger.error("Questions file '%s' not found.", self.questions_file)
            self._questions = {}
        except json.JSONDecodeError as e:
            logger.error("Failed to parse questions file: %s", e)
            self._questions = {}
    def _save_questions(self) -> None:
        try:
            with open(self.questions_file, "w", encoding="utf-8") as f:
                json.dump({"categories": self._questions}, f, ensure_ascii=False, indent=2)
            logger.info("Saved %d categories to %s", len(self._questions), self.questions_file)
        except OSError as e:
            logger.error("Could not save questions: %s", e)
    def get_categories(self) -> list[str]:
        return sorted(self._questions.keys())
    def get_questions(self, category: str) -> list[dict]:
        return self._questions.get(category, [])
    def _load_scores(self) -> None:
        if not os.path.exists(self.scores_file):
            self._scores = {}
            self._save_scores()
            return
        try:
            with open(self.scores_file, "r", encoding="utf-8") as f:
                self._scores = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Could not load scores: %s", e)
            self._scores = {}
    def _save_scores(self) -> None:
        try:
            with open(self.scores_file, "w", encoding="utf-8") as f:
                json.dump(self._scores, f, indent=2, ensure_ascii=False)
        except OSError as e:
            logger.error("Could not save scores: %s", e)
    def update_score(self, user_id: int, username: str, correct: int, total: int) -> None:
        uid = str(user_id)
        record = self._scores.get(uid, {"username": username, "total_correct": 0, "total_played": 0, "games": 0})
        record["username"] = username
        record["total_correct"] += correct
        record["total_played"] += total
        record["games"] += 1
        self._scores[uid] = record
        self._save_scores()
    def get_user_score(self, user_id: int) -> dict | None:
        return self._scores.get(str(user_id))
    def get_leaderboard(self, top_n: int = 5) -> list[dict]:
        ranked = sorted(
            self._scores.values(),
            key=lambda r: r["total_correct"],
            reverse=True,
        )[:top_n]
        return [{"rank": i + 1, **r} for i, r in enumerate(ranked)]