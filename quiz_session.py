import random
from dataclasses import dataclass, field
@dataclass
class QuizSession:
    user_id: int
    category: str
    questions: list[dict]
    current_index: int = 0
    correct: int = 0
    answers_given: list[bool] = field(default_factory=list)
    @classmethod
    def create(cls, user_id: int, category: str, questions: list[dict]) -> "QuizSession":
        shuffled = random.sample(questions, len(questions))
        return cls(user_id=user_id, category=category, questions=shuffled)
    @property
    def current_question(self) -> dict | None:
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None
    @property
    def total(self) -> int:
        return len(self.questions)
    @property
    def is_finished(self) -> bool:
        return self.current_index >= self.total
    @property
    def progress(self) -> str:
        return f"{self.current_index + 1} / {self.total}"
    def check_answer(self, chosen: str) -> bool:
        q = self.current_question
        if q is None:
            return False
        is_correct = chosen.strip() == q["answer"].strip()
        if is_correct:
            self.correct += 1
        self.answers_given.append(is_correct)
        self.current_index += 1
        return is_correct
    def result_emoji(self) -> str:
        pct = self.correct / self.total if self.total else 0
        if pct == 1.0:
            return "🏆"
        if pct >= 0.8:
            return "🥇"
        if pct >= 0.6:
            return "🥈"
        if pct >= 0.4:
            return "🥉"
        return "📚"
    def summary(self) -> str:
        pct = round(self.correct / self.total * 100) if self.total else 0
        emoji = self.result_emoji()
        return (
            f"{emoji} *Quiz Complete!*\n\n"
            f"Category: *{self.category}*\n"
            f"Score: *{self.correct} / {self.total}* ({pct}%)\n\n"
            + self._verdict(pct)
        )
    @staticmethod
    def _verdict(pct: int) -> str:
        if pct == 100:
            return "Perfect score! You're a genius! 🎉"
        if pct >= 80:
            return "Excellent work! Almost perfect! 👏"
        if pct >= 60:
            return "Good job! Keep practising! 💪"
        if pct >= 40:
            return "Not bad! Review the material and try again. 📖"
        return "Keep studying — you'll get there! 🌱"