"""SQLite persistence layer for the audiobook player."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS audiobooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """.strip(),
    """
    CREATE TABLE IF NOT EXISTS audio_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audiobook_id INTEGER NOT NULL,
        path TEXT NOT NULL,
        duration_seconds REAL NOT NULL,
        order_index INTEGER NOT NULL,
        file_hash TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (audiobook_id) REFERENCES audiobooks (id)
    )
    """.strip(),
    """
    CREATE TABLE IF NOT EXISTS playback_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audiobook_id INTEGER NOT NULL,
        audio_file_id INTEGER NOT NULL,
        position_seconds REAL NOT NULL,
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE (audiobook_id),
        FOREIGN KEY (audiobook_id) REFERENCES audiobooks (id),
        FOREIGN KEY (audio_file_id) REFERENCES audio_files (id)
    )
    """.strip(),
    """
    CREATE TABLE IF NOT EXISTS transcript_segments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audio_file_id INTEGER NOT NULL,
        start_seconds REAL NOT NULL,
        end_seconds REAL NOT NULL,
        text TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (audio_file_id) REFERENCES audio_files (id)
    )
    """.strip(),
)


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA foreign_keys=ON;")
    return connection


def initialize(connection: sqlite3.Connection) -> None:
    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    connection.commit()


def initialize_db(db_path: str | Path) -> sqlite3.Connection:
    connection = connect(db_path)
    initialize(connection)
    return connection


def execute_many(connection: sqlite3.Connection, query: str, rows: Iterable[tuple]) -> None:
    connection.executemany(query, rows)
    connection.commit()
