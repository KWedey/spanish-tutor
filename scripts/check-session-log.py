#!/usr/bin/env python3
"""Check that a session log has all fields expected for its session type.

`validate-state.py` checks required fields from the schema. This script is
stricter: it enforces the ``expected`` set for a given session type. Those
fields are technically optional in the schema (since not every session type
needs them), but if a standard session is missing ``decision_engine_trace``
or a weekly review is missing ``weekly_summary_written``, that is silent
protocol drift — exactly what this check catches.

Usage:
    python3 scripts/check-session-log.py 2026-04-11
    python3 scripts/check-session-log.py 2026-04-11 --strict   # warn → fail

Exit codes:
    0  — all expected fields present (or only warnings in non-strict mode)
    1  — missing expected fields / invalid YAML / file missing
"""
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from shared import ROOT, STATE_DIR

_C = sys.stdout.isatty()
green = lambda t: f"\033[32m{t}\033[0m" if _C else t
yellow = lambda t: f"\033[33m{t}\033[0m" if _C else t
red = lambda t: f"\033[31m{t}\033[0m" if _C else t
dim = lambda t: f"\033[2m{t}\033[0m" if _C else t


# ---------------------------------------------------------------------------
# Expected fields by session type
# ---------------------------------------------------------------------------
#
# Keys here are field dotted-paths. A dotted path like
# "learner_observations.mood" means "the nested key mood inside
# learner_observations".
#
# These are fields the tutor agent is SUPPOSED to populate for a given
# session type. Missing them indicates the agent skipped a post-session
# protocol step — which is the single biggest risk with a 19-step checklist.
#
# Fields shared across all session types live in BASE_EXPECTED.

BASE_EXPECTED = [
    "date",
    "session_number",
    "duration_minutes",
    "session_type",
    "session_status",
    "learner_energy",
    "session_activities",
    "learner_observations.mood",
    "learner_observations.engagement",
]

STANDARD_EXPECTED = BASE_EXPECTED + [
    "assignment_review",
    "skill_map_updates",
    "assignments",
    "decision_engine_trace.selected_primary",
    "decision_engine_trace.candidates_scored",
    "session_difficulty_rating",
    "next_session.recommended_focus",
    "next_session.session_type",
]

WEEKLY_REVIEW_EXPECTED = BASE_EXPECTED + [
    "assignment_review",
    "skill_map_updates",
    "next_session.recommended_focus",
]

PHASE_TRANSITION_EXPECTED = BASE_EXPECTED + [
    "assignment_review",
    "skill_map_updates",
    "decision_engine_trace.selected_primary",
    "next_session.recommended_focus",
]

RETURN_EXPECTED = BASE_EXPECTED + [
    "gap_days",
    "skill_map_updates",
    "assignments",
    "next_session.recommended_focus",
]

MICRO_EXPECTED = BASE_EXPECTED + [
    "skill_map_updates",
]

FIRST_SESSION_EXPECTED = BASE_EXPECTED + [
    "assessment",
    "skill_map_updates",
]

ONBOARDING_EXPECTED = BASE_EXPECTED + [
    "skill_map_updates",
    "assignments",
    "next_session.recommended_focus",
]

SPRINT_EXPECTED = BASE_EXPECTED + [
    "assignments",
    "skill_map_updates",
    "next_session.recommended_focus",
]

FLUENCY_EXPECTED = BASE_EXPECTED + [
    "skill_map_updates",
    "assignments",
    "next_session.recommended_focus",
]

EXPECTED_BY_TYPE: dict[str, list[str]] = {
    "standard": STANDARD_EXPECTED,
    "weekly-review": WEEKLY_REVIEW_EXPECTED,
    "phase-transition": PHASE_TRANSITION_EXPECTED,
    "return": RETURN_EXPECTED,
    "micro": MICRO_EXPECTED,
    "first-session": FIRST_SESSION_EXPECTED,
    "onboarding": ONBOARDING_EXPECTED,
    "sprint": SPRINT_EXPECTED,
    "fluency": FLUENCY_EXPECTED,
}

