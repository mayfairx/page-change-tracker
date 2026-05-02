from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import html
from core.state import read_state


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
    context.user_data.pop("pending_untrack_source", None)


def get_saved_keywords_menu():
    keyboard = [
        [
            InlineKeyboardButton("Show keywords", callback_data="saved_keywords_show"),
            InlineKeyboardButton("Set / Replace", callback_data="saved_keywords_set"),
        ],
        [
            InlineKeyboardButton(
                "Clear keywords", callback_data="saved_keywords_clear"
            ),
        ],
        [
            InlineKeyboardButton("Back", callback_data="menu_back"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_confirm_clear_keywords_menu():
    keyboard = [
        [
            InlineKeyboardButton("Clear", callback_data="saved_keywords_clear_confirm"),
            InlineKeyboardButton("Cancel", callback_data="saved_keywords_clear_cancel"),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_start_text():
    return (
        f"{bold('Page Change Tracker')}\n\n"
        "Monitor public sources for signals you care about.\n\n"
        "Set keywords, track Hacker News and BBC News, and get alerts when new matching items appear.\n\n"
        "Choose an action:"
    )


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
    source_name = SOURCE_NAMES.get(source, source)
    escaped_keywords = [html.escape(kw) for kw in keywords]
    keywords_text = ", ".join(escaped_keywords)
    return (
        f"{bold('✅ Confirm monitor')}\n\n"
        f"{bold('Source:')} {bold(source_name)}\n"
        f"{bold('Keywords:')} {keywords_text}\n"
        f"{bold('Interval:')} {interval} min\n\n"
        "Start monitoring?"
    )


def bold(text):
    return f"<b>{text}</b>"


SOURCE_NAMES = {
    "hn": "Hacker News",
    "bbc": "BBC News",
}


class MenuStack:
    def __init__(self):
        self.stack = []

    def push(self, screen_name, **kwargs):
        self.stack.append({"screen": screen_name, "data": kwargs})

    def pop(self):
        if len(self.stack) > 1:
            self.stack.pop()
        return self.stack[-1] if self.stack else None

    def current(self):
        return self.stack[-1] if self.stack else None

    def clear(self):
        self.stack = []


def get_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🔎 Check now", callback_data="menu_check"),
            InlineKeyboardButton("📡 Start monitoring", callback_data="menu_track"),
        ],
        [
            InlineKeyboardButton("📋 Watchlist", callback_data="menu_watchlist"),
            InlineKeyboardButton("🔑 Saved keywords", callback_data="menu_keywords"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_back_menu():
    keyboard = [[InlineKeyboardButton("Back", callback_data="menu_back")]]

    return InlineKeyboardMarkup(keyboard)


def get_watchlist_menu(chat_id):
    state = read_state()
    user_data = state.get(chat_id, {})
    monitors = user_data.get("monitors", {}) if isinstance(user_data, dict) else {}

    has_hn = False
    has_bbc = False

    if isinstance(monitors, dict):
        for data in monitors.values():
            if not isinstance(data, dict):
                continue

            if data.get("source") == "hacker_news":
                has_hn = True

            if data.get("source") == "bbc_all":
                has_bbc = True

    keyboard = []
    stop_buttons = []

    if has_hn:
        stop_buttons.append(
            InlineKeyboardButton("Stop Hacker News", callback_data="untrack_source_hn")
        )

    if has_bbc:
        stop_buttons.append(
            InlineKeyboardButton("Stop BBC News", callback_data="untrack_source_bbc")
        )

    if stop_buttons:
        keyboard.append(stop_buttons)

    keyboard.append([InlineKeyboardButton("Back", callback_data="menu_back")])

    return InlineKeyboardMarkup(keyboard)


def get_confirm_untrack_menu():
    keyboard = [
        [
            InlineKeyboardButton("Stop", callback_data="untrack_confirm_stop"),
            InlineKeyboardButton("Cancel", callback_data="untrack_confirm_cancel"),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_untrack_confirmation_text(context):
    source = context.user_data.get("pending_untrack_source", "unknown")

    if source == "hn":
        source_name = "Hacker News"
    elif source == "bbc":
        source_name = "BBC News"
    else:
        source_name = source

    return f"{bold('⛔ Confirm stop')}\n\n{bold('Source:')} {bold(source_name)}\n\n{bold('Stop this monitor?')}"


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


def get_keyword_choice_menu():
    keyboard = [
        [
            InlineKeyboardButton("Enter keywords", callback_data="keywords_enter"),
            InlineKeyboardButton("Use saved keywords", callback_data="keywords_saved"),
        ],
        [InlineKeyboardButton("Back", callback_data="menu_back")],
    ]

    return InlineKeyboardMarkup(keyboard)


DEFAULT_MONITOR_INTERVAL = 1
