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
    get_listings,
    check_new_listings,
    check_keyword,
    check_keywords,
    set_keywords,
    show_keywords,
    check_saved_keywords,
    check_hn_topics,
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
            if "hash" not in data:
                continue

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
        "This bot tracks webpage changes, listings, and keywords.\n\n"
        "Main commands:\n"
        "/track <url> <minutes> — track page changes\n"
        "/untrack <url> — stop tracking a page\n"
        "/show — show tracked pages\n"
        "/check <url> — manual page check\n\n"
        "Listings:\n"
        "/listings <url> — show parsed listings\n"
        "/new_listings <url> — check new listings\n\n"
        "Keywords:\n"
        "/check_keyword <url> <keyword> — check one keyword\n"
        "/check_keywords <url> <keyword1> <keyword2> — check multiple keywords\n"
        "/set_keywords <keyword1> <keyword2> — save keywords\n"
        "/show_keywords — show saved keywords\n\n"
        "Example:\n"
        "/set_keywords example domain\n"
        "/check_keywords https://example.com example domain"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Commands:\n\n"
        "/track <url> <minutes> — track page changes\n"
        "/untrack <url> — stop tracking\n"
        "/show — show tracked pages\n"
        "/check <url> — manual page check\n"
        "/reset — clear all data\n\n"
        "/listings <url> — show listings\n"
        "/new_listings <url> — check new listings\n\n"
        "/check_keyword <url> <keyword> — check one keyword\n"
        "/check_keywords <url> <keyword1> <keyword2> — check multiple keywords\n"
        "/set_keywords <keyword1> <keyword2> — save keywords\n"
        "/show_keywords — show saved keywords"
    )

async def listings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Use: /listings <url>")
        return
    
    url = context.args[0]
    items = get_listings(url)

    if items is None:
        await update.effective_message.reply_text("Could not get listings.")
        return
    
    if not items:
        await update.effective_message.reply_text("No listings found.")
        return
    
    message = "Listings:\n\n"

    for item in items[:5]:
        message += (
             f"{item['title']}\n"
             f"{item['price']}\n"
             f"{item['link']}\n\n"
        )

    await update.effective_message.reply_text(message)

async def new_listings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Use: /new_listings <url>")
        return
    
    chat_id = str(update.effective_chat.id)
    url = context.args[0]

    result = check_new_listings(chat_id, url)

    await update.effective_message.reply_text(result)

async def check_keyword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.effective_message.reply_text("Use: /check_keyword <url> <keyword>")
        return
    
    url = context.args[0]
    keyword = context.args[1]

    result = check_keyword(url, keyword)

    await update.effective_message.reply_text(result)

async def check_keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.effective_message.reply_text("Use: /check_keywords <url> <keyword1> <keyword2>")
        return
    
    url = context.args[0]
    keywords = context.args[1:]

    result = check_keywords(url, keywords)

    await update.effective_message.reply_text(result)

async def set_keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Use: /set_keywords <keyword1> <keyword2>")
        return
    
    chat_id = str(update.effective_chat.id)
    keywords = context.args

    result = set_keywords(chat_id, keywords)

    await update.effective_message.reply_text(result)

async def show_keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    result = show_keywords(chat_id)

    await update.effective_message.reply_text(result)

async def check_saved_keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.effective_message.reply_text("Use: /check_saved_keywords <url>")
        return
    
    chat_id = str(update.effective_chat.id)
    url = context.args[0]

    result = check_saved_keywords(chat_id, url)

    await update.effective_message.reply_text(result)

async def check_hn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.effective_message.reply_text("Use: /check_hn <url> <keyword1> <keyword2>")
        return

    url = context.args[0]
    keywords = context.args[1:]

    result = check_hn_topics(url, keywords)

    await update.effective_message.reply_text(result)

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
app.add_handler(CommandHandler("listings", listings))
app.add_handler(CommandHandler("new_listings", new_listings))
app.add_handler(CommandHandler("check_keyword", check_keyword_command))
app.add_handler(CommandHandler("check_keywords", check_keywords_command))
app.add_handler(CommandHandler("set_keywords", set_keywords_command))
app.add_handler(CommandHandler("show_keywords", show_keywords_command))
app.add_handler(CommandHandler("check_saved_keywords", check_saved_keywords_command))
app.add_handler(CommandHandler("check_hn", check_hn))

app.job_queue.run_repeating(check_tracked_pages, interval=30, first=5)

app.run_polling(drop_pending_updates=True)