# Fields that MAY be empty when applicable is uncertain. Agent should still
# populate them deliberately (even if empty list), but absence of the key at
# all means the agent skipped the step.


# ---------------------------------------------------------------------------
# Field lookup
# ---------------------------------------------------------------------------

def get_nested(data: dict, dotted_path: str) -> tuple[bool, object]:
    """Walk a dotted path. Returns (present, value)."""
    parts = dotted_path.split(".")
    current: object = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def is_empty(value: object) -> bool:
    """Empty means: None, empty string, empty list, empty dict."""
    if value is None:
        return True
    if isinstance(value, (str, list, dict)) and len(value) == 0:
        return True
    return False


# ---------------------------------------------------------------------------
# ENGINE Phase 4: Conditional recasts enforcement (D-06)
# ---------------------------------------------------------------------------

# Backward compatibility: session logs before this date were written without
# the recasts field. Skip conditional enforcement for pre-Phase-4 logs.
PHASE_4_CUTOFF = "2026-04-20"


def check_recasts_required(data: dict) -> bool:
    """D-06: recasts field is required when session contained
    Stage 3/4 activities, fluency type, or conversation practice."""
    # Short-circuit: fluency sessions always require recasts (Pitfall 6)
    if data.get("session_type") == "fluency":
        return True
    activities = data.get("session_activities") or []
    for a in activities:
        if not isinstance(a, dict):
            continue
        stage = (a.get("stage") or "").lower()
        if "stage-3" in stage or "stage-4" in stage:
            return True
        atype = (a.get("type") or "").lower()
        if "conversation" in atype or "role-play" in atype or "storytelling" in atype:
            return True
    # Fallback: scan free-text fields for "recast" substring
    for a in activities:
        if not isinstance(a, dict):
            continue
        for key in ("notes", "observations"):
            if "recast" in str(a.get(key, "")).lower():
                return True
    return False


# ---------------------------------------------------------------------------
# LOAD Phase 5: Conditional homework_load_rating enforcement (D-10 / Pitfall 5)
# ---------------------------------------------------------------------------

def check_homework_load_rating_required(data: dict) -> bool:
    """D-10/Pitfall-5: homework_load_rating is required when there was a PRIOR
    session with homework. Exempts first-session (no prior homework) and
    onboarding session_number=1 (still the first real session).

    Also exempts special session types (weekly-review, phase-transition, return,
    micro) — these have their own purpose and are not budget-gated daily sessions.
    """
    stype = (data.get("session_type") or "").lower()
    if stype in ("first-session", "weekly-review", "phase-transition", "return", "micro"):
        return False
    try:
        snum = int(data.get("session_number") or 0)
    except (TypeError, ValueError):
        return False
    if stype == "onboarding" and snum <= 1:
        return False
    return snum >= 2


# ---------------------------------------------------------------------------
# LOAD Phase 5: Homework budget enforcement (D-07 / Pitfall 1)
# ---------------------------------------------------------------------------

# Backward compatibility: session logs before this date were written without
# the study_time_budget in schedule.yaml. Grandfather pre-LOAD logs.
PHASE_5_CUTOFF = "2026-04-21"


def _load_schedule() -> dict | None:
    """Load state/schedule.yaml, returning None on missing-file or YAML error."""
    schedule_path = STATE_DIR / "schedule.yaml"
    if not schedule_path.exists():
        return None
    try:
        with schedule_path.open() as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError:
        return None


def compute_assignment_budget_total(data: dict) -> int:
    """Sum the estimated_minutes field across the per-log homework list.

    Pitfall 1 note: the authoritative per-item field name is estimated_minutes.
    The neighbor field on next_session (a separate top-level key, NOT the
    per-log list) is named estimated_duration; that path is unrelated to this
    sum. Reference: docs/session-log-example.yaml L109/L119/L129 and
    docs/system-design.md L807.
    """
    total = 0
    for a in data.get("assignments") or []:
        if isinstance(a, dict):
            total += int(a.get("estimated_minutes") or 0)
    return total


