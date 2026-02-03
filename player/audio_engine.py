"""Audio playback helpers using FFmpeg/ffplay for time-stretching."""
from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PlaybackCommand:
    args: list[str]

    def display(self) -> str:
        return " ".join(shlex.quote(arg) for arg in self.args)


def build_atempo_filter(speed: float) -> str:
    if speed <= 0:
        raise ValueError("Speed must be positive")
    filters: list[str] = []
    remaining = speed

    while remaining > 2.0:
        filters.append("atempo=2.0")
        remaining /= 2.0

    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining *= 2.0

    filters.append(f"atempo={remaining:.3f}")
    return ",".join(filters)


def build_ffplay_command(audio_path: str | Path, speed: float) -> PlaybackCommand:
    atempo = build_atempo_filter(speed)
    return PlaybackCommand(
        args=[
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-af",
            atempo,
            str(audio_path),
        ]
    )


def start_ffplay(audio_path: str | Path, speed: float) -> subprocess.Popen:
    command = build_ffplay_command(audio_path, speed)
    return subprocess.Popen(command.args)
