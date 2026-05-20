import uuid
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from handlers import quiz_data

logger = logging.getLogger(__name__)
(
    QUIZ_TITLE,
    Q_TEXT,
    Q_OPTION_A,
    Q_OPTION_B,
    Q_OPTION_C,
    Q_OPTION_D,
    Q_CORRECT,
    Q_ANOTHER,
) = range(8)
def _new_quiz(context: ContextTypes.DEFAULT_TYPE) -> dict:
    return context.user_data.setdefault("new_quiz", {"questions": []})

def _correct_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("A", callback_data="correct_A"),
        InlineKeyboardButton("B", callback_data="correct_B"),
        InlineKeyboardButton("C", callback_data="correct_C"),
        InlineKeyboardButton("D", callback_data="correct_D"),
    ]])
def _another_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("➕ Add another question", callback_data="add_another"),
        InlineKeyboardButton("✅ Finish quiz",          callback_data="finish_quiz"),
    ]])
async def create_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("new_quiz", None)
    context.user_data.pop("current_question", None)
    await update.message.reply_text(
        "🆕 *Let's create a quiz!*\n\nWhat's the *title* of your quiz?",
        parse_mode="Markdown",
    )
    return QUIZ_TITLE
async def received_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    _new_quiz(context)["title"] = update.message.text.strip()
    await update.message.reply_text("Great! Send the *first question* text:", parse_mode="Markdown")
    return Q_TEXT
async def received_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["current_question"] = {
        "question": update.message.text.strip(),
        "options": [],
    }
    await update.message.reply_text("Send *option A*:", parse_mode="Markdown")
    return Q_OPTION_A
async def received_option_a(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["current_question"]["options"].append(update.message.text.strip())
    await update.message.reply_text("Send *option B*:", parse_mode="Markdown")
    return Q_OPTION_B

async def received_option_b(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["current_question"]["options"].append(update.message.text.strip())
    await update.message.reply_text("Send *option C*:", parse_mode="Markdown")
    return Q_OPTION_C

async def received_option_c(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["current_question"]["options"].append(update.message.text.strip())
    await update.message.reply_text("Send *option D*:", parse_mode="Markdown")
    return Q_OPTION_D

async def received_option_d(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["current_question"]["options"].append(update.message.text.strip())
    opts = context.user_data["current_question"]["options"]
    preview = "\n".join(f"  {lbl}. {opt}" for lbl, opt in zip("ABCD", opts))
    await update.message.reply_text(
        f"*Options:*\n{preview}\n\nWhich one is correct?",
        parse_mode="Markdown",
        reply_markup=_correct_keyboard(),
    )
    return Q_CORRECT

async def received_correct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    letter = query.data.split("_")[1]
    idx    = ord(letter) - ord("A")
    q      = context.user_data["current_question"]
    q["answer"]      = q["options"][idx]
    q["explanation"] = f"The correct answer is {letter}. {q['answer']}"

    _new_quiz(context)["questions"].append(q)
    count = len(_new_quiz(context)["questions"])

    await query.edit_message_text(
        f"✅ Question {count} saved! (correct: *{letter}*)\n\nWhat next?",
        parse_mode="Markdown",
        reply_markup=_another_keyboard(),
    )
    return Q_ANOTHER
async def another_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "add_another":
        await query.edit_message_text("Send the next *question* text:", parse_mode="Markdown")
        return Q_TEXT
    return await _save_and_finish(update, context)
async def _save_and_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query     = update.callback_query
    quiz      = _new_quiz(context)
    title     = quiz.get("title", "Untitled")
    questions = quiz.get("questions", [])
    creator   = update.effective_user.first_name or "Someone"

    if not questions:
        await query.edit_message_text("⚠️ No questions added. Quiz not saved.")
        return ConversationHandler.END
    category_name = f"👤 {title} (by {creator})"
    quiz_data._questions[category_name] = questions
    quiz_data._save_questions()

    await query.edit_message_text(
        f"🎉 *\"{title}\"* is live!\n"
        f"• {len(questions)} question(s)\n"
        f"• Category: `{category_name}`\n\n"
        f"Anyone can play it via */quiz* → scroll to find it!",
        parse_mode="Markdown",
    )
    context.user_data.pop("new_quiz", None)
    context.user_data.pop("current_question", None)
    return ConversationHandler.END

async def cancel_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("new_quiz", None)
    context.user_data.pop("current_question", None)
    await update.message.reply_text("❌ Quiz creation cancelled.")
    return ConversationHandler.END