from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
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
        "Page Change Tracker\n\n" "Choose an action:", reply_markup=get_main_menu()
    )


def get_interval_menu():
    keyboard = [
        [
            InlineKeyboardButton("1 min", callback_data="interval_1"),
            InlineKeyboardButton("5 min", callback_data="interval_5"),
        ],
        [
            InlineKeyboardButton("15 min", callback_data="interval_15"),
            InlineKeyboardButton("Custom", callback_data="interval_custom"),
        ],
        [InlineKeyboardButton("Back", callback_data="menu_back")],
    ]

    return InlineKeyboardMarkup(keyboard)


def clear_pending_monitor(context):
    context.user_data.pop("pending_action", None)
    context.user_data.pop("pending_source", None)
    context.user_data.pop("pending_keywords", None)
    context.user_data.pop("pending_interval", None)
    context.user_data.pop("pending_step", None)


def get_confirm_monitor_menu():
    keyboard = [
        [
            InlineKeyboardButton("✅ Start", callback_data="monitor_confirm_start"),
            InlineKeyboardButton("Cancel", callback_data="monitor_confirm_cancel"),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_monitor_confirmation_text(context):
    source = context.user_data.get("pending_source", "unknown")
    keywords = context.user_data.get("pending_keywords", [])
    interval = context.user_data.get("pending_interval", "?")

    if source == "hn":
        source_name = "Hacker News"
    elif source == "bbc":
        source_name = "BBC News"
    else:
        source_name = source

    keywords_text = ", ".join(keywords)

    return (
        "Confirm monitor\n\n"
        f"Source: {source_name}\n"
        f"Keywords: {keywords_text}\n"
        f"Interval: {interval} min\n\n"
        "Start monitoring?"
    )


def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("Check now", callback_data="menu_check"),
            InlineKeyboardButton("Start monitoring", callback_data="menu_track"),
        ],
        [
            InlineKeyboardButton("Watchlist", callback_data="menu_watchlist"),
            InlineKeyboardButton("Saved keywords", callback_data="menu_keywords"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_back_menu():
    keyboard = [[InlineKeyboardButton("Back", callback_data="menu_back")]]

    return InlineKeyboardMarkup(keyboard)


def get_check_source_menu():
    keyboard = [
        [
            InlineKeyboardButton("Hacker News", callback_data="check_source_hn"),
            InlineKeyboardButton("BBC News", callback_data="check_source_bbc"),
        ],
        [InlineKeyboardButton("Back", callback_data="menu_back")],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_track_source_menu():
    keyboard = [
        [
            InlineKeyboardButton("Hacker News", callback_data="track_source_hn"),
            InlineKeyboardButton("BBC News", callback_data="track_source_bbc"),
        ],
        [InlineKeyboardButton("Back", callback_data="menu_back")],
    ]

    return InlineKeyboardMarkup(keyboard)


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
        "/untrack hn\n"
        "/untrack bbc"
    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "menu_back":
        clear_pending_monitor(context)

        await query.edit_message_text(
            "Page Change Tracker\n\n" "Choose an action:", reply_markup=get_main_menu()
        )
        return

    if data == "menu_check":
        await query.edit_message_text(
            "Check now\n\n" "Choose a source:", reply_markup=get_check_source_menu()
        )
        return

    if data == "menu_track":
        await query.edit_message_text(
            "Start monitoring\n\n" "Choose a source:",
            reply_markup=get_track_source_menu(),
        )
        return

    if data == "track_source_hn":
        context.user_data["pending_action"] = "track"
        context.user_data["pending_source"] = "hn"

        await query.edit_message_text(
            "Hacker News monitoring\n\n" "Choose how to set keywords:",
            reply_markup=get_keyword_choice_menu(),
        )
        return

    if data == "track_source_bbc":
        context.user_data["pending_action"] = "track"
        context.user_data["pending_source"] = "bbc"

        await query.edit_message_text(
            "BBC News monitoring\n\n" "Choose how to set keywords:",
            reply_markup=get_keyword_choice_menu(),
        )
        return

    if data == "menu_watchlist":
        chat_id = str(update.effective_chat.id)
        result = show_watchlist(chat_id)

        await query.edit_message_text(result, reply_markup=get_back_menu())
        return

    if data == "menu_keywords":
        chat_id = str(update.effective_chat.id)
        result = show_keywords(chat_id)

        await query.edit_message_text(result, reply_markup=get_back_menu())
        return

    if data == "check_source_bbc":
        await query.edit_message_text(
            "BBC News\n\n"
            "Send keywords with:\n"
            "/check_source bbc trump police\n\n"
            "Example:\n"
            "/check_source bbc trump, police, government",
            reply_markup=get_back_menu(),
        )
        return

    if data == "check_source_hn":
        await query.edit_message_text(
            "Hacker News\n\n"
            "Send keywords with:\n"
            "/check_source hn ai python\n\n"
            "Example:\n"
            "/check_source hn ai, python, bot",
            reply_markup=get_back_menu(),
        )
        return

    if data == "keywords_enter":
        pending_source = context.user_data.get("pending_source")

        if not pending_source:
            await query.edit_message_text(
                "No source selected.\n\n" "Go back and choose a source first.",
                reply_markup=get_back_menu(),
            )
            return

        context.user_data["pending_step"] = "keywords"

        await query.edit_message_text(
            "Send keywords for this monitor.\n\n" "Example:\n" "ai python bot",
            reply_markup=get_back_menu(),
        )
        return

    if data == "keywords_saved":
        pending_source = context.user_data.get("pending_source")
        chat_id = str(update.effective_chat.id)
        state = read_state()

        if not pending_source:
            await query.edit_message_text(
                "No source selected.\n\n" "Go back and choose a source first.",
                reply_markup=get_back_menu(),
            )
            return

        if (
            chat_id not in state
            or "keywords" not in state[chat_id]
            or not state[chat_id]["keywords"]
        ):
            await query.edit_message_text(
                "No saved keywords found.\n\n"
                "Use /set_keywords first or choose Enter keywords.",
                reply_markup=get_back_menu(),
            )
            return

        keywords = state[chat_id]["keywords"]

        context.user_data["pending_keywords"] = keywords
        context.user_data["pending_step"] = "interval"

        await query.edit_message_text(
            "Choose interval:", reply_markup=get_interval_menu()
        )
        return

    if data in ["interval_1", "interval_5", "interval_15"]:
        pending_source = context.user_data.get("pending_source")
        pending_keywords = context.user_data.get("pending_keywords")

        if not pending_source or not pending_keywords:
            await query.edit_message_text(
                "Monitor setup is incomplete.\n\n" "Go back and start again.",
                reply_markup=get_back_menu(),
            )
            return

        interval = int(data.replace("interval_", ""))

        context.user_data["pending_interval"] = interval
        context.user_data["pending_step"] = "confirm"

        await query.edit_message_text(
            get_monitor_confirmation_text(context),
            reply_markup=get_confirm_monitor_menu(),
        )
        return

    if data == "interval_custom":
        pending_source = context.user_data.get("pending_source")
        pending_keywords = context.user_data.get("pending_keywords")

        if not pending_source or not pending_keywords:
            await query.edit_message_text(
                "Monitor setup is incomplete.\n\n" "Go back and start again.",
                reply_markup=get_back_menu(),
            )
            return

        context.user_data["pending_step"] = "custom_interval"

        await query.edit_message_text(
            "Send custom interval in minutes.\n\n" "Example:\n" "10",
            reply_markup=get_back_menu(),
        )
        return

    if data == "monitor_confirm_start":
        pending_source = context.user_data.get("pending_source")
        pending_keywords = context.user_data.get("pending_keywords")
        pending_interval = context.user_data.get("pending_interval")

        if not pending_source or not pending_keywords or not pending_interval:
            await query.edit_message_text(
                "Monitor setup is incomplete.\n\n" "Go back and start again.",
                reply_markup=get_back_menu(),
            )
            return

        chat_id = str(update.effective_chat.id)

        result = track_source_monitor(
            chat_id, pending_source, pending_interval, pending_keywords
        )

        clear_pending_monitor(context)

        await query.edit_message_text(result, reply_markup=get_back_menu())
        return

    if data == "monitor_confirm_cancel":
        clear_pending_monitor(context)

        await query.edit_message_text(
            "Monitor setup cancelled.", reply_markup=get_back_menu()
        )
        return


def get_keyword_choice_menu():
    keyboard = [
        [
            InlineKeyboardButton("Enter keywords", callback_data="keywords_enter"),
            InlineKeyboardButton("Use saved keywords", callback_data="keywords_saved"),
        ],
        [InlineKeyboardButton("Back", callback_data="menu_back")],
    ]

    return InlineKeyboardMarkup(keyboard)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pending_action = context.user_data.get("pending_action")
    pending_source = context.user_data.get("pending_source")
    pending_step = context.user_data.get("pending_step")

    if pending_action != "track" or not pending_source:
        return

    chat_id = str(update.effective_chat.id)

    if pending_step == "keywords":
        keywords = normalize_keywords(update.effective_message.text.split())

        if not keywords:
            await update.effective_message.reply_text("No valid keywords provided.")
            return

        context.user_data["pending_keywords"] = keywords
        context.user_data["pending_step"] = "interval"

        await update.effective_message.reply_text(
            "Choose interval:", reply_markup=get_interval_menu()
        )
        return

    if pending_step == "custom_interval":
        interval_text = update.effective_message.text.strip()

        if not interval_text.isdigit():
            await update.effective_message.reply_text(
                "Interval must be a number.\n\n" "Example:\n" "10"
            )
            return

        interval = int(interval_text)

        if interval < 1:
            await update.effective_message.reply_text(
                "Interval must be at least 1 minute."
            )
            return

        pending_keywords = context.user_data.get("pending_keywords")

        if not pending_keywords:
            await update.effective_message.reply_text(
                "No keywords found. Start monitor setup again."
            )
            clear_pending_monitor(context)
            return

        context.user_data["pending_interval"] = interval
        context.user_data["pending_step"] = "confirm"

        await update.effective_message.reply_text(
            get_monitor_confirmation_text(context),
            reply_markup=get_confirm_monitor_menu(),
        )
        return


# =========================
# Keyword commands
# =========================


async def set_keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text(
            "Use: /set_keywords <keyword1> <keyword2>"
        )
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
        chat_id, source_key, DEFAULT_MONITOR_INTERVAL, keywords
    )

    await update.effective_message.reply_text(result)


async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.effective_message.reply_text(
            "Use: /untrack <source>\n\n" "Examples:\n" "/untrack hn\n" "/untrack bbc"
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
                        ),
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
                        ),
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

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CallbackQueryHandler(handle_button))
# =========================
# Scheduled jobs
# =========================

app.job_queue.run_repeating(check_monitors, interval=30, first=10)

# =========================
# Run bot
# =========================

app.run_polling(drop_pending_updates=True)
