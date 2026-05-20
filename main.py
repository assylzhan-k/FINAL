import logging
import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from handlers import (
    start_handler,
    help_handler,
    quiz_handler,
    score_handler,
    leaderboard_handler,
    text_handler,
    callback_handler,
)
from create_handlers import (
    create_start,
    received_title,
    received_question,
    received_option_a,
    received_option_b,
    received_option_c,
    received_option_d,
    received_correct,
    another_question,
    cancel_create,
    QUIZ_TITLE, Q_TEXT, Q_OPTION_A, Q_OPTION_B, Q_OPTION_C, Q_OPTION_D, Q_CORRECT, Q_ANOTHER,
)

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
def main() -> None:
    token = "8888139889:AAGVQ8Lpx5F8y9_3s3o6ilPBrv8L8jJrkWE"
    if not token:
        raise ValueError("BOT_TOKEN environment variable is not set.")
    app = ApplicationBuilder().token(token).build()
    create_conv = ConversationHandler(
        entry_points=[CommandHandler("create", create_start)],
        states={
            QUIZ_TITLE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, received_title)],
            Q_TEXT:      [MessageHandler(filters.TEXT & ~filters.COMMAND, received_question)],
            Q_OPTION_A:  [MessageHandler(filters.TEXT & ~filters.COMMAND, received_option_a)],
            Q_OPTION_B:  [MessageHandler(filters.TEXT & ~filters.COMMAND, received_option_b)],
            Q_OPTION_C:  [MessageHandler(filters.TEXT & ~filters.COMMAND, received_option_c)],
            Q_OPTION_D:  [MessageHandler(filters.TEXT & ~filters.COMMAND, received_option_d)],
            Q_CORRECT:   [CallbackQueryHandler(received_correct, pattern="^correct_")],
            Q_ANOTHER:   [CallbackQueryHandler(another_question, pattern="^(add_another|finish_quiz)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel_create)],
        per_message=False,
    )
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("quiz", quiz_handler))
    app.add_handler(CommandHandler("score", score_handler))
    app.add_handler(CommandHandler("leaderboard", leaderboard_handler))
    app.add_handler(create_conv)
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    logger.info("Quiz Bot is running. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)
if __name__ == "__main__":
    main()