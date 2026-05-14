"""ROUTE-FOLLOWUP-01: End-to-end session-type routing harness.

Mirrors CLAUDE.md Step 3 routing table exactly, row by row.
Branch order is load-bearing — do not reorder.

Canonical return values:
  first-session
  onboarding
  onboarding-with-return-overlay
  return
  maintenance
  maintenance-with-weekly-review
  weekly-review
  sprint
  placement-validation
  fluency
  standard
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

SessionType = str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    """Load a YAML file; return empty dict if missing or unparseable."""
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _gap_days(last_session_date: str | None, today: date, sessions_dir: Path) -> int:
    """Return the number of days since the last session.

    Priority order (mirrors CLAUDE.md Step 3 gap-detection note):
      1. last_session_date from schedule.yaml (ISO 8601 string)
      2. Most-recent *.yaml filename in sessions_dir
      3. 0 (no gap detectable)
    """
    if last_session_date:
        try:
            last = date.fromisoformat(str(last_session_date))
            return (today - last).days
        except ValueError:
            pass

    # Fallback: most-recent session log filename (YYYY-MM-DD.yaml)
    session_files = sorted(sessions_dir.glob("*.yaml"), reverse=True)
    if session_files:
        stem = session_files[0].stem  # "2026-05-13"
        try:
            last = date.fromisoformat(stem)
            return (today - last).days
        except ValueError:
            pass

    return 0


def _session_logs_exist(sessions_dir: Path) -> bool:
    """True if at least one *.yaml file exists in sessions_dir."""
    return any(sessions_dir.glob("*.yaml"))


# Fixed weekday name table — locale-independent, English-canonical.
# Indexed by `today.weekday()` (Monday=0..Sunday=6). Used in preference to
# `strftime("%A")` which is locale-aware: on a Spanish-locale system the latter
# would return "miércoles" and never match the project's English-capitalized
# weekly_review_day contract.
_WEEKDAY_NAMES_EN = (
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
)


def _is_weekly_review_day(profile: dict, today: date) -> bool:
    """True if today's weekday matches weekly_review_day (case-insensitive, stripped).

    An empty or missing weekly_review_day means no weekly-review day configured.
    Comparison is against a fixed English weekday table so the routing is
    deterministic regardless of system locale.
    """
    raw = profile.get("weekly_review_day", "") or ""
    normalized = raw.strip().capitalize()
    if not normalized:
        return False
    return _WEEKDAY_NAMES_EN[today.weekday()] == normalized


# Fluency-day target per phase (CLAUDE.md Step 2.9 + fluency-activities.md).
# Phase A: never (foundation work). B/C/D: 1/2/3 fluency sessions per week.
# Keyed by the canonical schema-enum strings from schemas/schedule.schema.yaml
# (NOT the bare letters — that drift caused the audit C-1/C-2 bugs).
_FLUENCY_DAYS_PER_PHASE = {
    "B-conversational": 1,
    "C-intermediate": 2,
    "D-advanced": 3,
}


def _is_fluency_day(schedule: dict, today: date) -> bool:
    """True if today qualifies as a fluency day per CLAUDE.md Step 2.9.

    Conditions (all must hold):
      - current_phase is B/C/D (canonical "X-name" form per schedule.schema.yaml)
      - phase-specific weekly fluency target > 0
      - fluency_days_this_week count < weekly target
      - today is not consecutive with last_fluency_day

    Reads `fluency_days_this_week` directly from schedule.yaml — the explicit
    counter the post-session.sh ritual maintains. The audit (C-1/C-2) caught
    that the previous version read a non-existent `fluency_days_per_week`
    field AND compared against bare-letter phase strings the schema never
    writes, leaving the predicate permanently False in production.
    """
    current_phase = schedule.get("current_phase") or ""
    target = _FLUENCY_DAYS_PER_PHASE.get(current_phase, 0)
    if target <= 0:
        return False

    fluency_this_week = int(schedule.get("fluency_days_this_week") or 0)
    if fluency_this_week >= target:
        return False

    last_fluency_raw = schedule.get("last_fluency_day")
    if last_fluency_raw:
        try:
            last_fluency = date.fromisoformat(str(last_fluency_raw))
        except ValueError:
            return True  # malformed date — don't block the routing
        if (today - last_fluency).days <= 1:
            return False
    return True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def route_session(
    state_dir: Path,
    today: date | None = None,
) -> SessionType:
    """Decide today's session type from on-disk state.

    Reads:
      - {state_dir}/learner-profile.yaml  — weekly_review_day, autonomy_level
      - {state_dir}/schedule.yaml         — last_session_date, onboarding_complete,
        current_onboarding_session, sprint.active, placement_validation.active,
        placement_validation.sessions_completed, fluency_days_per_week,
        last_fluency_day, current_phase
      - {state_dir}/sessions/*.yaml       — existence + most-recent filename

    Returns the session_type CLAUDE.md Step 3 routing table would select.
    Branch order mirrors Step 3 row order exactly.
    """
    if today is None:
        today = date.today()

    state_dir = Path(state_dir)
    sessions_dir = state_dir / "sessions"

    profile = _load_yaml(state_dir / "learner-profile.yaml")
    schedule = _load_yaml(state_dir / "schedule.yaml")

    # ------------------------------------------------------------------
    # Row 1: No session logs exist → first-session
    # ------------------------------------------------------------------
    if not _session_logs_exist(sessions_dir):
        return "first-session"

    # ------------------------------------------------------------------
    # Row 2: onboarding_complete is false → onboarding
    #   ROUTE-01 overlay: gap >= 3 days → onboarding-with-return-overlay
    # ------------------------------------------------------------------
    if not schedule.get("onboarding_complete", True):
        last_session_date = schedule.get("last_session_date")
        gap = _gap_days(last_session_date, today, sessions_dir)
        if gap >= 3:
            return "onboarding-with-return-overlay"
        return "onboarding"

    # ------------------------------------------------------------------
    # Row 3: Gap >= 3 days → return
    #   ROUTE-02: takes priority over weekly review when both match
    # ------------------------------------------------------------------
    last_session_date = schedule.get("last_session_date")
    gap = _gap_days(last_session_date, today, sessions_dir)
    if gap >= 3:
        return "return"

    # ------------------------------------------------------------------
    # Row 4: autonomy_level == "maintenance" → maintenance
    #   ROUTE-07 overlay: today is weekly_review_day → maintenance-with-weekly-review
    # ------------------------------------------------------------------
    if profile.get("autonomy_level") == "maintenance":
        if _is_weekly_review_day(profile, today):
            return "maintenance-with-weekly-review"
        return "maintenance"

    # ------------------------------------------------------------------
    # Row 5: today's day-of-week matches weekly_review_day → weekly-review
    # ------------------------------------------------------------------
    if _is_weekly_review_day(profile, today):
        return "weekly-review"

    # ------------------------------------------------------------------
    # Row 6: sprint.active is true → sprint
    #   ROUTE-03 override: placement_validation.active + sessions_completed < 3
    #   → placement-validation (override sprint)
    # ------------------------------------------------------------------
    sprint = schedule.get("sprint") or {}
    if sprint.get("active", False):
        pv = schedule.get("placement_validation") or {}
        if pv.get("active", False) and pv.get("sessions_completed", 0) < 3:
            return "placement-validation"
        return "sprint"

    # ------------------------------------------------------------------
    # Row 7: Phase B+ AND today is a fluency day → fluency
    # ------------------------------------------------------------------
    if _is_fluency_day(schedule, today):
        return "fluency"

    # ------------------------------------------------------------------
    # Row 8: otherwise → standard
    # ------------------------------------------------------------------
    return "standard"


# ---------------------------------------------------------------------------
# CLI entry point  (useful for canary protocol — 08-08)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/route_session.py <state_dir>", file=sys.stderr)
        sys.exit(1)
    result = route_session(Path(sys.argv[1]))
    print(result)
