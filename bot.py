from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

import os
import time

from page_checker import (
    check_page_change,
    show_tracked_pages, 
    reset_tracked_pages, 
    track_page,
    read_state,
    write_state,
    get_page_content,
    get_page_hash,
    untrack_page,
)

load_dotenv()

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Use: /check <url>")
        return
    
    url = context.args[0]
    result = check_page_change(url)

    await update.effective_message.reply_text(result)

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    result = show_tracked_pages(chat_id)
    await update.effective_message.reply_text(result)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = reset_tracked_pages()
    await update.effective_message.reply_text(result)

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.effective_message.reply_text("Use: /track <url> <minutes>")
        return
    
    url = context.args[0]
    interval = context.args[1]

    if not interval.isdigit():
        await update.effective_message.reply_text(
            "Interval must be a number. Example: /track https://example.com 5"
        )
        return
    
    interval = int(interval)
    
    chat_id = str(update.effective_chat.id)
    result = track_page(chat_id, url, interval)
    
    await update.effective_message.reply_text(result)

async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.effective_message.reply_text("Use: /untrack <url>")
        return
    
    chat_id = str(update.effective_chat.id)
    url = context.args[0]

    result = untrack_page(chat_id, url)

    await update.effective_message.reply_text(result)

async def check_tracked_pages(context: ContextTypes.DEFAULT_TYPE):
    state = read_state()
    current_time = time.time()

    for chat_id, pages in state.items():
        for url, data in pages.items():
            interval = data["interval"] * 60
            last_check = data["last_check"]

            if current_time - last_check < interval:
                continue

            content = get_page_content(url)

            state[chat_id][url]["last_check"] = current_time

            if content is None:
                continue

            current_hash = get_page_hash(content)
            last_hash = data["hash"]

            if current_hash != last_hash:
                state[chat_id][url]["hash"] = current_hash

                await context.bot.send_message(
                    chat_id=int(chat_id),
                    text=f"Page changed\n\n{url}"
                )

        write_state(state)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
          "Welcome 👋\n\n"
        "This bot tracks webpage changes and notifies you when a page is updated.\n\n"
        "Commands:\n"
        "/track <url> <minutes> — start tracking a page\n"
        "/untrack <url> — stop tracking a page\n"
        "/show — show tracked pages\n"
        "/check <url> — check a page manually\n"
        "/reset — clear all tracked pages\n\n"
        "Example:\n"
        "/track https://example.com 5"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Commands:\n\n"
        "/track <url> <minutes> — start tracking\n"
        "/untrack <url> — stop tracking\n"
        "/show — show tracked pages\n"
        "/check <url> — manual check\n"
        "/reset — clear all pages"
    )

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("show", show))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(CommandHandler("track", track))
app.add_handler(CommandHandler("untrack", untrack))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))

app.job_queue.run_repeating(check_tracked_pages, interval=30, first=5)

app.run_polling(drop_pending_updates=True)