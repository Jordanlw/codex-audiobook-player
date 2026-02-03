"""Library management for audiobooks and audio files."""
from __future__ import annotations

import sqlite3
from typing import Iterable, Sequence

from player.models import AudioFile, Audiobook


def create_audiobook(connection: sqlite3.Connection, title: str) -> Audiobook:
    cursor = connection.execute("INSERT INTO audiobooks (title) VALUES (?)", (title,))
    connection.commit()
    return Audiobook(id=cursor.lastrowid, title=title)


def list_audiobooks(connection: sqlite3.Connection) -> Sequence[Audiobook]:
    rows = connection.execute("SELECT id, title FROM audiobooks ORDER BY created_at").fetchall()
    return [Audiobook(id=row["id"], title=row["title"]) for row in rows]


def add_audio_file(
    connection: sqlite3.Connection,
    audiobook_id: int,
    path: str,
    duration_seconds: float,
    order_index: int,
    file_hash: str | None = None,
) -> AudioFile:
    cursor = connection.execute(
        """
        INSERT INTO audio_files (audiobook_id, path, duration_seconds, order_index, file_hash)
        VALUES (?, ?, ?, ?, ?)
        """,
        (audiobook_id, path, duration_seconds, order_index, file_hash),
    )
    connection.commit()
    return AudioFile(
        id=cursor.lastrowid,
        audiobook_id=audiobook_id,
        path=path,
        duration_seconds=duration_seconds,
        order_index=order_index,
        file_hash=file_hash,
    )


def add_audio_files(
    connection: sqlite3.Connection,
    audiobook_id: int,
    files: Iterable[tuple[str, float, int, str | None]],
) -> list[AudioFile]:
    created: list[AudioFile] = []
    for path, duration, order_index, file_hash in files:
        created.append(
            add_audio_file(connection, audiobook_id, path, duration, order_index, file_hash)
        )
    return created


def list_audio_files(connection: sqlite3.Connection, audiobook_id: int) -> Sequence[AudioFile]:
    rows = connection.execute(
        """
        SELECT id, audiobook_id, path, duration_seconds, order_index, file_hash
        FROM audio_files
        WHERE audiobook_id = ?
        ORDER BY order_index
        """,
        (audiobook_id,),
    ).fetchall()
    return [
        AudioFile(
            id=row["id"],
            audiobook_id=row["audiobook_id"],
            path=row["path"],
            duration_seconds=row["duration_seconds"],
            order_index=row["order_index"],
            file_hash=row["file_hash"],
        )
        for row in rows
    ]
