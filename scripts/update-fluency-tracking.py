#!/usr/bin/env python3
"""Persist fluency-day tracking after a session (C1 wiring).

The router (route_session._is_fluency_day) reads `fluency_days_this_week` and
`last_fluency_day` from schedule.yaml at session START to decide whether today
is a fluency day. This script is the WRITER: post-session.sh runs it at session
END. On a fluency session it increments the week-aware counter and stamps
last_fluency_day; on any other session type it is a no-op.

Week-awareness: the stored counter only counts fluency days within the ISO week
of last_fluency_day. The router treats a counter whose last_fluency_day is in a
prior week as 0, so the reset is implicit — this writer just continues the count
within a week and restarts it on the first fluency day of a new week. That
split keeps the reset visible to the router (which reads before this writer
runs) without a separate reset pass.
"""
import sys
from datetime import date
from pathlib import Path

import yaml

from shared import STATE_DIR, atomic_write, leading_header


def same_iso_week(a: date, b: date) -> bool:
    """True if two dates fall in the same ISO (year, week)."""
    return a.isocalendar()[:2] == b.isocalendar()[:2]


def update_fluency_tracking(date_str: str, state_dir: Path) -> dict | None:
    """Increment fluency tracking if the session on date_str was a fluency day.

    Returns the updated schedule dict on a write, or None when nothing changed
    (non-fluency session, missing session log, or missing schedule).
    """
    today = date.fromisoformat(date_str)
    state_dir = Path(state_dir)

    session_log = state_dir / "sessions" / f"{date_str}.yaml"
    if not session_log.exists():
        return None
    log = yaml.safe_load(session_log.read_text(encoding="utf-8")) or {}
    if not isinstance(log, dict) or log.get("session_type") != "fluency":
        return None

    schedule_path = state_dir / "schedule.yaml"
    if not schedule_path.exists():
        return None
    text = schedule_path.read_text(encoding="utf-8")
    schedule = yaml.safe_load(text) or {}
    if not isinstance(schedule, dict):
        return None

    last_raw = schedule.get("last_fluency_day")
    # Idempotent: a date can host at most one session, so if today is already
    # stamped the fluency day was counted on a prior run — don't double-count.
    if last_raw == date_str:
        return None
    last_fluency = None
    if last_raw:
        try:
            last_fluency = date.fromisoformat(str(last_raw))
        except ValueError:
            last_fluency = None

    if last_fluency is not None and same_iso_week(last_fluency, today):
        try:
            base = int(schedule.get("fluency_days_this_week") or 0)
        except (TypeError, ValueError):
            base = 0
    else:
        base = 0  # first fluency day of a new ISO week

    schedule["fluency_days_this_week"] = base + 1
    schedule["last_fluency_day"] = date_str

    body = yaml.safe_dump(schedule, sort_keys=False, allow_unicode=True)
    atomic_write(schedule_path, leading_header(text) + body)
    return schedule


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/update-fluency-tracking.py YYYY-MM-DD", file=sys.stderr)
        return 2
    try:
        date.fromisoformat(sys.argv[1])
    except ValueError:
        print(f"Invalid date: {sys.argv[1]} (expected YYYY-MM-DD)", file=sys.stderr)
        return 2
    result = update_fluency_tracking(sys.argv[1], STATE_DIR)
    if result is not None:
        print(f"fluency tracking updated: fluency_days_this_week="
              f"{result['fluency_days_this_week']}, last_fluency_day={result['last_fluency_day']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
