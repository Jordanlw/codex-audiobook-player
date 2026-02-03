"""Simple GUI for audiobook playback speed control."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from player.audio_engine import PlaybackCommand, build_ffplay_command, start_ffplay


class AudiobookPlayerGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Audiobook Player")
        self.audio_path: Path | None = None
        self.process = None
        self.command_label_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self) -> None:
        container = tk.Frame(self.root, padx=12, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(container, text="Audiobook Player", font=("Arial", 16, "bold"))
        title.pack(anchor=tk.W)

        file_row = tk.Frame(container)
        file_row.pack(fill=tk.X, pady=(12, 6))

        self.file_label = tk.Label(file_row, text="No file selected")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        select_button = tk.Button(file_row, text="Choose File", command=self.select_file)
        select_button.pack(side=tk.RIGHT)

        speed_row = tk.Frame(container)
        speed_row.pack(fill=tk.X, pady=(6, 6))

        speed_label = tk.Label(speed_row, text="Playback Speed:")
        speed_label.pack(side=tk.LEFT)

        self.speed_var = tk.DoubleVar(value=1.0)
        speed_slider = tk.Scale(
            speed_row,
            from_=0.5,
            to=2.5,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=lambda _: self.update_command_preview(),
        )
        speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        controls_row = tk.Frame(container)
        controls_row.pack(fill=tk.X, pady=(12, 6))

        play_button = tk.Button(controls_row, text="Play", command=self.play)
        play_button.pack(side=tk.LEFT)

        stop_button = tk.Button(controls_row, text="Stop", command=self.stop)
        stop_button.pack(side=tk.LEFT, padx=(8, 0))

        command_label = tk.Label(
            container,
            textvariable=self.command_label_var,
            font=("Arial", 9),
            wraplength=520,
            justify=tk.LEFT,
            fg="#555",
        )
        command_label.pack(fill=tk.X, pady=(8, 0))

        self.update_command_preview()

    def select_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select audiobook file",
            filetypes=[("Audio Files", "*.mp3 *.m4a *.wav *.flac"), ("All Files", "*.*")],
        )
        if not path:
            return
        self.audio_path = Path(path)
        self.file_label.config(text=str(self.audio_path))
        self.update_command_preview()

    def update_command_preview(self) -> None:
        if not self.audio_path:
            self.command_label_var.set("Select a file to preview playback command.")
            return
        command = build_ffplay_command(self.audio_path, self.speed_var.get())
        self.command_label_var.set(f"Playback command: {command.display()}")

    def play(self) -> None:
        if not self.audio_path:
            messagebox.showwarning("No file", "Please select an audio file first.")
            return
        self.stop()
        self.process = start_ffplay(self.audio_path, self.speed_var.get())

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=2)
        self.process = None


def main() -> None:
    root = tk.Tk()
    app = AudiobookPlayerGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
