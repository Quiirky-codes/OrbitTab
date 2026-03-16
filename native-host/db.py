import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any

from migrations import run_migrations

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        run_migrations(self.conn)

    # ----------------------------
    # Save Session
    # ----------------------------
    def save_session(self, groups: List[Dict[str, Any]]):
        now = int(time.time())
        cur = self.conn.cursor()

        cur.execute(
            "INSERT INTO sessions (created, title) VALUES (?, ?)",
            (now, f"Session {now}")
        )
        session_id = cur.lastrowid

        for g in groups:
            cur.execute(
                "INSERT INTO groups (session_id, name, summary) VALUES (?, ?, ?)",
                (session_id, g.get("name"), g.get("summary"))
            )
            group_id = cur.lastrowid

            for t in g.get("tabs", []):
                cur.execute("""
                    INSERT INTO tabs (group_id, tab_id, title, domain, summary, pinned)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    group_id,
                    t.get("tabId"),
                    t.get("title"),
                    t.get("domain"),
                    t.get("summary"),
                    1 if t.get("pinned") else 0
                ))

        self.conn.commit()

    # ----------------------------
    # Get Sessions
    # ----------------------------
    def get_sessions(self):
        sessions = []
        cur = self.conn.cursor()

        for s in cur.execute("SELECT * FROM sessions ORDER BY created DESC"):
            session = {
                "created": s["created"],
                "groups": []
            }

            groups = cur.execute(
                "SELECT * FROM groups WHERE session_id = ?",
                (s["id"],)
            ).fetchall()

            for g in groups:
                group = {
                    "name": g["name"],
                    "summary": g["summary"],
                    "tabs": []
                }

                tabs = cur.execute(
                    "SELECT * FROM tabs WHERE group_id = ?",
                    (g["id"],)
                ).fetchall()

                for t in tabs:
                    group["tabs"].append({
                        "title": t["title"],
                        "domain": t["domain"],
                        "summary": t["summary"],
                        "tabId": t["tab_id"]
                    })

                session["groups"].append(group)

            sessions.append(session)

        return sessions

    # ----------------------------
    # Search
    # ----------------------------
    def search(self, query: str):
        cur = self.conn.cursor()
        rows = cur.execute("""
            SELECT title, domain, summary
            FROM tabs
            WHERE title LIKE ?
               OR summary LIKE ?
               OR domain LIKE ?
            LIMIT 50
        """, (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()

        return [dict(row) for row in rows]