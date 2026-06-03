#!/usr/bin/env python3
"""Archive session logs older than 60 days.

Moves YAML session files from state/sessions/ to state/sessions/archive/
based on the date parsed from their filename (YYYY-MM-DD.yaml).

Usage:
  python3 scripts/archive-sessions.py              # archive files > 60 days old
  python3 scripts/archive-sessions.py --days 30    # override threshold
  python3 scripts/archive-sessions.py --dry-run    # show what would be moved
"""
import argparse
import re
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

from shared import ROOT, STATE_DIR, green, yellow

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SESSIONS_DIR = STATE_DIR / "sessions"
ARCHIVE_DIR = SESSIONS_DIR / "archive"
DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\.yaml$")
DEFAULT_DAYS = 60

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def parse_session_date(filename: str) -> date | None:
    """Extract the date from a session filename like '2026-03-15.yaml'.

    Returns None if the filename doesn't match the expected pattern.
    """
    match = DATE_PATTERN.match(filename)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


def find_archivable_sessions(days: int) -> list[tuple[Path, date]]:
    """Find session files older than `days` days.

    Returns a list of (file_path, session_date) tuples sorted oldest-first.
    Only considers .yaml files directly in state/sessions/ (not archive/).
    """
    if not SESSIONS_DIR.exists():
        return []

    cutoff = date.today() - timedelta(days=days)
    archivable = []

    for f in sorted(SESSIONS_DIR.iterdir()):
        if not f.is_file() or f.name.startswith("."):
            continue
        session_date = parse_session_date(f.name)
        if session_date is not None and session_date < cutoff:
            archivable.append((f, session_date))

    return archivable


def archive_sessions(days: int = DEFAULT_DAYS, dry_run: bool = False) -> int:
    """Move session files older than `days` days to the archive directory.

    Returns the number of files moved (or that would be moved in dry-run).
    """
    archivable = find_archivable_sessions(days)

    if not archivable:
        print(green(f"No session files older than {days} days. Nothing to archive."))
        return 0

    if not dry_run:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    moved = 0
    for filepath, session_date in archivable:
        dest = ARCHIVE_DIR / filepath.name
        if dry_run:
            print(yellow(f"[dry-run] Would move: {filepath.name} ({session_date})"))
        else:
            shutil.move(str(filepath), str(dest))
            print(f"  Archived: {filepath.name} ({session_date})")
        moved += 1

    action = "would archive" if dry_run else "archived"
    print(green(f"\n{moved} session file(s) {action} (threshold: {days} days)."))
    return moved


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Archive session logs older than a given number of days."
    )
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS,
                        help=f"Archive sessions older than this many days (default: {DEFAULT_DAYS})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be moved without making changes")
    args = parser.parse_args()

    if args.days < 1:
        parser.error("--days must be at least 1")

    archive_sessions(days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
