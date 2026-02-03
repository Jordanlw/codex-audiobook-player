"""Domain models for the audiobook player."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Audiobook:
    id: int
    title: str


@dataclass(frozen=True)
class AudioFile:
    id: int
    audiobook_id: int
    path: str
    duration_seconds: float
    order_index: int
    file_hash: str | None = None


@dataclass(frozen=True)
class PlaybackState:
    audiobook_id: int
    audio_file_id: int
    position_seconds: float


@dataclass(frozen=True)
class TranscriptSegment:
    audio_file_id: int
    start_seconds: float
    end_seconds: float
    text: str
