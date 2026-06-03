#!/usr/bin/env python3
"""Snapshot and rollback mechanism for state/ directory.

Commands:
  snapshot   Copy all state/ files into a timestamped .snapshot/ backup
  rollback   Restore state/ from the most recent snapshot
  list       Show available snapshots
  clean      Remove snapshots older than 7 days
"""
import argparse
import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

from shared import ROOT, STATE_DIR, green, yellow, red, dim

SNAPSHOT_DIR = STATE_DIR / ".snapshot"
TIMESTAMP_FMT = "%Y%m%d-%H%M%S"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _snapshot_timestamp(snapshot_path: Path) -> datetime | None:
    """Parse timestamp from a snapshot directory name.

    Handles both plain timestamps ('20260413-141500') and collision-suffixed
    names ('20260413-141500-a', '20260413-141500-b').
    """
    name = snapshot_path.name
    # Strip single-letter collision suffix if present
    if len(name) == len("20260413-141500") + 2 and name[-2] == '-' and name[-1].isalpha():
        name = name[:-2]
    try:
        return datetime.strptime(name, TIMESTAMP_FMT)
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

def _sweep_orphan_tmpdirs(dry_run: bool = False) -> None:
    """Remove .tmp-* directories under SNAPSHOT_DIR older than 1 hour."""
    if not SNAPSHOT_DIR.exists():
        return
    cutoff = datetime.now() - timedelta(hours=1)
    for item in SNAPSHOT_DIR.iterdir():
        if not item.is_dir() or not item.name.startswith(".tmp-"):
            continue
        # Parse timestamp from .tmp-<pid>-YYYYMMDD-HHMMSS
        parts = item.name.split("-")
        if len(parts) >= 4:
            ts_str = parts[-2] + "-" + parts[-1]
            try:
                ts = datetime.strptime(ts_str, TIMESTAMP_FMT)
                if ts < cutoff:
                    if dry_run:
                        print(yellow(f"[dry-run] Would sweep orphan: {item.name}"))
                    else:
                        shutil.rmtree(item)
                        print(yellow(f"Swept orphan temp dir: {item.name}"))
            except ValueError:
                pass  # unparseable name — leave alone


def cmd_snapshot(dry_run: bool = False) -> int:
    """Create a timestamped snapshot of state/ using atomic rename."""
    # Step 0: sweep orphan .tmp-* dirs from previous crashed runs
    _sweep_orphan_tmpdirs(dry_run=dry_run)

    stamp = datetime.now().strftime(TIMESTAMP_FMT)
    tmp_name = f".tmp-{os.getpid()}-{stamp}"
    tmp_dest = SNAPSHOT_DIR / tmp_name
    final_dest = SNAPSHOT_DIR / stamp
    files = _state_files()

    if not files:
        print(red("No state files found to snapshot."))
        return 1

    if dry_run:
        print(yellow(f"[dry-run] Would create snapshot at: {final_dest.relative_to(ROOT)}"))
        for f in files:
            print(f"  {dim(str(f.relative_to(STATE_DIR)))}")
        print(yellow(f"[dry-run] {len(files)} file(s) would be copied."))
        return 0

    tmp_dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    try:
        for f in files:
            rel = f.relative_to(STATE_DIR)
            target = tmp_dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
            copied += 1

        # Atomic rename: find an available final name (collision handling)
        dest = final_dest
        if dest.exists():
            for suffix in "abcdefghijklmnopqrstuvwxyz":
                candidate = SNAPSHOT_DIR / f"{stamp}-{suffix}"
                if not candidate.exists():
                    dest = candidate
                    break
            else:
                shutil.rmtree(tmp_dest)
                print(red(f"Snapshot collision: could not find free name for {stamp}"))
                return 1

        shutil.move(str(tmp_dest), str(dest))
        print(green(f"Snapshot created: {dest.relative_to(ROOT)} ({copied} files)"))
        return 0
    except BaseException:
        # Leave tmp_dest for orphan sweep; don't hide original exception
        raise


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

    # QR-S3: preserve session logs written AFTER the snapshot. STUDENT-GUIDE
    # promises "your session log stays (for transparency)" while skill-map /
    # schedule / profile revert. A session log present now but absent from the
    # snapshot is newer than it — keep it instead of unlinking. (Logs already
    # in the snapshot are restored normally below.)
    snapshot_rel = {
        f.relative_to(latest) for f in latest.rglob("*") if f.is_file()
    }

    def _is_session_log(rel: Path) -> bool:
        # state/sessions/<date>.yaml — NOT sessions/archive/* or other subdirs
        return (
            len(rel.parts) == 2
            and rel.parts[0] == "sessions"
            and rel.suffix == ".yaml"
        )

    # Remove current state files (except .snapshot/ and preserved session logs)
    preserved = 0
    for f in _state_files():
        rel = f.relative_to(STATE_DIR)
        if _is_session_log(rel) and rel not in snapshot_rel:
            preserved += 1
            continue
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

    msg = f"Rolled back to snapshot {label} ({restored} files restored)"
    if preserved:
        msg += f"; {preserved} newer session log(s) preserved"
    print(green(msg))
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
    _sweep_orphan_tmpdirs(dry_run=dry_run)
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
