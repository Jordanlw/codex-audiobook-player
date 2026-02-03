"""Playback state and autosave handling."""
from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from typing import Iterable

from player.models import AudioFile, PlaybackState


@dataclass
class PlaybackPosition:
    audio_file: AudioFile
    position_seconds: float


class PlaybackRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get_state(self, audiobook_id: int) -> PlaybackState | None:
        row = self.connection.execute(
            """
            SELECT audiobook_id, audio_file_id, position_seconds
            FROM playback_state
            WHERE audiobook_id = ?
            """,
            (audiobook_id,),
        ).fetchone()
        if not row:
            return None
        return PlaybackState(
            audiobook_id=row["audiobook_id"],
            audio_file_id=row["audio_file_id"],
            position_seconds=row["position_seconds"],
        )

    def upsert_state(self, state: PlaybackState) -> None:
        self.connection.execute(
            """
            INSERT INTO playback_state (audiobook_id, audio_file_id, position_seconds)
            VALUES (?, ?, ?)
            ON CONFLICT(audiobook_id)
            DO UPDATE SET
                audio_file_id = excluded.audio_file_id,
                position_seconds = excluded.position_seconds,
                updated_at = datetime('now')
            """,
            (state.audiobook_id, state.audio_file_id, state.position_seconds),
        )
        self.connection.commit()


def compute_global_position(files: Iterable[AudioFile], current_file_id: int, position: float) -> float:
    total = 0.0
    for audio_file in files:
        if audio_file.id == current_file_id:
            total += position
            break
        total += audio_file.duration_seconds
    return total


def resolve_position_from_global(
    files: Iterable[AudioFile],
    global_position: float,
) -> PlaybackPosition:
    remaining = max(global_position, 0.0)
    last_file: AudioFile | None = None
    for audio_file in files:
        last_file = audio_file
        if remaining <= audio_file.duration_seconds:
            return PlaybackPosition(audio_file=audio_file, position_seconds=remaining)
        remaining -= audio_file.duration_seconds
    if last_file is None:
        raise ValueError("No audio files available for playback.")
    return PlaybackPosition(audio_file=last_file, position_seconds=last_file.duration_seconds)


class PlaybackSession:
    def __init__(self, repository: PlaybackRepository, audiobook_id: int) -> None:
        self.repository = repository
        self.audiobook_id = audiobook_id
        self._autosave_thread: threading.Thread | None = None
        self._autosave_stop = threading.Event()

    def start_autosave(self, state_supplier, interval_seconds: float = 2.5) -> None:
        if self._autosave_thread and self._autosave_thread.is_alive():
            return
        self._autosave_stop.clear()
        self._autosave_thread = threading.Thread(
            target=self._run_autosave, args=(state_supplier, interval_seconds), daemon=True
        )
        self._autosave_thread.start()

    def stop_autosave(self) -> None:
        self._autosave_stop.set()
        if self._autosave_thread:
            self._autosave_thread.join(timeout=1.0)

    def _run_autosave(self, state_supplier, interval_seconds: float) -> None:
        while not self._autosave_stop.is_set():
            state = state_supplier()
            if state:
                self.repository.upsert_state(state)
            self._autosave_stop.wait(interval_seconds)

    def save_state(self, state: PlaybackState) -> None:
        self.repository.upsert_state(state)


def advance_position(
    files: Iterable[AudioFile],
    current_file_id: int,
    position_seconds: float,
    delta_seconds: float,
) -> PlaybackPosition:
    if delta_seconds < 0:
        raise ValueError("Delta seconds must be non-negative")
    files_list = list(files)
    current_index = next(
        (idx for idx, audio_file in enumerate(files_list) if audio_file.id == current_file_id),
        None,
    )
    if current_index is None:
        raise ValueError("Current file not found in audiobook.")

    remaining = position_seconds + delta_seconds
    index = current_index
    while index < len(files_list):
        current_file = files_list[index]
        if remaining <= current_file.duration_seconds:
            return PlaybackPosition(audio_file=current_file, position_seconds=remaining)
        remaining -= current_file.duration_seconds
        index += 1

    last_file = files_list[-1]
    return PlaybackPosition(audio_file=last_file, position_seconds=last_file.duration_seconds)