def check_assignment_budget(data: dict, schedule: dict | None) -> tuple[str, str, int]:
    """D-07: Returns (level, message, total_minutes). level in {OK, WARN, FAIL}.

    Reads study_time_budget.{daily_target, daily_maximum, today_stretch} from schedule.

    Ordering:
    - Pre-PHASE_5_CUTOFF -> OK (grandfathered, Pitfall 4)
    - total == 0 -> OK (no assignments)
    - schedule unreadable -> FAIL
    - study_time_budget missing or not a dict -> FAIL (required after session 1, D-06)
    - total > daily_maximum + today_stretch -> FAIL
    - total > daily_target -> WARN
    - else -> OK
    """
    session_date = str(data.get("date", ""))
    if session_date < PHASE_5_CUTOFF:
        return ("OK", "pre-LOAD session — grandfathered", 0)

    total = compute_assignment_budget_total(data)
    if total == 0:
        return ("OK", "no homework assignments — budget not applicable", 0)

    if not isinstance(schedule, dict):
        return ("FAIL", "schedule.yaml unreadable — cannot enforce study_time_budget", total)
    budget = schedule.get("study_time_budget")
    if not isinstance(budget, dict):
        return ("FAIL",
                "study_time_budget missing from schedule.yaml "
                "(required after first-session per D-06)",
                total)

    d_max = int(budget.get("daily_maximum") or 0)
    stretch = int(budget.get("today_stretch") or 0)
    d_tgt = int(budget.get("daily_target") or 0)

    ceiling = d_max + stretch
    if total > ceiling:
        return ("FAIL",
                f"homework sum {total}min > daily_maximum({d_max}) + today_stretch({stretch})",
                total)
    if total > d_tgt:
        return ("WARN",
                f"homework sum {total}min > daily_target({d_tgt}) (<= max+stretch OK)",
                total)
    return ("OK", f"homework sum {total}min within daily_target", total)


