"""Build a single-file Windows executable with ffplay bundled."""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def build_command(ffplay_path: Path) -> list[str]:
    return [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name",
        "audiobook-player",
        "--add-binary",
        f"{ffplay_path};.",
        "gui.py",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a single-file Windows exe with ffplay bundled."
    )
    parser.add_argument(
        "--ffplay",
        required=True,
        type=Path,
        help="Path to ffplay.exe to bundle.",
    )
    args = parser.parse_args()

    if shutil.which("pyinstaller") is None:
        raise SystemExit("pyinstaller is required. Install with: pip install pyinstaller")

    ffplay_path = args.ffplay
    if not ffplay_path.exists():
        raise SystemExit(f"ffplay not found at {ffplay_path}")

    command = build_command(ffplay_path)
    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
