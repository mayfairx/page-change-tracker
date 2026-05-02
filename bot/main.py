import os
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from bot.handlers import (
    start,
    help_command,
    handle_button,
    handle_text,
    set_keywords_command,
    show_keywords_command,
    track_command,
    untrack_command,
    check_source_command,
    watchlist_command,
    check_monitors,
)

from core.db import init_db

load_dotenv()
init_db()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("set_keywords", set_keywords_command))
app.add_handler(CommandHandler("show_keywords", show_keywords_command))
app.add_handler(CommandHandler("track", track_command))
app.add_handler(CommandHandler("check_source", check_source_command))
app.add_handler(CommandHandler("watchlist", watchlist_command))
app.add_handler(CommandHandler("untrack", untrack_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CallbackQueryHandler(handle_button))
app.job_queue.run_repeating(check_monitors, interval=30, first=10)

app.run_polling(drop_pending_updates=True)
