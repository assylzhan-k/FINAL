import logging
from telegram import Update
from telegram.ext import ContextTypes
from quiz_data import QuizData
from quiz_session import QuizSession
from keyboards import (
    main_menu_keyboard,
    category_keyboard,
    online_category_keyboard,
    answer_keyboard,
    next_question_keyboard,
    play_again_keyboard,
    OPTION_LABELS,
)
from trivia_api import fetch_questions, get_online_category_names

logger = logging.getLogger(__name__)
quiz_data = QuizData()

def _get_session(context: ContextTypes.DEFAULT_TYPE) -> QuizSession | None:
    return context.user_data.get("session")

def _set_session(context: ContextTypes.DEFAULT_TYPE, session: QuizSession) -> None:
    context.user_data["session"] = session

def _clear_session(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("session", None)

def _username(update: Update) -> str:
    user = update.effective_user
    return user.first_name or user.username or str(user.id)

async def _send_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = _get_session(context)
    if session is None or session.is_finished:
        return
    q = session.current_question
    options = q["options"]
    numbered_opts = "\n".join(f"  {lbl}. {opt}" for lbl, opt in zip(OPTION_LABELS, options))
    text = (
        f"*Question {session.progress}* — _{session.category}_\n\n"
        f"❓ {q['question']}\n\n"
        f"{numbered_opts}"
    )
    if update.callback_query:
        await update.callback_query.message.reply_text(
            text, parse_mode="Markdown", reply_markup=answer_keyboard(options)
        )
    else:
        await update.message.reply_text(
            text, parse_mode="Markdown", reply_markup=answer_keyboard(options)
        )
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = _username(update)
    await update.message.reply_text(
        f"👋 Welcome to *Quiz Bot*, {name}!\n\n"
        "Test your knowledge with local *or* live online questions.\n\n"
        "💡 You can also build your own quiz with /create!\n\n"
        "Use the menu below to get started 👇",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "📖 *How to Play*\n\n"
        "1. Tap *🎯 Start Quiz* for local questions.\n"
        "2. Tap *🌐 Online Quiz* for live questions from the internet!\n"
        "3. Answer each question using the inline buttons.\n"
        "4. See your result and check the leaderboard!\n\n"
        "*Commands*\n"
        "/start       — Main menu\n"
        "/quiz        — Local category picker\n"
        "/onlinequiz  — Online category picker\n"
        "/create      — Make your own quiz\n"
        "/score       — Your personal stats\n"
        "/leaderboard — Top players\n"
        "/help        — This message"
    )
    target = update.message or update.callback_query.message
    await target.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    categories = quiz_data.get_categories()
    if not categories:
        await update.message.reply_text("⚠️ No questions loaded. Check questions.json.")
        return
    await update.message.reply_text(
        "📂 *Choose a Local Category:*",
        parse_mode="Markdown",
        reply_markup=category_keyboard(categories),
    )
async def online_quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    categories = get_online_category_names()
    await update.message.reply_text(
        "🌐 *Online Quiz — Choose a Category:*\n\n"
        "_Questions are fetched live from the internet!_",
        parse_mode="Markdown",
        reply_markup=online_category_keyboard(categories),
    )
async def score_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    record = quiz_data.get_user_score(uid)
    target = update.message or (update.callback_query and update.callback_query.message)
    if record is None:
        await target.reply_text(
            "You haven't played yet! Tap *🎯 Start Quiz* to begin.",
            parse_mode="Markdown"
        )
        return
    pct = round(record["total_correct"] / record["total_played"] * 100) if record["total_played"] else 0
    text = (
        f"📊 *Your Stats*\n\n"
        f"🎮 Games played: *{record['games']}*\n"
        f"✅ Correct answers: *{record['total_correct']} / {record['total_played']}*\n"
        f"📈 Accuracy: *{pct}%*"
    )
    await target.reply_text(text, parse_mode="Markdown")
async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    board = quiz_data.get_leaderboard(top_n=5)
    target = update.message or (update.callback_query and update.callback_query.message)
    if not board:
        await target.reply_text("No scores yet. Be the first to play! 🏆")
        return
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    lines = [f"🏆 *Leaderboard — Top {len(board)}*\n"]
    for entry in board:
        medal = medals[entry["rank"] - 1]
        pct = round(entry["total_correct"] / entry["total_played"] * 100) if entry["total_played"] else 0
        lines.append(f"{medal} *{entry['username']}* — {entry['total_correct']} pts ({pct}%)")
    await target.reply_text("\n".join(lines), parse_mode="Markdown")
async def create_quiz_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("To create a quiz, use the /create command!")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    routes = {
        "🎯 Start Quiz":   quiz_handler,
        "🌐 Online Quiz":  online_quiz_handler,
        "📊 My Score":     score_handler,
        "🏆 Leaderboard":  leaderboard_handler,
        "🆕 Create Quiz":  create_quiz_text_handler,
        "ℹ️ Help":         help_handler,
    }
    handler = routes.get(text)
    if handler:
        await handler(update, context)
    else:
        await update.message.reply_text(
            "Use the menu buttons below, or type /help.",
            reply_markup=main_menu_keyboard(),
        )
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("cat:"):
        category = data[4:]
        if category == "cancel":
            await query.edit_message_text("Cancelled. Use the menu to start again.")
            return
        questions = quiz_data.get_questions(category)
        if not questions:
            await query.edit_message_text(f"No questions found for '{category}'.")
            return
        session = QuizSession.create(update.effective_user.id, category, questions)
        _set_session(context, session)
        await query.edit_message_text(
            f"✅ Category *{category}* selected!\n"
            f"Get ready — {session.total} questions incoming! 🚀",
            parse_mode="Markdown",
        )
        await _send_question(update, context)
    elif data.startswith("online:"):
        category = data[7:]
        if category == "cancel":
            await query.edit_message_text("Cancelled. Use the menu to start again.")
            return
        await query.edit_message_text(
            f"🌐 Fetching questions for *{category}*...\n\n_Please wait a moment!_",
            parse_mode="Markdown",
        )
        questions = await fetch_questions(category, amount=5)
        if not questions:
            await query.edit_message_text(
                "⚠️ Could not fetch questions from the internet.\n"
                "Check your connection and try again."
            )
            return
        session = QuizSession.create(update.effective_user.id, category, questions)
        _set_session(context, session)
        await query.edit_message_text(
            f"✅ *{category}*\n"
            f"🌐 {session.total} fresh questions loaded from the internet! 🚀",
            parse_mode="Markdown",
        )
        await _send_question(update, context)
    elif data.startswith("ans:"):
        session = _get_session(context)
        if session is None:
            await query.edit_message_text("No active quiz. Tap /quiz to start.")
            return
        chosen = data[4:]
        q = session.current_question
        is_correct = session.check_answer(chosen)
        result_icon = "✅" if is_correct else "❌"
        feedback = f"{result_icon} *{'Correct!' if is_correct else 'Wrong!'}*\n\n💡 {q['explanation']}"

        if not session.is_finished:
            await query.edit_message_text(
                feedback, parse_mode="Markdown", reply_markup=next_question_keyboard()
            )
        else:
            uid = update.effective_user.id
            quiz_data.update_score(uid, _username(update), session.correct, session.total)
            summary = session.summary()
            _clear_session(context)
            await query.edit_message_text(
                feedback + "\n\n" + summary,
                parse_mode="Markdown",
                reply_markup=play_again_keyboard(),
            )
    elif data == "next":
        session = _get_session(context)
        if session is None or session.is_finished:
            await query.edit_message_text("Quiz already finished. Start a new one!")
            return
        await query.edit_message_text("⏭ Loading next question…")
        await _send_question(update, context)
    elif data == "play_again":
        categories = quiz_data.get_categories()
        await query.edit_message_text(
            "📂 *Choose a Category:*",
            parse_mode="Markdown",
            reply_markup=category_keyboard(categories),
        )
    elif data == "play_online":
        categories = get_online_category_names()
        await query.edit_message_text(
            "🌐 *Online Quiz — Choose a Category:*",
            parse_mode="Markdown",
            reply_markup=online_category_keyboard(categories),
        )
    elif data == "main_menu":
        await query.edit_message_text("Use the menu below 👇")