#!/usr/bin/env python3
"""Snapshot and rollback mechanism for state/ directory.

Commands:
  snapshot   Copy all state/ files into a timestamped .snapshot/ backup
  rollback   Restore state/ from the most recent snapshot
  list       Show available snapshots
  clean      Remove snapshots older than 7 days
"""
import argparse
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

from shared import ROOT, STATE_DIR

# ---------------------------------------------------------------------------
# Color helpers (same pattern as init-student.py)
# ---------------------------------------------------------------------------

_C = sys.stdout.isatty()
green = lambda t: f"\033[32m{t}\033[0m" if _C else t
yellow = lambda t: f"\033[33m{t}\033[0m" if _C else t
red = lambda t: f"\033[31m{t}\033[0m" if _C else t
dim = lambda t: f"\033[2m{t}\033[0m" if _C else t

SNAPSHOT_DIR = STATE_DIR / ".snapshot"
TIMESTAMP_FMT = "%Y%m%d-%H%M%S"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _snapshot_timestamp(snapshot_path: Path) -> datetime | None:
    """Parse timestamp from a snapshot directory name."""
    try:
        return datetime.strptime(snapshot_path.name, TIMESTAMP_FMT)
    except ValueError:
        return None


def _list_snapshots() -> list[Path]:
    """Return snapshot directories sorted oldest-first."""
    if not SNAPSHOT_DIR.exists():
        return []
    return sorted(
        (d for d in SNAPSHOT_DIR.iterdir()
         if d.is_dir() and _snapshot_timestamp(d) is not None),
        key=lambda d: d.name,
    )


def _state_files() -> list[Path]:
    """Return all files in state/ that should be snapshotted.

    Includes YAML files at the top level and everything inside subdirectories
    (sessions/, summaries/, etc), but excludes the .snapshot/ directory itself.
    """
    files = []
    for item in sorted(STATE_DIR.rglob("*")):
        if item.is_file() and ".snapshot" not in item.parts:
            files.append(item)
    return files


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_snapshot(dry_run: bool = False) -> int:
    """Create a timestamped snapshot of state/."""
    stamp = datetime.now().strftime(TIMESTAMP_FMT)
    dest = SNAPSHOT_DIR / stamp
    files = _state_files()

    if not files:
        print(red("No state files found to snapshot."))
        return 1

    if dry_run:
        print(yellow(f"[dry-run] Would create snapshot at: {dest.relative_to(ROOT)}"))
        for f in files:
            print(f"  {dim(str(f.relative_to(STATE_DIR)))}")
        print(yellow(f"[dry-run] {len(files)} file(s) would be copied."))
        return 0

    dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    for f in files:
        rel = f.relative_to(STATE_DIR)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
        copied += 1

    print(green(f"Snapshot created: {dest.relative_to(ROOT)} ({copied} files)"))
    return 0


def cmd_rollback(dry_run: bool = False) -> int:
    """Restore state/ from the most recent snapshot."""
    snapshots = _list_snapshots()
    if not snapshots:
        print(red("No snapshots available to rollback to."))
        return 1

    latest = snapshots[-1]
    ts = _snapshot_timestamp(latest)
    label = ts.strftime("%Y-%m-%d %H:%M:%S") if ts else latest.name

    if dry_run:
        print(yellow(f"[dry-run] Would rollback state/ from snapshot: {label}"))
        files = list(latest.rglob("*"))
        for f in files:
            if f.is_file():
                print(f"  {dim(str(f.relative_to(latest)))}")
        return 0

    # Remove current state files (except .snapshot/)
    for f in _state_files():
        f.unlink()

    # Copy snapshot contents back into state/
    restored = 0
    for f in sorted(latest.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(latest)
        target = STATE_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
        restored += 1

    print(green(f"Rolled back to snapshot {label} ({restored} files restored)"))
    return 0


def cmd_list() -> int:
    """Show available snapshots."""
    snapshots = _list_snapshots()
    if not snapshots:
        print(yellow("No snapshots found."))
        return 0

    print(f"{'Snapshot':<20} {'Files':>6}  {'Created'}")
    print("-" * 50)
    for snap in snapshots:
        ts = _snapshot_timestamp(snap)
        label = ts.strftime("%Y-%m-%d %H:%M:%S") if ts else snap.name
        count = sum(1 for f in snap.rglob("*") if f.is_file())
        print(f"{snap.name:<20} {count:>6}  {label}")

    print(f"\n{len(snapshots)} snapshot(s) available.")
    return 0


def cmd_clean(dry_run: bool = False, max_age_days: int = 7) -> int:
    """Remove snapshots older than max_age_days."""
    snapshots = _list_snapshots()
    cutoff = datetime.now() - timedelta(days=max_age_days)
    to_remove = []

    for snap in snapshots:
        ts = _snapshot_timestamp(snap)
        if ts is not None and ts < cutoff:
            to_remove.append(snap)

    if not to_remove:
        print(green("No snapshots older than 7 days. Nothing to clean."))
        return 0

    for snap in to_remove:
        ts = _snapshot_timestamp(snap)
        label = ts.strftime("%Y-%m-%d %H:%M:%S") if ts else snap.name
        if dry_run:
            print(yellow(f"[dry-run] Would remove: {snap.name} ({label})"))
        else:
            shutil.rmtree(snap)
            print(f"Removed: {snap.name} ({label})")

    action = "would remove" if dry_run else "removed"
    print(green(f"\n{len(to_remove)} snapshot(s) {action}."))
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Snapshot and rollback mechanism for state/ directory."
    )
    parser.add_argument("command", choices=["snapshot", "rollback", "list", "clean"],
                        help="Action to perform")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would happen without making changes")
    args = parser.parse_args()

    handlers = {
        "snapshot": lambda: cmd_snapshot(dry_run=args.dry_run),
        "rollback": lambda: cmd_rollback(dry_run=args.dry_run),
        "list": lambda: cmd_list(),
        "clean": lambda: cmd_clean(dry_run=args.dry_run),
    }

    sys.exit(handlers[args.command]())


if __name__ == "__main__":
    main()