def _append_load_adjustment_warn(session_date: str, total: int,
                                 schedule: dict | None, message: str) -> None:
    """D-07/A7: Append a WARN-tier entry to state/system-health.yaml > load_adjustments.

    Separate from auto_fixes because the intent differs (learner-load signal vs
    validator-driven data repair). Shape mirrors auto_fixes (Phase 3 D-03 pattern).
    """
    health_path = STATE_DIR / "system-health.yaml"
    if not health_path.exists():
        # Don't fabricate system-health.yaml; if it's absent the WARN is still printed.
        return
    try:
        with health_path.open() as f:
            health = yaml.safe_load(f) or {}
    except yaml.YAMLError:
        return
    budget = (schedule or {}).get("study_time_budget") or {}
    entry = {
        "date": session_date,
        "level": "WARN",
        "homework_sum": total,
        "daily_target": int(budget.get("daily_target") or 0),
        "daily_maximum": int(budget.get("daily_maximum") or 0),
        "today_stretch": int(budget.get("today_stretch") or 0),
        "message": message,
        "detected_by": "check-session-log.py:check_assignment_budget",
    }
    health.setdefault("load_adjustments", []).append(entry)
    try:
        with health_path.open("w") as f:
            yaml.safe_dump(health, f, sort_keys=False, allow_unicode=True)
    except OSError:
        return


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def check_log(date: str, strict: bool) -> int:
    log_path = STATE_DIR / "sessions" / f"{date}.yaml"

    if not log_path.exists():
        print(red(f"FAIL: session log not found: {log_path.relative_to(ROOT)}"))
        return 1

    try:
        with log_path.open() as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(red(f"FAIL: invalid YAML in {log_path.relative_to(ROOT)}:"))
        print(red(f"  {e}"))
        return 1

    if not isinstance(data, dict):
        print(red(f"FAIL: {log_path.relative_to(ROOT)} is not a YAML mapping"))
        return 1

    session_type = data.get("session_type", "")
    if not session_type:
        print(red("FAIL: session_type field is missing or empty"))
        return 1

    # Derive session_date once — used by both LOAD-03 budget enforcement and
    # ENGINE-03/D-06 conditional recasts enforcement below.
    session_date = str(data.get("date", ""))

    # LOAD-03/D-07: Homework-budget enforcement (Phase 5). Runs BEFORE the
    # EXPECTED_BY_TYPE scan and the early-return so that a session whose
    # protocol fields are all populated but whose homework sum exceeds
    # study_time_budget.daily_maximum + today_stretch is still correctly
    # blocked. Mirrors the WR-01 precedent (commit e273529) that moved the
    # recasts check before the early-return.
    if session_date >= PHASE_5_CUTOFF:
        schedule = _load_schedule()
        level, msg, total = check_assignment_budget(data, schedule)
        if level == "FAIL":
            print(red(f"FAIL: {msg}"))
            return 1
        if level == "WARN":
            print(yellow(f"WARN: {msg}"))
            _append_load_adjustment_warn(session_date, total, schedule, msg)

    # LOAD-04/D-10/Pitfall-5: Conditional homework_load_rating enforcement.
    # Retrospective capture: the tutor records the LEARNER's rating of the
    # PRIOR session's homework load in today's session log during the Review
    # & Warm-up. Required on post-cutoff sessions that had a prior session
    # with homework (see check_homework_load_rating_required for the exempt
    # list). Out-of-range enum values are caught by the schema-driven enum
    # loop in validate-state.py check_session_logs — no duplicate check here.
    if session_date >= PHASE_5_CUTOFF and check_homework_load_rating_required(data):
        if "homework_load_rating" not in data:
            print(red("FAIL: homework_load_rating is required for post-LOAD "
                       "sessions that had prior homework (D-10). "
                       "Ask the learner: 'How did the homework load feel — "
                       "too much, just right, or too light?'"))
            return 1
        # The key is present. Its value may be null/None (learner declined)
        # which is a valid enum option per D-10; out-of-range string values
        # are caught by the schema-driven enum loop in validate-state.py.

    expected = EXPECTED_BY_TYPE.get(session_type)
    if expected is None:
        print(yellow(f"WARN: unknown session_type '{session_type}' — skipping expected-field check"))
        return 0

    missing = []
    empty_fields = []
    for path in expected:
        present, value = get_nested(data, path)
        if not present:
            missing.append(path)
        elif is_empty(value):
            empty_fields.append(path)

    # ENGINE-03/D-06: Conditional recasts enforcement (with backward-compat date guard)
    # Must run before the early-return so that a session with all expected
    # fields populated but missing a conditionally-required 'recasts' field
    # is correctly caught as a failure.
    if session_date >= PHASE_4_CUTOFF and check_recasts_required(data) and "recasts" not in data:
        missing.append("recasts")

    # Report
    print(dim(f"Checking {log_path.relative_to(ROOT)} ({session_type})"))
    print(dim(f"  Expected fields: {len(expected)}"))

    if not missing and not empty_fields:
        print(green(f"PASS: all {len(expected)} expected fields populated"))
        return 0

    if missing:
        print(red(f"FAIL: {len(missing)} expected field(s) missing:"))
        for path in missing:
            if path == "recasts":
                print(red(f"  - {path} (required for Stage 3/4 / fluency / conversation -- D-06)"))
            else:
                print(red(f"  - {path}"))

    if empty_fields:
        severity = red("FAIL") if strict else yellow("WARN")
        print(f"{severity}: {len(empty_fields)} expected field(s) present but empty:")
        for path in empty_fields:
            label = red(f"  - {path}") if strict else yellow(f"  - {path}")
            print(label)

    if missing or (strict and empty_fields):
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check a session log for protocol compliance (all expected fields populated)."
    )
    parser.add_argument("date", help="Session date (YYYY-MM-DD)")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat empty fields as failures (default: warn only)",
    )
    args = parser.parse_args()

    sys.exit(check_log(args.date, args.strict))


if __name__ == "__main__":
    main()
