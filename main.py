"""CLI interface for the audiobook player plan implementation."""
from __future__ import annotations

import argparse
from pathlib import Path

from player import db
from player.library import add_audio_file, create_audiobook, list_audio_files, list_audiobooks
from player.models import PlaybackState, TranscriptSegment
from player.playback import PlaybackRepository, advance_position, compute_global_position
from player.transcript import add_segment, find_segment_at_time


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audiobook player plan implementation")
    parser.add_argument("--db", default="data/player.sqlite3", help="Path to sqlite database")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize the database")

    add_book = subparsers.add_parser("add-book", help="Add a new audiobook")
    add_book.add_argument("title")

    list_books = subparsers.add_parser("list-books", help="List audiobooks")
    list_books.set_defaults(command="list-books")

    add_file = subparsers.add_parser("add-file", help="Add audio file to an audiobook")
    add_file.add_argument("audiobook_id", type=int)
    add_file.add_argument("path")
    add_file.add_argument("duration", type=float)
    add_file.add_argument("order_index", type=int)
    add_file.add_argument("--hash", dest="file_hash")

    list_files = subparsers.add_parser("list-files", help="List audio files for an audiobook")
    list_files.add_argument("audiobook_id", type=int)

    update_pos = subparsers.add_parser("update-position", help="Update playback position")
    update_pos.add_argument("audiobook_id", type=int)
    update_pos.add_argument("audio_file_id", type=int)
    update_pos.add_argument("position", type=float)

    advance = subparsers.add_parser("advance", help="Advance playback position with auto-advance")
    advance.add_argument("audiobook_id", type=int)
    advance.add_argument("audio_file_id", type=int)
    advance.add_argument("position", type=float)
    advance.add_argument("delta", type=float)

    resume = subparsers.add_parser("resume", help="Get stored playback state")
    resume.add_argument("audiobook_id", type=int)

    global_pos = subparsers.add_parser("global-position", help="Compute global position")
    global_pos.add_argument("audiobook_id", type=int)
    global_pos.add_argument("audio_file_id", type=int)
    global_pos.add_argument("position", type=float)

    add_segment_cmd = subparsers.add_parser("add-segment", help="Add transcript segment")
    add_segment_cmd.add_argument("audio_file_id", type=int)
    add_segment_cmd.add_argument("start", type=float)
    add_segment_cmd.add_argument("end", type=float)
    add_segment_cmd.add_argument("text")

    find_segment_cmd = subparsers.add_parser("find-segment", help="Find transcript segment")
    find_segment_cmd.add_argument("audio_file_id", type=int)
    find_segment_cmd.add_argument("position", type=float)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    database_path = Path(args.db)
    connection = db.initialize_db(database_path)

    if args.command == "init":
        print(f"Initialized database at {database_path}")
        return

    if args.command == "add-book":
        book = create_audiobook(connection, args.title)
        print(f"Created audiobook {book.id}: {book.title}")
        return

    if args.command == "list-books":
        for book in list_audiobooks(connection):
            print(f"{book.id}: {book.title}")
        return

    if args.command == "add-file":
        audio_file = add_audio_file(
            connection,
            args.audiobook_id,
            args.path,
            args.duration,
            args.order_index,
            args.file_hash,
        )
        print(f"Added audio file {audio_file.id} to audiobook {audio_file.audiobook_id}")
        return

    if args.command == "list-files":
        files = list_audio_files(connection, args.audiobook_id)
        for audio_file in files:
            print(
                f"{audio_file.id}: {audio_file.path}"
                f" (duration {audio_file.duration_seconds}s, order {audio_file.order_index})"
            )
        return

    repository = PlaybackRepository(connection)

    if args.command == "update-position":
        repository.upsert_state(
            PlaybackState(
                audiobook_id=args.audiobook_id,
                audio_file_id=args.audio_file_id,
                position_seconds=args.position,
            )
        )
        print("Playback position saved.")
        return

    if args.command == "advance":
        files = list_audio_files(connection, args.audiobook_id)
        next_position = advance_position(
            files,
            args.audio_file_id,
            args.position,
            args.delta,
        )
        repository.upsert_state(
            PlaybackState(
                audiobook_id=args.audiobook_id,
                audio_file_id=next_position.audio_file.id,
                position_seconds=next_position.position_seconds,
            )
        )
        print(
            f"Advanced to file {next_position.audio_file.id}"
            f" at {next_position.position_seconds:.2f}s"
        )
        return

    if args.command == "resume":
        state = repository.get_state(args.audiobook_id)
        if not state:
            print("No playback state saved.")
        else:
            print(
                f"Resume audiobook {state.audiobook_id}"
                f" at file {state.audio_file_id} position {state.position_seconds:.2f}s"
            )
        return

    if args.command == "global-position":
        files = list_audio_files(connection, args.audiobook_id)
        global_position = compute_global_position(files, args.audio_file_id, args.position)
        print(f"Global position: {global_position:.2f}s")
        return

    if args.command == "add-segment":
        add_segment(
            connection,
            TranscriptSegment(
                audio_file_id=args.audio_file_id,
                start_seconds=args.start,
                end_seconds=args.end,
                text=args.text,
            ),
        )
        print("Transcript segment added.")
        return

    if args.command == "find-segment":
        segment = find_segment_at_time(connection, args.audio_file_id, args.position)
        if segment:
            print(f"[{segment.start_seconds}-{segment.end_seconds}] {segment.text}")
        else:
            print("No segment found.")
        return


if __name__ == "__main__":
    main()
