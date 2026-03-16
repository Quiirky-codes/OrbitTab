from pathlib import Path
import sqlite3

SCHEMA_VERSION = 1

def run_migrations(conn: sqlite3.Connection):
    current = conn.execute("PRAGMA user_version").fetchone()[0]

    if current < 1:
        create_v1(conn)
        conn.execute("PRAGMA user_version = 1")
        conn.commit()

def create_v1(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created INTEGER NOT NULL,
        title TEXT
    );

    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        summary TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tabs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        tab_id INTEGER,
        title TEXT,
        domain TEXT,
        summary TEXT,
        pinned INTEGER DEFAULT 0,
        FOREIGN KEY(group_id) REFERENCES groups(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_tabs_domain ON tabs(domain);
    CREATE INDEX IF NOT EXISTS idx_tabs_title ON tabs(title);
    CREATE INDEX IF NOT EXISTS idx_tabs_summary ON tabs(summary);
    """)