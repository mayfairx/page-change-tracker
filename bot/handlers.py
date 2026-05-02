from telegram import Update
from telegram.ext import ContextTypes
import time

from bot.ui import (
    bold,
    MenuStack,
    DEFAULT_MONITOR_INTERVAL,
    get_start_text,
    get_main_menu,
    get_back_menu,
    get_interval_menu,
    get_check_source_menu,
    get_track_source_menu,
    get_saved_keywords_menu,
    get_confirm_monitor_menu,
    get_confirm_untrack_menu,
    get_confirm_clear_keywords_menu,
    get_watchlist_menu,
    get_keyword_choice_menu,
    get_monitor_confirmation_text,
    get_untrack_confirmation_text,
    clear_pending_monitor,
)
from core.checker import (
    read_state,
    write_state,
    set_keywords,
    show_keywords,
    check_source_preset,
    track_source_monitor,
    untrack_source_monitor,
    show_watchlist,
    normalize_keywords,
    clear_keywords,
    get_hn_matches,
    get_bbc_all_matches,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nav = MenuStack()
    nav.push("main_menu")
    context.user_data["nav"] = nav
    await update.effective_message.reply_text(
        get_start_text(), reply_markup=get_main_menu(), parse_mode="HTML"
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
        "/untrack hn\n"
        "/untrack bbc"
    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    async def show_main_menu():
        await query.edit_message_text(
            get_start_text(), reply_markup=get_main_menu(), parse_mode="HTML"
        )

    async def show_check_source():
        await query.edit_message_text(
            f"{bold('🔎 Check now')}\n\nChoose a source:",
            reply_markup=get_check_source_menu(),
            parse_mode="HTML",
        )

    async def show_track_source():
        await query.edit_message_text(
            f"{bold('📡 Start monitoring')}\n\nChoose a source:",
            reply_markup=get_track_source_menu(),
            parse_mode="HTML",
        )

    async def show_keywords_menu():
        await query.edit_message_text(
            f"{bold('🔑 Saved keywords')}\n\nChoose an action:",
            reply_markup=get_saved_keywords_menu(),
            parse_mode="HTML",
        )

    async def render_watchlist():
        chat_id = str(update.effective_chat.id)
        result = show_watchlist(chat_id)
        await query.edit_message_text(
            result, reply_markup=get_watchlist_menu(chat_id), parse_mode="HTML"
        )

    screens = {
        "main_menu": show_main_menu,
        "check_source": show_check_source,
        "track_source": show_track_source,
        "keywords_menu": show_keywords_menu,
        "watchlist": render_watchlist,
    }

    if data == "untrack_confirm_stop":
        source_key = context.user_data.get("pending_untrack_source")
        if not source_key:
            await query.edit_message_text(
                "No source selected.\n\nGo back and try again.",
                reply_markup=get_back_menu(),
                parse_mode="HTML",
            )
            return
        chat_id = str(update.effective_chat.id)
        result = untrack_source_monitor(chat_id, source_key)
        context.user_data.pop("pending_untrack_source", None)
        updated_watchlist = show_watchlist(chat_id)
        await query.edit_message_text(
            f"{result}\n\n{updated_watchlist}",
            reply_markup=get_watchlist_menu(chat_id),
        )
        return

    if data == "untrack_confirm_cancel":
        context.user_data.pop("pending_untrack_source", None)
        chat_id = str(update.effective_chat.id)
        result = show_watchlist(chat_id)
        await query.edit_message_text(
            result, reply_markup=get_watchlist_menu(chat_id), parse_mode="HTML"
        )
        return

    if data == "menu_back":
        clear_pending_monitor(context)
        nav = context.user_data.get("nav")
        if nav:
            nav.pop()
            current = nav.current()
            if current:
                screen_name = current["screen"]
                show_func = screens.get(screen_name)
                if show_func:
                    await show_func()
                    return
        await query.edit_message_text(
            get_start_text(), reply_markup=get_main_menu(), parse_mode="HTML"
        )
        return

    if data == "menu_check":
        nav = context.user_data.get("nav")
        if nav:
            nav.push("check_source")
        await screens["check_source"]()
        return

    if data == "menu_track":
        nav = context.user_data.get("nav")
        if nav:
            nav.push("track_source")
        await screens["track_source"]()
        return

    if data == "track_source_hn":
        context.user_data["pending_action"] = "track"
        context.user_data["pending_source"] = "hn"
        await query.edit_message_text(
            f"{bold('📡 Hacker News monitoring')}\n\nChoose how to set keywords:",
            reply_markup=get_keyword_choice_menu(),
            parse_mode="HTML",
        )
        return

    if data == "track_source_bbc":
        context.user_data["pending_action"] = "track"
        context.user_data["pending_source"] = "bbc"
        await query.edit_message_text(
            f"{bold('📡 BBC News monitoring')}\n\nChoose how to set keywords:",
            reply_markup=get_keyword_choice_menu(),
            parse_mode="HTML",
        )
        return

    if data == "menu_watchlist":
        nav = context.user_data.get("nav")
        if nav:
            nav.push("watchlist")
        await screens["watchlist"]()
        return

    if data == "untrack_source_hn":
        context.user_data["pending_untrack_source"] = "hn"
        await query.edit_message_text(
            get_untrack_confirmation_text(context),
            reply_markup=get_confirm_untrack_menu(),
            parse_mode="HTML",
        )
        return

    if data == "untrack_source_bbc":
        context.user_data["pending_untrack_source"] = "bbc"
        await query.edit_message_text(
            get_untrack_confirmation_text(context),
            reply_markup=get_confirm_untrack_menu(),
            parse_mode="HTML",
        )
        return

    if data == "menu_keywords":
        nav = context.user_data.get("nav")
        if nav:
            nav.push("keywords_menu")
        await screens["keywords_menu"]()
        return

    if data == "saved_keywords_show":
        chat_id = str(update.effective_chat.id)
        result = show_keywords(chat_id)
        await query.edit_message_text(result, reply_markup=get_saved_keywords_menu())
        return

    if data == "saved_keywords_set":
        context.user_data["pending_action"] = "set_keywords"
        context.user_data["pending_step"] = "saved_keywords"
        await query.edit_message_text(
            "Send keywords to save.\n\nExample:\nai python api prompt",
            reply_markup=get_back_menu(),
            parse_mode="HTML",
        )
        return

    if data == "saved_keywords_clear":
        await query.edit_message_text(
            "Clear saved keywords?\n\nThis will remove your saved keyword list.",
            reply_markup=get_confirm_clear_keywords_menu(),
            parse_mode="HTML",
        )
        return

    if data == "saved_keywords_clear_confirm":
        chat_id = str(update.effective_chat.id)
        result = clear_keywords(chat_id)
        clear_pending_monitor(context)
        await query.edit_message_text(result, reply_markup=get_saved_keywords_menu())
        return

    if data == "saved_keywords_clear_cancel":
        clear_pending_monitor(context)
        await query.edit_message_text(
            "Saved keywords\n\nChoose an action:",
            reply_markup=get_saved_keywords_menu(),
            parse_mode="HTML",
        )
        return

    if data == "check_source_bbc":
        context.user_data["pending_action"] = "check"
        context.user_data["pending_source"] = "bbc"
        await query.edit_message_text(
            f"{bold('🔎 BBC News check')}\n\nChoose how to set keywords:",
            reply_markup=get_keyword_choice_menu(),
            parse_mode="HTML",
        )
        return

    if data == "check_source_hn":
        context.user_data["pending_action"] = "check"
        context.user_data["pending_source"] = "hn"
        await query.edit_message_text(
            f"{bold('🔎 Hacker News check')}\n\nChoose how to set keywords:",
            reply_markup=get_keyword_choice_menu(),
            parse_mode="HTML",
        )
        return

    if data == "keywords_enter":
        if not context.user_data.get("pending_source"):
            await query.edit_message_text(
                "No source selected.\n\nGo back and choose a source first.",
                reply_markup=get_back_menu(),
                parse_mode="HTML",
            )
            return
        context.user_data["pending_step"] = "keywords"
        await query.edit_message_text(
            "Send keywords.\n\nExample:\nai python bot",
            reply_markup=get_back_menu(),
        )
        return

    if data == "keywords_saved":
        pending_source = context.user_data.get("pending_source")
        chat_id = str(update.effective_chat.id)
        state = read_state()
        if not pending_source:
            await query.edit_message_text(
                "No source selected.\n\nGo back and choose a source first.",
                reply_markup=get_back_menu(),
            )
            return
        if (
            chat_id not in state
            or "keywords" not in state[chat_id]
            or not state[chat_id]["keywords"]
        ):
            context.user_data["pending_step"] = "keywords"
            await query.edit_message_text(
                f"{bold('No saved keywords yet')}\n\nSend your keywords now — they will be saved automatically.\n\nExample:\nai python bot",
                reply_markup=get_back_menu(),
                parse_mode="HTML",
            )
            return
        keywords = state[chat_id]["keywords"]
        pending_action = context.user_data.get("pending_action")
        if pending_action == "check":
            result = check_source_preset(pending_source, keywords)
            clear_pending_monitor(context)
            await query.edit_message_text(result, reply_markup=get_back_menu())
            return
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
                "Monitor setup is incomplete.\n\nGo back and start again.",
                reply_markup=get_back_menu(),
                parse_mode="HTML",
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
        if not context.user_data.get("pending_source") or not context.user_data.get(
            "pending_keywords"
        ):
            await query.edit_message_text(
                "Monitor setup is incomplete.\n\nGo back and start again.",
                reply_markup=get_back_menu(),
                parse_mode="HTML",
            )
            return
        context.user_data["pending_step"] = "custom_interval"
        await query.edit_message_text(
            "Send custom interval in minutes.\n\nExample:\n10",
            reply_markup=get_back_menu(),
        )
        return

    if data == "monitor_confirm_start":
        pending_source = context.user_data.get("pending_source")
        pending_keywords = context.user_data.get("pending_keywords")
        pending_interval = context.user_data.get("pending_interval")
        if not pending_source or not pending_keywords or not pending_interval:
            await query.edit_message_text(
                "Monitor setup is incomplete.\n\nGo back and start again.",
                reply_markup=get_back_menu(),
                parse_mode="HTML",
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
            "Monitor setup cancelled.", reply_markup=get_back_menu(), parse_mode="HTML"
        )
        return


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pending_action = context.user_data.get("pending_action")
    pending_source = context.user_data.get("pending_source")
    pending_step = context.user_data.get("pending_step")
    if pending_action not in ["track", "check", "set_keywords"]:
        return
    if pending_action in ["track", "check"] and not pending_source:
        return
    chat_id = str(update.effective_chat.id)

    if pending_action == "set_keywords":
        keywords = normalize_keywords(update.effective_message.text.split())
        if not keywords:
            await update.effective_message.reply_text("No valid keywords provided.")
            return
        result = set_keywords(chat_id, keywords)
        clear_pending_monitor(context)
        await update.effective_message.reply_text(
            result, reply_markup=get_saved_keywords_menu()
        )
        return

    if pending_step == "keywords":
        keywords = normalize_keywords(update.effective_message.text.split())
        if not keywords:
            await update.effective_message.reply_text("No valid keywords provided.")
            return
        set_keywords(chat_id, keywords)
        if pending_action == "check":
            result = check_source_preset(pending_source, keywords)
            clear_pending_monitor(context)
            await update.effective_message.reply_text(
                result, reply_markup=get_back_menu()
            )
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
                "Interval must be a number.\n\nExample:\n10"
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


async def track_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.effective_message.reply_text(
            "Use:\n/track <source> <keywords>\n/track <source>\n\nExamples:\n/track hn ai python bot\n/track hn"
        )
        return
    source_key = context.args[0]
    chat_id = str(update.effective_chat.id)
    keywords = normalize_keywords(context.args[1:])
    if not keywords:
        state = read_state()
        if chat_id not in state or "keywords" not in state[chat_id]:
            await update.effective_message.reply_text(
                "No keywords provided or saved.\n\nUse:\n/track hn ai python bot\n\nOr save keywords first:\n/set_keywords ai python bot\n/track hn"
            )
            return
        keywords = state[chat_id]["keywords"]
    result = track_source_monitor(
        chat_id, source_key, DEFAULT_MONITOR_INTERVAL, keywords
    )
    await update.effective_message.reply_text(result)


async def untrack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.effective_message.reply_text(
            "Use: /untrack <source>\n\nExamples:\n/untrack hn\n/untrack bbc"
        )
        return
    chat_id = str(update.effective_chat.id)
    source_key = context.args[0]
    result = untrack_source_monitor(chat_id, source_key)
    await update.effective_message.reply_text(result)


async def check_source_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.effective_message.reply_text(
            "Use: /check_source <source> <keyword1> <keyword2>\n\nAvailable sources:\nbbc_all\nhacker_news\n\nExamples:\n/check_source bbc_all ai trump police\n/check_source hacker_news ai python bot"
        )
        return
    source_key = context.args[0]
    keywords = normalize_keywords(context.args[1:])
    if not keywords:
        await update.effective_message.reply_text("No valid keywords provided.")
        return
    result = check_source_preset(source_key, keywords)
    await update.effective_message.reply_text(result)


async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    result = show_watchlist(chat_id)
    await update.effective_message.reply_text(result, parse_mode="HTML")


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
                        text=f"New monitor item:\n\nSource: Hacker News\nAdapter: Structured Link Feed\n\n{item['title']}\nTime: {item['age']}\nKeywords: {keywords_text}\n{item['link']}",
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
                        text=f"New monitor item:\n\nSource: BBC News\nAdapter: RSS Feed\n\n{item['title']}\nFeed: {item['source']}\nPublished: {item['published']}\nKeywords: {keywords_text}\n{item['link']}",
                    )
                    seen_links.append(item["link"])
                state[chat_id]["monitors"][monitor_id]["seen_links"] = seen_links
    write_state(state)
