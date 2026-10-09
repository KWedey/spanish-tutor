#!/usr/bin/env python3
"""Recompute derived pedagogy metrics from authoritative state.

Wires the previously-dead calibration counters the audit found (QR-P1/QR-P2):
the schema/system-design.md say these are "incremented by post-session.sh" and
read by the decision engine / CLAUDE.md calibration, but nothing ever wrote them
— so the regression-escalation ladder and the too-easy/too-hard calibration
were keyed on counters frozen at 0.

This script derives them DETERMINISTICALLY from state (skill-map + session logs),
not from the LLM, and is invoked by post-session.sh after the session log
validates. Run once per session (the regression counter is a per-session tally).

Recomputed:
  - skill-map: regression_session_count per grammar concept (grammar-only, per
      the schema + system-design.md — vocabulary_entry_template has no such field)
      regressed status  -> += 1 (consecutive sessions in regression)
      acquired/automatic -> reset to 0 (re-acquired)
      (other statuses left untouched)
  - system-health:
      concepts_requiring_reteach_total = # grammar+vocab concepts 'regressed'
      sessions_rated_too_easy_30d / sessions_rated_too_hard_30d =
          # session logs within 30 days whose session_difficulty_rating matches

Usage:
  python3 scripts/recompute-metrics.py YYYY-MM-DD
"""
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

from shared import STATE_DIR, atomic_write, leading_header, load_yaml_strict

_REGRESSED = "regressed"
_REACQUIRED = ("acquired", "automatic")
_REGRESSION_CATEGORIES = ("grammar", "vocabulary")  # reteach total spans both
_REGRESSION_COUNT_CATEGORIES = ("grammar",)  # regression_session_count is grammar-only (P2-t)
_WINDOW_DAYS = 30


def recompute_regression_counts(skill_map: dict) -> int:
    """Update regression_session_count in place. Returns concepts touched."""
    touched = 0
    for category in _REGRESSION_COUNT_CATEGORIES:
        entries = skill_map.get(category)
        if not isinstance(entries, dict):
            continue
        for entry in entries.values():
            if not isinstance(entry, dict):
                continue
            status = entry.get("status")
            if status == _REGRESSED:
                entry["regression_session_count"] = (
                    entry.get("regression_session_count") or 0
                ) + 1
                touched += 1
            elif status in _REACQUIRED:
                if entry.get("regression_session_count"):
                    entry["regression_session_count"] = 0
                    touched += 1
    return touched


def count_reteach(skill_map: dict) -> int:
    """# concepts currently 'regressed' across grammar + vocabulary."""
    total = 0
    for category in _REGRESSION_CATEGORIES:
        entries = skill_map.get(category)
        if not isinstance(entries, dict):
            continue
        total += sum(
            1 for e in entries.values()
            if isinstance(e, dict) and e.get("status") == _REGRESSED
        )
    return total


def count_difficulty_ratings(sessions_dir: Path, today: date) -> tuple[int, int]:
    """(too_easy, too_hard) over session logs within _WINDOW_DAYS of `today`.

    Includes archive/: archiving is by age from the real date, so a backfilled
    `today` can have its whole window there already.
    """
    if not sessions_dir.exists():
        return (0, 0)
    cutoff = today - timedelta(days=_WINDOW_DAYS)
    too_easy = too_hard = 0
    logs = {f.stem: f for f in (sessions_dir / "archive").glob("*.yaml")}
    logs.update({f.stem: f for f in sessions_dir.glob("*.yaml")})
    for f in logs.values():
        # window by filename date (YYYY-MM-DD) — cheap and avoids parsing all logs
        try:
            log_date = date.fromisoformat(f.stem)
        except ValueError:
            continue
        if not (cutoff <= log_date <= today):
            continue
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        rating = data.get("session_difficulty_rating")
        if rating == "too-easy":
            too_easy += 1
        elif rating == "too-hard":
            too_hard += 1
    return (too_easy, too_hard)


def _write_yaml_preserving_header(path: Path, data: dict) -> None:
    header = leading_header(path.read_text(encoding="utf-8")) if path.exists() else ""
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    atomic_write(path, header + body)


def recompute(state_dir: Path, today: date) -> dict:
    """Recompute and persist metrics. Returns a summary dict (for logging/tests)."""
    sm_path = state_dir / "skill-map.yaml"
    health_path = state_dir / "system-health.yaml"
    summary = {"regression_touched": 0, "reteach_total": 0,
               "too_easy_30d": 0, "too_hard_30d": 0}

    if sm_path.exists():
        # Write-back path: load strictly so a corrupt skill-map raises instead
        # of collapsing to {} and erasing every concept on the write below (A3).
        skill_map = load_yaml_strict(sm_path)
        summary["regression_touched"] = recompute_regression_counts(skill_map)
        reteach = count_reteach(skill_map)
        summary["reteach_total"] = reteach
        _write_yaml_preserving_header(sm_path, skill_map)
    else:
        reteach = 0

    too_easy, too_hard = count_difficulty_ratings(state_dir / "sessions", today)
    summary["too_easy_30d"] = too_easy
    summary["too_hard_30d"] = too_hard

    if health_path.exists():
        # Write-back path: strict load so a corrupt system-health raises rather
        # than being silently overwritten with just the three counters (A3).
        health = load_yaml_strict(health_path)
        health["concepts_requiring_reteach_total"] = reteach
        health["sessions_rated_too_easy_30d"] = too_easy
        health["sessions_rated_too_hard_30d"] = too_hard
        _write_yaml_preserving_header(health_path, health)

    return summary


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/recompute-metrics.py YYYY-MM-DD", file=sys.stderr)
        return 2
    try:
        today = date.fromisoformat(sys.argv[1])
    except ValueError:
        print(f"Invalid date: {sys.argv[1]} (expected YYYY-MM-DD)", file=sys.stderr)
        return 2
    summary = recompute(STATE_DIR, today)
    print(
        "Metrics recomputed: "
        f"{summary['regression_touched']} regression counter(s) updated, "
        f"reteach_total={summary['reteach_total']}, "
        f"too_easy_30d={summary['too_easy_30d']}, "
        f"too_hard_30d={summary['too_hard_30d']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
