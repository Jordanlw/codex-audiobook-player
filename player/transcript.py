"""Transcript storage and lookup utilities."""
from __future__ import annotations

import sqlite3
from typing import Sequence

from player.models import TranscriptSegment


def add_segment(connection: sqlite3.Connection, segment: TranscriptSegment) -> None:
    connection.execute(
        """
        INSERT INTO transcript_segments (audio_file_id, start_seconds, end_seconds, text)
        VALUES (?, ?, ?, ?)
        """,
        (segment.audio_file_id, segment.start_seconds, segment.end_seconds, segment.text),
    )
    connection.commit()


def list_segments(connection: sqlite3.Connection, audio_file_id: int) -> Sequence[TranscriptSegment]:
    rows = connection.execute(
        """
        SELECT audio_file_id, start_seconds, end_seconds, text
        FROM transcript_segments
        WHERE audio_file_id = ?
        ORDER BY start_seconds
        """,
        (audio_file_id,),
    ).fetchall()
    return [
        TranscriptSegment(
            audio_file_id=row["audio_file_id"],
            start_seconds=row["start_seconds"],
            end_seconds=row["end_seconds"],
            text=row["text"],
        )
        for row in rows
    ]


def find_segment_at_time(
    connection: sqlite3.Connection, audio_file_id: int, position_seconds: float
) -> TranscriptSegment | None:
    row = connection.execute(
        """
        SELECT audio_file_id, start_seconds, end_seconds, text
        FROM transcript_segments
        WHERE audio_file_id = ?
          AND start_seconds <= ?
          AND end_seconds >= ?
        ORDER BY start_seconds
        LIMIT 1
        """,
        (audio_file_id, position_seconds, position_seconds),
    ).fetchone()
    if not row:
        return None
    return TranscriptSegment(
        audio_file_id=row["audio_file_id"],
        start_seconds=row["start_seconds"],
        end_seconds=row["end_seconds"],
        text=row["text"],
    )
