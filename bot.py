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
    get_hn_matches,
    check_source_preset,
    show_watchlist,
    normalize_keywords,
    track_source_monitor,
    untrack_source_monitor,
    get_bbc_all_matches,
)

load_dotenv()

# =========================
# Config
# =========================

DEFAULT_MONITOR_INTERVAL = 1

# =========================
# Basic commands
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Page Change Tracker\n\n"
        "Keyword monitoring for structured sources.\n\n"
        "Available sources:\n"
        "– bbc — RSS Feed / BBC News\n"
        "– hn — Structured Link Feed / Hacker News\n\n"
        "Check now:\n"
        "/check_source bbc government police\n"
        "/check_source hn ai python\n\n"
        "Saved keywords:\n"
        "/set_keywords ai python bot\n"
        "/show_keywords\n\n"
        "Background monitoring:\n"
        "/track hn ai python\n"
        "/track bbc trump police"
        "/track hn\n"
        "/untrack hn\n"
        "/untrack bbc"
        "/watchlist\n\n"
        "Use /help for details."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "Main commands\n\n"
        "Check sources:\n"
        "/check_source <source> <keywords>\n\n"
        "Sources:\n"
        "– bbc — BBC News RSS feeds\n"
        "– hn — Hacker News newest\n\n"
        "Keywords:\n"
        "/set_keywords <keywords>\n"
        "/show_keywords\n\n"
        "Monitoring:\n"
        "/track <source> <keywords>\n"
        "/track <source>\n"
        "/untrack <source>\n"
        "/watchlist\n\n"
        "Examples:\n"
        "/check_source bbc trump police\n"
        "/check_source hn ai python\n"
        "/set_keywords ai, python, bot\n"
        "/track hn ai python\n"
        "/track bbc trump police\n"
        "/track hn\n"
        "/untrack hn"
        "/untrack bbc"
    )

# =========================
# Keyword commands
# =========================

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

# =========================
# Monitor commands
# =========================

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.effective_message.reply_text(
            "Use:\n"
            "/track <source> <keywords>\n"
            "/track <source>\n\n"
            "Examples:\n"
            "/track hn ai python bot\n"
            "/track hn"
        )
        return
    
    source_key = context.args[0]
    chat_id = str(update.effective_chat.id)

    keywords = normalize_keywords(context.args[1:])

    if not keywords:
        state = read_state()

        if chat_id not in state or "keywords" not in state[chat_id]:
            await update.effective_message.reply_text(
                "No keywords provided or saved.\n\n"
                "Use:\n"
                "/track hn ai python bot\n\n"
                "Or save keywords first:\n"
                "/set_keywords ai python bot\n"
                "/track hn"
            )
            return
        
        keywords = state[chat_id]["keywords"]

    result = track_source_monitor(
        chat_id,
        source_key,
        DEFAULT_MONITOR_INTERVAL,
        keywords
    )    

    await update.effective_message.reply_text(result)

async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.effective_message.reply_text(
            "Use: /untrack <source>\n\n"
            "Examples:\n"
            "/untrack hn\n"
            "/untrack bbc"
        )
        return
    
    chat_id = str(update.effective_chat.id)
    source_key = context.args[0]

    result = untrack_source_monitor(chat_id, source_key)

    await update.effective_message.reply_text(result)

# =========================
# Background jobs
# =========================

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

            source_type = data.get("source")
            keywords = data.get("keywords", [])

            interval = data.get("interval", 1) * 60
            last_check = data.get("last_check", 0)

            if current_time - last_check < interval:
                continue

            state[chat_id]["monitors"][monitor_id]["last_check"] = current_time

            if source_type == "hacker_news":
                url = data.get("url")

                if not url:
                    continue

                matches = get_hn_matches(url, keywords)

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

            elif source_type == "bbc_all":
                matches = get_bbc_all_matches(keywords)

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
                            "Source: BBC News\n"
                            "Adapter: RSS Feed\n\n"
                            f"{item['title']}\n"
                            f"Feed: {item['source']}\n"
                            f"Published: {item['published']}\n"
                            f"Keywords: {keywords_text}\n"
                            f"{item['link']}"
                        )
                    )

                    seen_links.append(item["link"])

                state[chat_id]["monitors"][monitor_id]["seen_links"] = seen_links

    write_state(state)

# =========================
# Source check commands
# =========================

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

# =========================
# App setup
# =========================

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found")

app = Application.builder().token(TOKEN).build()

# =========================
# Handlers
# =========================

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("set_keywords", set_keywords_command))
app.add_handler(CommandHandler("show_keywords", show_keywords_command))
app.add_handler(CommandHandler("track", track))
app.add_handler(CommandHandler("check_source", check_source))
app.add_handler(CommandHandler("watchlist", watchlist))
app.add_handler(CommandHandler("untrack", untrack))

# =========================
# Scheduled jobs
# =========================

app.job_queue.run_repeating(check_monitors, interval=30, first=10)

# =========================
# Run bot
# =========================

app.run_polling(drop_pending_updates=True)