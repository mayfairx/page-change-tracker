import sqlite3

DB_PATH = "data/bot.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitors (
            chat_id TEXT,
            source TEXT,
            url TEXT,
            interval INTEGER,
            keywords TEXT,
            last_check REAL,
            seen_links TEXT
        )
    """)

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            chat_id TEXT,
            keyword TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_keywords(chat_id, keywords):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keywords WHERE chat_id = ?", (chat_id,))
    for kw in keywords:
        cursor.execute(
            "INSERT INTO keywords (chat_id, keyword) VALUES (?, ?)", (chat_id, kw)
        )
    conn.commit()
    conn.close()


def load_keywords(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT keyword FROM keywords WHERE chat_id = ?", (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def save_monitor(chat_id, monitor_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM monitors WHERE chat_id = ? AND url = ?",
        (chat_id, monitor_data["url"]),
    )
    cursor.execute(
        """
                   INSERT INTRO monitors (chat_id, source, url, interval, keywords, last_check, seen_links)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            chat_id,
            monitor_data["source"],
            monitor_data["url"],
            monitor_data["interval"],
            ", ".join(monitor_data.get("seen_links", [])),
        ),
    )
    conn.commit()
    conn.close()


def load_monitors(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT source, url, interval, keywords, last_check, seen_links FROM monitors WHERE chat_id = ?",
        (chat_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    monitors = {}

    for row in rows:
        source, url, interval, keywords_str, last_check, seen_str = row
        monitors[url] = {
            "source": source,
            "url": url,
            "interval": interval,
            "keywords": keywords_str.split(",") if keywords_str else [],
            "last_check": last_check,
            "seen_links": seen_str.split(",") if seen_str else [],
        }
    return monitors


def delete_monitor(chat_id, url):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM monitors WHERE chat_id = ? AND url = ?", (chat_id, url))
    conn.commit()
    conn.close()


def delete_all_monitors(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM monitors WHERE chat_id = ?", (chat_id))
    conn.commit()
    conn.close()


def update_monitor_seen(chat_id, url, last_check, seen_links):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE monitors SET last_check = ?, seen_links = ?
        WHERE chat_id = ? AND url = ?
    """,
        ("last_check", ",".join(seen_links), chat_id, url),
    )
    conn.commit()
    conn.close()
