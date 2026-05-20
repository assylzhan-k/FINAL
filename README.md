# 🎯 Quiz Bot — Telegram Quiz Game

A feature-rich Telegram bot that lets users play multiple-choice quizzes, track their scores, compete on a leaderboard, create their own quizzes, and play live online questions fetched from the internet in real time.

Username: @quizaza_bot
---

## Features

| Feature | Details |
|---|---|
| **Multiple-choice questions** | 4-option questions with instant feedback and explanation after each answer |
| **Local categories** | Python, Science, History, Math — stored in `questions.json` |
| **🌐 Online Quiz** | Live questions fetched from Open Trivia Database API — 10 categories |
| **Score tracking** | Per-user stats persisted to `scores.json` — survives bot restarts |
| **Leaderboard** | Top-5 players ranked by total correct answers |
| **Create your own quiz** | Step-by-step conversation to build and publish a custom quiz |
| **Two keyboard types** | `ReplyKeyboardMarkup` for main menu, `InlineKeyboardMarkup` for gameplay |
| **Robustness** | Exception handling on all file I/O and API calls — bot never crashes |

---

## Technologies Used

- **Python 3.11+**
- **python-telegram-bot 21.x** — async bot framework
- **aiohttp** — async HTTP client for external API requests
- **Open Trivia Database API** — free external API, no key required
- **JSON** — questions database and score persistence

---

## Project Structure

```
FINAL/
├── main.py             # Entry point — registers all handlers and starts the bot
├── handlers.py         # Command & callback handlers (start, quiz, online quiz, score, leaderboard)
├── create_handlers.py  # ConversationHandler for step-by-step quiz creation
├── trivia_api.py       # External API integration — fetches live questions from OpenTDB
├── keyboards.py        # ReplyKeyboard & InlineKeyboard builder functions
├── quiz_session.py     # Dataclass tracking one user's active quiz state
├── quiz_data.py        # Data layer — loads questions.json, saves scores.json
├── questions.json      # Local question bank, auto-updated when users create quizzes
├── scores.json         # Auto-generated user score records
├── requirements.txt
└── README.md
```

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/assylzhan-k/quiz-bot.git
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the prompts
3. Copy the token and set.


### 4. Run the bot
```bash
python main.py
```

---

## How to Play

1. Press **Start** or send `/start` — the main menu appears
2. Tap **🎯 Start Quiz** for local questions, or **🌐 Online Quiz** for live questions
3. Choose a category from the inline keyboard
4. Answer each question by tapping an option button
5. After each answer see ✅ Correct / ❌ Wrong with an explanation
6. After the last question see the score and choose to play again

---

## How to Create a Quiz

1. Tap **🆕 Create Quiz** from the main menu or send `/create`
2. Send a quiz title
3. For each question: send the question text, then options A / B / C / D one by one
4. Tap the correct answer button
5. Choose **➕ Add another question** or **✅ Finish quiz**
6. A quiz is saved instantly and appears in the category picker for everyone

---

## Online Quiz — External API

The **🌐 Online Quiz** feature fetches fresh questions from the [Open Trivia Database](https://opentdb.com) every time user plays.

Available online categories:
- 🔬 Science & Nature
- 💻 Computers
- 🎬 Film
- 🎵 Music
- ⚽ Sports
- 🌍 Geography
- 📜 History
- 🎨 Art
- 🐾 Animals
- 🚗 Vehicles

The bot sends an HTTP GET request using `aiohttp`, parses the JSON response, decodes HTML entities, shuffles the answer options, and feeds the questions into the same `QuizSession` class used for local quizzes.

---

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Show main menu with persistent keyboard |
| `/quiz` | Local category picker |
| `/onlinequiz` | Online category picker (live API questions) |
| `/create` | Build and publish your own quiz |
| `/score` | Your personal statistics |
| `/leaderboard` | Top-5 players |
| `/help` | Instructions and command list |

---

## OOP Concepts Used

| Concept | Where |
|---|---|
| **Classes & Objects** | `QuizData`, `QuizSession` |
| **Encapsulation** | Private `_load_questions`, `_save_scores`, `_save_questions` methods |
| **Dataclass** | `QuizSession` uses `@dataclass` decorator |
| **Properties** | `current_question`, `is_finished`, `progress` in `QuizSession` |
| **Class method (factory)** | `QuizSession.create()` shuffles and returns a new session |
| **Modular design** | Separated into 7 modules with clear responsibilities |

---

## Data Persistence

- `questions.json` — loaded on startup; updated in place when a user creates a new quiz
- `scores.json` — updated after every completed quiz; tracks `total_correct`, `total_played`, and `games` per user

---

## Adding Questions Manually

Edit `questions.json` directly:

```json
{
  "categories": {
    "My Category": [
      {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4",
        "explanation": "Basic arithmetic: 2 + 2 = 4."
      }
    ]
  }
}
```

---

## Team Members

| Name | Role |
|---|---|
| Kishibayeva Assylzhan | bot handlers, main entry point, API integration, README, quiz creation flow|
| Bazarbay Uldanay | report, keyboard builders, modified conversation handler, data layer |

---

## Screenshots

<img width="1150" height="925" alt="Screenshot 2026-05-20 at 14 39 25" src="https://github.com/user-attachments/assets/373aa368-8698-4573-befc-0baf1f13bba7" />

<img width="1150" height="514" alt="Screenshot 2026-05-20 at 14 40 47" src="https://github.com/user-attachments/assets/d041cb89-0310-411b-8a80-bbff72e5def3" />
