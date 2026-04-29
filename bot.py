from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

import os
import time

from page_checker import (
    read_state,
    write_state,
    set_keywords,
    show_keywords,
    track_hn_page,
    get_hn_matches,
    check_source_preset,
    show_watchlist,
    normalize_keywords,
)

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Page Change Tracker\n\n"
        "Keyword monitoring for structured sources.\n\n"
        "Available sources:\n"
        "– bbc_all — RSS Feed / BBC News\n"
        "– hacker_news — Structured Link Feed / Hacker News\n\n"
        "Check now:\n"
        "/check_source bbc_all government police\n"
        "/check_source hn ai python\n\n"
        "Saved keywords:\n"
        "/set_keywords ai python bot\n"
        "/show_keywords\n\n"
        "Background monitoring:\n"
        "/track_hn https://news.ycombinator.com/newest 1 ai python\n"
        "/watchlist\n\n"
        "Use /help for details."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Main commands\n\n"
        "Check sources:\n"
        "/check_source <source> <keywords>\n\n"
        "Sources:\n"
        "– bbc_all / bbc — BBC News RSS feeds\n"
        "– hacker_news / hn — Hacker News newest\n\n"
        "Keywords:\n"
        "/set_keywords <keywords>\n"
        "/show_keywords\n\n"
        "Monitoring:\n"
        "/track_hn <url> <minutes> <keywords>\n"
        "/watchlist\n\n"
        "Examples:\n"
        "/check_source bbc_all trump police\n"
        "/check_source hn ai python\n"
        "/set_keywords ai, python, bot\n"
        "/track_hn https://news.ycombinator.com/newest 1 ai python"
    )
    
async def set_keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Use: /set_keywords <keyword1> <keyword2>")
        return
    
    chat_id = str(update.effective_chat.id)
    keywords = normalize_keywords(context.args)

    if not keywords:
        await update.effective_message.reply_text("No valid keywords provided.")
        return

    result = set_keywords(chat_id, keywords)

    await update.effective_message.reply_text(result)

async def show_keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    result = show_keywords(chat_id)

    await update.effective_message.reply_text(result)

async def track_hn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.effective_message.reply_text(
            "Use: /track_hn <url> <minutes> <keyword1> <keyword2>\n\n"
            "Or save keywords first with /set_keywords and use:\n"
            "/track_hn <url> <minutes>"
        )
        return

    url = context.args[0]
    interval = context.args[1]

    if not interval.isdigit():
        await update.effective_message.reply_text(
            "Interval must be a number. Example: /track_hn https://news.ycombinator.com/newest 1 ai python"
        )
        return

    interval = int(interval)
    chat_id = str(update.effective_chat.id)

    keywords = normalize_keywords(context.args[2:])

    if not keywords:
        state = read_state()

        if chat_id not in state or "keywords" not in state[chat_id]:
            await update.effective_message.reply_text(
                "No keywords provided or saved.\n\n"
                "Use: /track_hn <url> <minutes> <keyword1> <keyword2>\n"
                "Or save keywords first with /set_keywords."
            )
            return

        keywords = state[chat_id]["keywords"]

    result = track_hn_page(chat_id, url, interval, keywords)

    await update.effective_message.reply_text(result)

async def check_monitors(context: ContextTypes.DEFAULT_TYPE):
    state = read_state()
    current_time = time.time()

    for chat_id, user_data in state.items():
        if not isinstance(user_data, dict):
            continue

        monitors = user_data.get("monitors", {})

        if not isinstance(monitors, dict):
            continue

        for monitor_id, data in monitors.items():
            if not isinstance(data, dict):
                continue

            if data.get("source") != "hacker_news":
                continue

            url = data.get("url")

            if not url:
                continue

            interval = data.get("interval", 1) * 60
            last_check = data.get("last_check", 0)

            if current_time - last_check < interval:
                continue

            matches = get_hn_matches(url, data.get("keywords", []))

            state[chat_id]["monitors"][monitor_id]["last_check"] = current_time

            if matches is None:
                continue

            seen_links = data.get("seen_links", [])

            for item in matches:
                if item["link"] in seen_links:
                    continue

                keywords_text = ", ".join(item["keywords"])

                await context.bot.send_message(
                    chat_id=int(chat_id),
                    text=(
                        "New monitor item:\n\n"
                        "Source: Hacker News\n"
                        "Adapter: Structured Link Feed\n\n"
                        f"{item['title']}\n"
                        f"Time: {item['age']}\n"
                        f"Keywords: {keywords_text}\n"
                        f"{item['link']}"
                    )
                )

                seen_links.append(item["link"])

            state[chat_id]["monitors"][monitor_id]["seen_links"] = seen_links

    write_state(state)

async def check_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.effective_message.reply_text(
            "Use: /check_source <source> <keyword1> <keyword2>\n\n"
            "Available sources:\n"
            "bbc_all\n"
            "hacker_news\n\n"
            "Examples:\n"
            "/check_source bbc_all ai trump police\n"
            "/check_source hacker_news ai python bot"
        )
        return

    source_key = context.args[0]
    keywords = normalize_keywords(context.args[1:])

    if not keywords:
        await update.effective_message.reply_text("No valid keywords provided.")
        return

    result = check_source_preset(source_key, keywords)

    await update.effective_message.reply_text(result)

async def watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    result = show_watchlist(chat_id)

    await update.effective_message.reply_text(result)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("set_keywords", set_keywords_command))
app.add_handler(CommandHandler("show_keywords", show_keywords_command))
app.add_handler(CommandHandler("track_hn", track_hn))
app.add_handler(CommandHandler("check_source", check_source))
app.add_handler(CommandHandler("watchlist", watchlist))

app.job_queue.run_repeating(check_monitors, interval=30, first=10)

app.run_polling(drop_pending_updates=True)