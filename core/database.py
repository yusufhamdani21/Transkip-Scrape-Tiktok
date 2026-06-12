import sqlite3
from datetime import datetime, date
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            duration REAL,
            text TEXT NOT NULL,
            language TEXT,
            model TEXT,
            segments TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS trending_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT NOT NULL,
            data TEXT NOT NULL,
            fetched_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS trending_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT NOT NULL,
            rank INTEGER,
            title TEXT,
            author TEXT,
            author_followers INTEGER,
            likes INTEGER,
            comments INTEGER,
            shares INTEGER,
            plays INTEGER,
            hashtags TEXT,
            music TEXT,
            duration INTEGER,
            url TEXT,
            fetched_date TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def save_transcription(filename, duration, text, language, model, segments):
    conn = get_conn()
    conn.execute(
        """INSERT INTO transcriptions (filename, duration, text, language, model, segments)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (filename, duration, text, language, model, str(segments)),
    )
    conn.commit()
    conn.close()


def get_transcriptions(limit=50):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM transcriptions ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_cached_trending(region):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM trending_cache WHERE region = ? ORDER BY fetched_at DESC LIMIT 1",
        (region,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def save_trending_cache(region, data):
    conn = get_conn()
    conn.execute(
        "INSERT INTO trending_cache (region, data) VALUES (?, ?)", (region, data)
    )
    conn.commit()
    conn.close()


def save_trending_history(region, videos):
    conn = get_conn()
    today = date.today().isoformat()
    for rank, v in enumerate(videos, 1):
        conn.execute(
            """INSERT INTO trending_history
               (region, rank, title, author, author_followers, likes, comments,
                shares, plays, hashtags, music, duration, url, fetched_date)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                region,
                rank,
                v.get("title", ""),
                v.get("author", ""),
                v.get("author_followers", 0),
                v.get("likes", 0),
                v.get("comments", 0),
                v.get("shares", 0),
                v.get("plays", 0),
                v.get("hashtags", ""),
                v.get("music", ""),
                v.get("duration", 0),
                v.get("url", ""),
                today,
            ),
        )
    conn.commit()
    conn.close()


def get_trending_history(region, days=7):
    conn = get_conn()
    rows = conn.execute(
        """SELECT * FROM trending_history
           WHERE region = ? AND fetched_date >= date('now', ? || ' days')
           ORDER BY fetched_date DESC, rank""",
        (region, f"-{days}"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
