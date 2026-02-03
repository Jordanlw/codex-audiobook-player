# Building a Windows 11 single-file exe

This project uses **PyInstaller** to produce a single-file executable that bundles `ffplay.exe` for pitch-preserving playback speed control.

## Prerequisites
- Windows 11
- Python 3.11+
- `ffplay.exe` from an FFmpeg build

Install PyInstaller:

```bash
pip install pyinstaller
```

## Build

Run the helper script with the path to `ffplay.exe`:

```bash
python build_windows_exe.py --ffplay C:\path\to\ffplay.exe
```

The output will be in `dist/audiobook-player.exe`.

## One-click build (ffplay next to script)

Place `ffplay.exe` in the same folder as `build_windows_exe.bat`, then double-click the batch file:

```
build_windows_exe.bat
```

The output will be in `dist/audiobook-player.exe`.

## Notes
- The GUI launches `ffplay.exe` from the bundled executable, so you do **not** need `ffplay` on PATH at runtime.
- If you see antivirus warnings, add your build output to the allowlist.
