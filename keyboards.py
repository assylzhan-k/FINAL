from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton("🎯 Start Quiz"),     KeyboardButton("🌐 Online Quiz")],
        [KeyboardButton("📊 My Score"),        KeyboardButton("🏆 Leaderboard")],
        [KeyboardButton("🆕 Create Quiz"),     KeyboardButton("ℹ️ Help")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)

def category_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"📂 {cat}", callback_data=f"cat:{cat}")]
        for cat in categories
    ]
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="cat:cancel")])
    return InlineKeyboardMarkup(buttons)

def online_category_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(cat, callback_data=f"online:{cat}")]
        for cat in categories
    ]
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="online:cancel")])
    return InlineKeyboardMarkup(buttons)

OPTION_LABELS = ["A", "B", "C", "D"]

def answer_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    for label, opt in zip(OPTION_LABELS, options):
        buttons.append([InlineKeyboardButton(f"{label}. {opt}", callback_data=f"ans:{opt}")])
    return InlineKeyboardMarkup(buttons)

def next_question_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Next Question", callback_data="next")]
    ])

def play_again_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Play Again",   callback_data="play_again"),
         InlineKeyboardButton("🌐 Online Quiz",  callback_data="play_online"),
         InlineKeyboardButton("🏠 Main Menu",    callback_data="main_menu")]
    ])