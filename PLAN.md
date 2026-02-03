# Windows Audiobook Player Plan

## Goals
- Autosave open files and playback positions, even on force-close or power loss.
- Treat multi-file audiobooks as a single logical book in the UI and playback.
- Persist positions per file and restore reliably.
- Transcribe audio and highlight the currently playing segment/word.

## Architecture Overview
- **UI + Shell:** Windows desktop app (WPF/WinUI or Electron).
- **Audio Engine:** NAudio or FFmpeg-backed playback service.
- **Persistence:** SQLite with WAL + append-only journal for recovery.
- **Transcription:** Whisper (local) or cloud STT, cached on disk.

## Data Model
- **Audiobook**: logical grouping of audio files.
- **AudioFile**: path, duration, order index, hash.
- **PlaybackState**: per-file position, current file, last open books.
- **Transcript**: per-file segments with timestamps.

## Autosave & Recovery
- Save playback position every 2–5 seconds during playback.
- Save immediately on pause/stop/background/exit events.
- Use atomic writes and SQLite WAL for resilience.
- On startup, restore the last session and open books.

## Multi-File Playback
- Treat files as a single timeline:
  - Auto-advance to the next file when one ends.
  - Track **global position** and **per-file position**.
  - Show combined progress in the UI.

## Per-File Position Tracking
- Persist per-file positions with timestamps.
- Restore to the last played file and its exact position.

## Transcription + Highlighting
- Preprocess audio to a consistent format before STT.
- Store transcript segments with start/end timestamps.
- Highlight the segment/word matching current playback time.

## UI/UX
- Library view with multi-file indicators.
- Book detail view showing file list and per-file progress.
- Transcript view with live highlight and click-to-seek.

## Edge Cases
- File moved/deleted: prompt user to relink.
- Partial transcripts: show available segments.
- Large books: lazy-load transcript data.

## Implementation Phases
1. Playback core + multi-file grouping.
2. Autosave + per-file positions.
3. Library UI + resume flow.
4. Transcription pipeline.
5. Transcript highlight UI.
