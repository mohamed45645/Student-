from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("STUDYFLOW_DB_PATH", ROOT / "data" / "studyflow.db"))


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                title TEXT NOT NULL,
                deadline TEXT NOT NULL,
                priority TEXT NOT NULL CHECK(priority IN ('High','Medium','Low')),
                status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open','In progress','Completed')),
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                minutes INTEGER NOT NULL CHECK(minutes BETWEEN 1 AND 600),
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            )
        """)


def add_task(subject: str, title: str, deadline: str, priority: str) -> int:
    with _connect() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks(subject,title,deadline,priority) VALUES(?,?,?,?)",
            (subject, title, deadline, priority),
        )
        return int(cursor.lastrowid)


def list_tasks() -> pd.DataFrame:
    with _connect() as connection:
        return pd.read_sql_query("SELECT * FROM tasks ORDER BY CASE priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END, deadline, id DESC", connection)


def update_task(task_id: int, status: str) -> None:
    if status not in {"Open", "In progress", "Completed"}:
        raise ValueError("Invalid task status")
    with _connect() as connection:
        connection.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))


def delete_task(task_id: int) -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM tasks WHERE id=?", (task_id,))


def add_session(subject: str, minutes: int, notes: str = "") -> int:
    if not 1 <= int(minutes) <= 600:
        raise ValueError("Session length must be between 1 and 600 minutes")
    with _connect() as connection:
        cursor = connection.execute(
            "INSERT INTO sessions(subject,minutes,notes) VALUES(?,?,?)",
            (subject, int(minutes), notes),
        )
        return int(cursor.lastrowid)


def list_sessions(days: int | None = 7, limit: int = 100) -> pd.DataFrame:
    query = "SELECT * FROM sessions"
    params: list[object] = []
    if days is not None:
        query += " WHERE date(created_at) >= date('now','localtime', ?)"
        params.append(f"-{int(days) - 1} days")
    query += " ORDER BY created_at DESC, id DESC LIMIT ?"
    params.append(int(limit))
    with _connect() as connection:
        return pd.read_sql_query(query, connection, params=params)


def get_summary() -> dict[str, int]:
    with _connect() as connection:
        task_counts = connection.execute("""
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN status != 'Completed' THEN 1 ELSE 0 END) AS open_count,
                   SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed_count
            FROM tasks
        """).fetchone()
        session_counts = connection.execute("""
            SELECT COALESCE(SUM(minutes),0) AS total_minutes,
                   SUM(CASE WHEN date(created_at) >= date('now','localtime','-6 days') THEN 1 ELSE 0 END) AS week_sessions
            FROM sessions
        """).fetchone()
    return {
        "open_tasks": int(task_counts["open_count"] or 0),
        "completed_tasks": int(task_counts["completed_count"] or 0),
        "total_minutes": int(session_counts["total_minutes"] or 0),
        "week_sessions": int(session_counts["week_sessions"] or 0),
    }
