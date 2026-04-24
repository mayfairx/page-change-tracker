from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from page_checker import check_page_change, show_tracked_pages, reset_tracked_pages

import os

load_dotenv()

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Use: /check <url>")
        return
    
    url = context.args[0]
    result = check_page_change(url)

    await update.effective_message.reply_text(result)

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = show_tracked_pages()
    await update.effective_message.reply_text(result)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = reset_tracked_pages()
    await update.effective_message.reply_text(result)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("show", show))
app.add_handler(CommandHandler("reset", reset))

app.run_polling(drop_pending_updates=True)