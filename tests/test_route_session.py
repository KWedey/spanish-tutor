"""ROUTE-FOLLOWUP-01: scripts/route_session.py simulates Step 3 routing decisions.

08-00 lands an import-level RED stub. 08-03 fills in the full row-by-row coverage.
08-06 adds the pairwise priority property test.
"""

import pytest
from pathlib import Path
from datetime import date
from scripts.route_session import route_session


class TestRouteSessionHarnessExists:
    def test_module_importable(self):
        """The routing harness module must exist and expose route_session(state_dir).
        Today this fails with ImportError; 08-03 turns it green."""
        from scripts import route_session as rs  # noqa: F401
        assert hasattr(rs, "route_session"), (
            "ROUTE-FOLLOWUP-01: scripts/route_session.py must define route_session(state_dir). "
            "See .planning/phases/08-followup-v1.1-improvements/08-03-PLAN.md."
        )

    def test_router_outputs_in_session_log_enum(self):
        """Audit C-3 regression guard. Every string `route_session()` may return
        must be a legal `session_type` value per `schemas/session-log.schema.yaml`.
        If this fails, either:
          (a) the router gained a new output without extending the schema enum, OR
          (b) the schema enum shrank without updating the router's ROUTABLE set.
        Both directions are equally bad — the session log can't persist the
        decision the router made and the canary doc's verification step breaks.
        """
        import yaml as _yaml
        from scripts.route_session import ROUTABLE_SESSION_TYPES
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "session-log.schema.yaml"
        schema = _yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        enum_values = set(schema["fields"]["session_type"]["enum"])
        unsupported = ROUTABLE_SESSION_TYPES - enum_values
        assert not unsupported, (
            f"audit C-3 regression: router can return {sorted(unsupported)} "
            f"but session-log.schema.yaml > session_type > enum lacks these. "
            "The session log writer will reject what the router decides."
        )


def _write_state(tmp_path, profile=None, schedule=None, sessions=None):
    """Helper — materialize a minimal state dir under tmp_path/state/ and return it."""
    state = tmp_path / "state"
    state.mkdir()
    (state / "sessions").mkdir()
    import yaml
    if profile is not None:
        (state / "learner-profile.yaml").write_text(yaml.safe_dump(profile))
    if schedule is not None:
        (state / "schedule.yaml").write_text(yaml.safe_dump(schedule))
    for s in (sessions or []):
        (state / "sessions" / f"{s['date']}.yaml").write_text(yaml.safe_dump(s))
    return state


class TestRouteSessionRows:
    """One test per Step 3 row + each documented overlay/precedence callout."""

    def test_no_session_logs_routes_to_first_session(self, tmp_path):
        state = _write_state(tmp_path, profile={}, schedule={}, sessions=[])
        assert route_session(state, today=date(2026, 5, 14)) == "first-session"

    def test_null_last_session_no_files_routes_to_first_session(self, tmp_path):
        """Edge case (eng-review 2026-05-14): schedule.yaml exists with
        last_session_date: null AND sessions/ directory has zero files. Row 1
        must still fire — `null` last_session_date alone is not enough to leave
        first-session if no log files back it up. Without this test, the
        documented fallback ("falls back to the most recent session log filename
        if last_session_date is null") silently routes to Standard with gap=0
        when no logs exist."""
        state = _write_state(
            tmp_path,
            profile={},
            schedule={"last_session_date": None, "onboarding_complete": True},
            sessions=[],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "first-session"

    def test_onboarding_incomplete_routes_to_onboarding(self, tmp_path):
        state = _write_state(
            tmp_path,
            profile={"target_dialect": "es-MX"},
            schedule={
                "onboarding_complete": False,
                "current_onboarding_session": 3,
                "last_session_date": "2026-05-13",
            },
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "onboarding"

    def test_onboarding_with_gap_routes_to_overlay(self, tmp_path):
        """ROUTE-01: gap >= 3 days during onboarding → onboarding-with-return-overlay
        (resume from same step, do NOT switch to standalone return-session)."""
        state = _write_state(
            tmp_path,
            schedule={
                "onboarding_complete": False,
                "current_onboarding_session": 3,
                "last_session_date": "2026-05-08",
            },
            sessions=[{"date": "2026-05-08"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "onboarding-with-return-overlay"

    def test_gap_3_plus_days_routes_to_return(self, tmp_path):
        state = _write_state(
            tmp_path,
            schedule={"onboarding_complete": True, "last_session_date": "2026-05-08"},
            sessions=[{"date": "2026-05-08"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "return"

    def test_return_takes_priority_over_weekly_review(self, tmp_path):
        """ROUTE-02: when gap >= 3 days AND today is weekly_review_day,
        return wins; weekly review is deferred to next session."""
        state = _write_state(
            tmp_path,
            profile={"weekly_review_day": "Wednesday"},
            schedule={"onboarding_complete": True, "last_session_date": "2026-05-08"},
            sessions=[{"date": "2026-05-08"}],
        )
        # 2026-05-13 is a Wednesday and is 5 days after 2026-05-08
        assert route_session(state, today=date(2026, 5, 13)) == "return"

    def test_maintenance_autonomy_routes_to_maintenance(self, tmp_path):
        state = _write_state(
            tmp_path,
            profile={"autonomy_level": "maintenance"},
            schedule={"onboarding_complete": True, "last_session_date": "2026-05-13"},
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "maintenance"

    def test_maintenance_overlays_weekly_review(self, tmp_path):
        """ROUTE-07: a maintenance-mode learner whose weekly_review_day matches today
        still receives a weekly review, with maintenance-specific focus."""
        state = _write_state(
            tmp_path,
            profile={"autonomy_level": "maintenance", "weekly_review_day": "Wednesday"},
            schedule={"onboarding_complete": True, "last_session_date": "2026-05-13"},
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 13)) == "maintenance-with-weekly-review"

    def test_weekly_review_day_routes_to_weekly_review(self, tmp_path):
        state = _write_state(
            tmp_path,
            profile={"weekly_review_day": "Wednesday"},
            schedule={"onboarding_complete": True, "last_session_date": "2026-05-12"},
            sessions=[{"date": "2026-05-12"}],
        )
        assert route_session(state, today=date(2026, 5, 13)) == "weekly-review"

    def test_sprint_active_routes_to_sprint(self, tmp_path):
        state = _write_state(
            tmp_path,
            schedule={
                "onboarding_complete": True,
                "last_session_date": "2026-05-13",
                "sprint": {"active": True},
                "placement_validation": {"active": False, "sessions_completed": 0},
            },
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "sprint"

    def test_placement_validation_overrides_sprint(self, tmp_path):
        """ROUTE-03: sprint.active=True + placement_validation.active=True
        + sessions_completed<3 → placement-validation (override)."""
        state = _write_state(
            tmp_path,
            schedule={
                "onboarding_complete": True,
                "last_session_date": "2026-05-13",
                "sprint": {"active": True},
                "placement_validation": {"active": True, "sessions_completed": 1},
            },
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "placement-validation"

    def test_placement_validation_complete_releases_sprint(self, tmp_path):
        """After placement_validation.sessions_completed >= 3, sprint resumes control."""
        state = _write_state(
            tmp_path,
            schedule={
                "onboarding_complete": True,
                "last_session_date": "2026-05-13",
                "sprint": {"active": True},
                "placement_validation": {"active": True, "sessions_completed": 3},
            },
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "sprint"

    def test_fluency_day_phase_b_plus_routes_to_fluency(self, tmp_path):
        """Production-realistic fixture: canonical phase string + counter field
        per `schemas/schedule.schema.yaml`. The audit C-1/C-2 fix changed the
        router to read these (not the bare letter / per-week field that the
        schema never defined)."""
        state = _write_state(
            tmp_path,
            schedule={
                "onboarding_complete": True,
                "last_session_date": "2026-05-13",
                "current_phase": "B-conversational",
                "fluency_days_this_week": 0,
                "last_fluency_day": "2026-05-06",
            },
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "fluency"

    def test_fluency_day_blocked_when_counter_reaches_target(self, tmp_path):
        """Production-realistic fixture: Phase B-conversational has a weekly
        target of 1 fluency day. Once `fluency_days_this_week >= 1`, the row
        must NOT fire. Regression guard for the audit C-2 bug where the field
        name was wrong and the count was effectively always 0."""
        state = _write_state(
            tmp_path,
            schedule={
                "onboarding_complete": True,
                "last_session_date": "2026-05-13",
                "current_phase": "B-conversational",
                "fluency_days_this_week": 1,
                "last_fluency_day": None,
            },
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "standard"

    def test_fluency_day_blocked_when_phase_a_foundation(self, tmp_path):
        """Production-realistic fixture: the very first canary learner has
        `current_phase: A-foundation` (verified against state/schedule.yaml).
        Fluency-day must not fire in Phase A. Audit C-1 regression guard:
        the old bare-letter check missed the "A-foundation" string entirely
        and would have allowed Phase A learners through if the target lookup
        had matched."""
        state = _write_state(
            tmp_path,
            schedule={
                "onboarding_complete": True,
                "last_session_date": "2026-05-13",
                "current_phase": "A-foundation",
                "fluency_days_this_week": 0,
            },
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "standard"

    def test_otherwise_routes_to_standard(self, tmp_path):
        state = _write_state(
            tmp_path,
            schedule={
                "onboarding_complete": True,
                "last_session_date": "2026-05-13",
                "current_phase": "A",
            },
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "standard"

    @pytest.mark.parametrize("day_value", ["Wednesday", "wednesday", "WEDNESDAY", "  Wednesday  "])
    def test_weekly_review_day_case_variants(self, tmp_path, day_value):
        """Format contract (eng-review 2026-05-14): weekly_review_day is normalized to
        capitalized-English. Case variants and surrounding whitespace must all route
        identically to weekly-review on a matching day. Documents the contract; protects
        against silent mis-route if a future onboarding edit writes lowercased values."""
        state = _write_state(
            tmp_path,
            profile={"weekly_review_day": day_value},
            schedule={"onboarding_complete": True, "last_session_date": "2026-05-12"},
            sessions=[{"date": "2026-05-12"}],
        )
        assert route_session(state, today=date(2026, 5, 13)) == "weekly-review"

    def test_weekly_review_day_uses_locale_independent_weekday_table(self):
        """Regression guard for the strftime('%A') locale trap (audit finding 08-03H2).

        The original implementation compared `today.strftime('%A')` to the profile's
        capitalized-English weekly_review_day. strftime is locale-aware: on a
        Spanish-locale system it returns 'miércoles' and never matches 'Wednesday',
        silently breaking weekly-review routing forever.

        The fix uses a fixed _WEEKDAY_NAMES_EN tuple indexed by today.weekday().
        weekday() returns 0..6 deterministically; the tuple is the canonical
        English source. This test fails if the table is removed or renamed."""
        from scripts import route_session as rs
        assert hasattr(rs, "_WEEKDAY_NAMES_EN"), (
            "scripts/route_session.py must expose _WEEKDAY_NAMES_EN — a fixed "
            "English weekday table — to avoid the strftime('%A') locale trap."
        )
        assert rs._WEEKDAY_NAMES_EN == (
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday",
        ), "_WEEKDAY_NAMES_EN must list English weekday names Monday..Sunday"


# ---------------------------------------------------------------------------
# ROUTE-FOLLOWUP-02: Pairwise priority property tests (08-06)
# ---------------------------------------------------------------------------
#
# NOTE: If you add a 10th row to CLAUDE.md Step 3, add the pair entries to
# PAIRWISE_EXPECTED below; CI will fail with missing-pair failures pointing
# back to the new row.
#
# Background: 9 row-equivalence classes × C(9,2) = 36 pairs. Many are not
# co-satisfiable (see None-winner entries). The remaining co-satisfiable pairs
# each have a documented winner from the canonical 11-string set in 08-03.

import yaml as _yaml  # noqa: E402 — local re-import for module-level helpers


class NotCoSatisfiable(Exception):
    """Raised when two row conditions cannot be satisfied simultaneously."""


# ---------------------------------------------------------------------------
# Fixed reference dates used across builders
#   TODAY      — 2026-05-14 (Thursday)
#   GAP_DATE   — 2026-05-08 (6 days before TODAY → gap >= 3)
#   RECENT_DATE — 2026-05-13 (1 day before TODAY → gap < 3)
#   WEDNESDAY  — 2026-05-13 (Wednesday, used for weekly_review_day tests)
# ---------------------------------------------------------------------------
_TODAY = date(2026, 5, 14)           # Thursday
_GAP_DATE = "2026-05-08"             # 6 days before _TODAY
_RECENT_DATE = "2026-05-13"          # 1 day before _TODAY (no gap)
_WEDNESDAY = date(2026, 5, 13)       # Wednesday (weekly-review day)


def _empty_state(tmp_path: Path) -> Path:
    """Create a fresh minimal state directory with sessions/ subdirectory."""
    state = tmp_path / "state"
    state.mkdir(exist_ok=True)
    (state / "sessions").mkdir(exist_ok=True)
    return state


def _write_profile(state: Path, data: dict) -> None:
    profile_path = state / "learner-profile.yaml"
    existing = {}
    if profile_path.exists():
        existing = _yaml.safe_load(profile_path.read_text()) or {}
    existing.update(data)
    profile_path.write_text(_yaml.safe_dump(existing))


def _write_schedule(state: Path, data: dict) -> None:
    """Write schedule fields, deep-merging nested dicts. Always overwrites."""
    schedule_path = state / "schedule.yaml"
    existing = {}
    if schedule_path.exists():
        existing = _yaml.safe_load(schedule_path.read_text()) or {}
    # Deep-merge nested dicts one level (sprint, placement_validation)
    for k, v in data.items():
        if isinstance(v, dict) and isinstance(existing.get(k), dict):
            existing[k].update(v)
        else:
            existing[k] = v
    schedule_path.write_text(_yaml.safe_dump(existing))


def _write_schedule_defaults(state: Path, data: dict) -> None:
    """Write schedule fields only for keys not already set (no-clobber).

    Used by builders that need a prerequisite field set as a baseline but
    must not override a value already written by a prior builder.
    Example: weekly-review needs onboarding_complete=True as a prereq,
    but must not clobber onboarding_complete=False set by onboarding builder.
    """
    schedule_path = state / "schedule.yaml"
    existing = {}
    if schedule_path.exists():
        existing = _yaml.safe_load(schedule_path.read_text()) or {}
    changed = False
    for k, v in data.items():
        if k not in existing:
            existing[k] = v
            changed = True
    if changed:
        schedule_path.write_text(_yaml.safe_dump(existing))


def _write_session(state: Path, session_date: str) -> None:
    (state / "sessions" / f"{session_date}.yaml").write_text(
        _yaml.safe_dump({"date": session_date})
    )


# ---------------------------------------------------------------------------
# Individual condition builders (each is *additive* — sets fields, does not
# clear others). Composed by _state_satisfying().
# ---------------------------------------------------------------------------

def _apply_no_sessions(state: Path) -> None:
    """Row 1 (first-session): no session log files.

    CLAUDE.md Step 3 Row 1: 'No session logs exist → first-session'.
    Deletes any logs written by a prior builder. Does NOT set onboarding_complete
    so that this builder doesn't conflict with onboarding (which sets it False).
    """
    for f in (state / "sessions").glob("*.yaml"):
        f.unlink()


def _apply_onboarding_incomplete(state: Path) -> None:
    """Row 2 (onboarding): onboarding_complete=False with a recent session log.

    CLAUDE.md Step 3 Row 2: 'onboarding_complete is false → onboarding'.
    Sets last_session_date to _RECENT_DATE (gap < 3) so that when composed with
    the return builder (_apply_3_day_gap, which only overrides last_session_date),
    the gap-date takes effect and the predicate still satisfies both conditions.
    """
    _write_schedule(state, {
        "onboarding_complete": False,
        "current_onboarding_session": 2,
        "last_session_date": _RECENT_DATE,
    })
    _write_session(state, _RECENT_DATE)


def _apply_3_day_gap(state: Path) -> None:
    """Row 3 (return): gap >= 3 days.

    CLAUDE.md Step 3 Row 3: 'Gap of 3+ days since last session → return'.
    ROUTE-02: takes priority over weekly review when both match.
    Only sets last_session_date — does NOT override onboarding_complete so
    that composing with _apply_onboarding_incomplete leaves onboarding_complete=False
    intact, producing onboarding-with-return-overlay as expected.
    """
    _write_schedule(state, {"last_session_date": _GAP_DATE})
    _write_session(state, _GAP_DATE)


def _apply_maintenance_autonomy(state: Path) -> None:
    """Row 4 (maintenance): autonomy_level=maintenance, recent session.

    CLAUDE.md Step 3 Row 4: 'autonomy_level is maintenance → maintenance'.
    Uses _write_schedule_defaults for onboarding_complete/last_session_date so
    that composing with return builder (_apply_3_day_gap) preserves the gap date.
    """
    _write_profile(state, {"autonomy_level": "maintenance"})
    _write_schedule_defaults(state, {
        "onboarding_complete": True,
        "last_session_date": _RECENT_DATE,
    })
    _write_session(state, _RECENT_DATE)


def _apply_weekly_review_day(state: Path) -> None:
    """Row 5 (weekly-review): today is weekly_review_day, recent session.

    CLAUDE.md Step 3 Row 5: 'today's day-of-week matches weekly_review_day
    → weekly-review'.
    Sets weekly_review_day=Wednesday (owned field). Uses _write_schedule_defaults
    for onboarding_complete/last_session_date so composing with onboarding or
    return builders preserves their values.
    """
    _write_profile(state, {"weekly_review_day": "Wednesday"})
    _write_schedule_defaults(state, {
        "onboarding_complete": True,
        "last_session_date": _RECENT_DATE,
    })
    _write_session(state, _RECENT_DATE)


def _apply_sprint_active(state: Path) -> None:
    """Row 6 (sprint): sprint.active=True, recent session, placement done.

    CLAUDE.md Step 3 Row 6: 'sprint.active is true → sprint'.
    Uses _write_schedule_defaults for onboarding_complete/last_session_date so
    composing with onboarding or return builders preserves their values.
    Sets placement_validation to inactive/complete as a default; when composed
    with _apply_placement_validation_active (which runs second), the deep-merge
    in _write_schedule overwrites these with the active values.
    """
    _write_schedule_defaults(state, {
        "onboarding_complete": True,
        "last_session_date": _RECENT_DATE,
    })
    _write_schedule(state, {
        "sprint": {"active": True},
        "placement_validation": {"active": False, "sessions_completed": 3},
    })
    _write_session(state, _RECENT_DATE)


def _apply_placement_validation_active(state: Path) -> None:
    """Row 7 (placement-validation override): sprint active + pv active + <3 sessions.

    CLAUDE.md Step 3 Row 6 ROUTE-03: 'placement_validation.active + sessions_completed
    < 3 overrides sprint → placement-validation'.
    This condition only fires *under* sprint, so sprint must also be active.
    Uses _write_schedule_defaults for onboarding_complete/last_session_date.
    """
    _write_schedule_defaults(state, {
        "onboarding_complete": True,
        "last_session_date": _RECENT_DATE,
    })
    _write_schedule(state, {
        "sprint": {"active": True},
        "placement_validation": {"active": True, "sessions_completed": 1},
    })
    _write_session(state, _RECENT_DATE)


def _apply_fluency_day_phase_b(state: Path) -> None:
    """Row 7 (fluency): Phase B+, weekly fluency target > 0, not consecutive.

    CLAUDE.md Step 3 Row 7: 'Phase B+ AND today is a fluency day → fluency'.
    Uses _write_schedule_defaults for onboarding_complete/last_session_date.
    current_phase, fluency_days_this_week, and last_fluency_day are owned
    fields written unconditionally.

    Uses the schema-canonical phase string `B-conversational` (NOT the bare
    letter `B` — the audit C-1 bug was the router checking `{"B","C","D"}`
    against schema enum `["A-foundation","B-conversational",...]`).
    """
    _write_schedule_defaults(state, {
        "onboarding_complete": True,
        "last_session_date": _RECENT_DATE,
    })
    _write_schedule(state, {
        "current_phase": "B-conversational",
        "fluency_days_this_week": 0,
        "last_fluency_day": "2026-05-06",
    })
    _write_session(state, _RECENT_DATE)


def _apply_standard_default(state: Path) -> None:
    """Row 9 (standard): recent session, onboarding complete, no special flags.

    CLAUDE.md Step 3 Row 8: 'otherwise → standard'.
    Uses _write_schedule_defaults for all fields — standard is the else-branch
    and must not clobber any field owned by a prior builder (e.g., must not
    override current_phase=B set by fluency, or last_session_date=_GAP_DATE
    set by return).
    """
    _write_schedule_defaults(state, {
        "onboarding_complete": True,
        "last_session_date": _RECENT_DATE,
    })
    _write_session(state, _RECENT_DATE)


_BUILDERS = {
    "first-session": _apply_no_sessions,
    "onboarding": _apply_onboarding_incomplete,
    "return": _apply_3_day_gap,
    "maintenance": _apply_maintenance_autonomy,
    "weekly-review": _apply_weekly_review_day,
    "sprint": _apply_sprint_active,
    "placement-validation": _apply_placement_validation_active,
    "fluency": _apply_fluency_day_phase_b,
    "standard": _apply_standard_default,
}

# ---------------------------------------------------------------------------
# Predicate re-validators (check that condition still holds after composition)
# ---------------------------------------------------------------------------

def _pred_first_session(state: Path) -> bool:
    return not any((state / "sessions").glob("*.yaml"))


def _pred_onboarding(state: Path) -> bool:
    schedule_path = state / "schedule.yaml"
    if not schedule_path.exists():
        return False
    schedule = _yaml.safe_load(schedule_path.read_text()) or {}
    return not schedule.get("onboarding_complete", True)


def _pred_return(state: Path, today: date) -> bool:
    """True if a 3+ day gap exists.

    Does NOT require onboarding_complete=True — the gap condition is independent
    of onboarding status. When onboarding_complete=False AND gap >= 3, the router
    returns 'onboarding-with-return-overlay' (Row 2 overlay), not 'return' (Row 3).
    The predicate captures only the raw gap condition so that the onboarding × return
    pair is correctly recognised as co-satisfiable.
    """
    schedule_path = state / "schedule.yaml"
    if not schedule_path.exists():
        return False
    schedule = _yaml.safe_load(schedule_path.read_text()) or {}
    last = schedule.get("last_session_date")
    if not last:
        return False
    try:
        return (today - date.fromisoformat(str(last))).days >= 3
    except ValueError:
        return False


def _pred_maintenance(state: Path) -> bool:
    profile_path = state / "learner-profile.yaml"
    if not profile_path.exists():
        return False
    profile = _yaml.safe_load(profile_path.read_text()) or {}
    return profile.get("autonomy_level") == "maintenance"


def _pred_weekly_review(state: Path, today: date) -> bool:
    # Mirror the production fix in scripts/route_session.py: avoid strftime("%A")
    # which is locale-aware. Use a fixed English weekday table indexed by
    # today.weekday() so test predicates match router behavior under any locale.
    from scripts.route_session import _WEEKDAY_NAMES_EN
    profile_path = state / "learner-profile.yaml"
    if not profile_path.exists():
        return False
    profile = _yaml.safe_load(profile_path.read_text()) or {}
    raw = profile.get("weekly_review_day", "") or ""
    return _WEEKDAY_NAMES_EN[today.weekday()] == raw.strip().capitalize()


def _pred_sprint(state: Path) -> bool:
    schedule_path = state / "schedule.yaml"
    if not schedule_path.exists():
        return False
    schedule = _yaml.safe_load(schedule_path.read_text()) or {}
    sprint = schedule.get("sprint") or {}
    return bool(sprint.get("active", False))


def _pred_placement_validation(state: Path) -> bool:
    schedule_path = state / "schedule.yaml"
    if not schedule_path.exists():
        return False
    schedule = _yaml.safe_load(schedule_path.read_text()) or {}
    pv = schedule.get("placement_validation") or {}
    return (
        bool(pv.get("active", False))
        and pv.get("sessions_completed", 0) < 3
        and _pred_sprint(state)
    )


def _pred_fluency(state: Path, today: date) -> bool:
    """Mirror the production predicate at scripts.route_session._is_fluency_day.

    Audit C-1/C-2: the production code now uses canonical phase strings
    ("B-conversational" etc.) and reads `fluency_days_this_week` directly
    (not the never-existed `fluency_days_per_week`). Keep this re-validator
    in sync — drift here was the original source of the pairwise test giving
    false-green coverage."""
    from scripts.route_session import _FLUENCY_DAYS_PER_PHASE
    schedule_path = state / "schedule.yaml"
    if not schedule_path.exists():
        return False
    schedule = _yaml.safe_load(schedule_path.read_text()) or {}
    phase = schedule.get("current_phase") or ""
    target = _FLUENCY_DAYS_PER_PHASE.get(phase, 0)
    if target <= 0:
        return False
    this_week = int(schedule.get("fluency_days_this_week") or 0)
    if this_week >= target:
        return False
    last_raw = schedule.get("last_fluency_day")
    if last_raw:
        try:
            lf = date.fromisoformat(str(last_raw))
            if (today - lf).days <= 1:
                return False
        except ValueError:
            return True
    return True


_PREDICATES = {
    "first-session": lambda state, today: _pred_first_session(state),
    "onboarding": lambda state, today: _pred_onboarding(state),
    "return": lambda state, today: _pred_return(state, today),
    "maintenance": lambda state, today: _pred_maintenance(state),
    "weekly-review": lambda state, today: _pred_weekly_review(state, today),
    "sprint": lambda state, today: _pred_sprint(state),
    "placement-validation": lambda state, today: _pred_placement_validation(state),
    "fluency": lambda state, today: _pred_fluency(state, today),
    "standard": lambda state, today: True,  # always satisfiable as fallback
}


def _both_satisfied(state: Path, a: str, b: str, today: date) -> bool:
    """Re-validate that both condition predicates still hold after builder composition."""
    return _PREDICATES[a](state, today) and _PREDICATES[b](state, today)


def _today_for(a: str, b: str) -> date:
    """Return the reference `today` appropriate for the condition pair.

    Pairs involving weekly-review need _WEDNESDAY; pairs involving return
    need _TODAY (6-day gap from _GAP_DATE). When both apply (return ×
    weekly-review), return wins and _WEDNESDAY satisfies both (Wednesday
    is still 5 days after _GAP_DATE=2026-05-08).
    """
    if "weekly-review" in (a, b) or "maintenance" in (a, b):
        # Wednesday: satisfies weekly_review_day=Wednesday AND is 5 days after GAP_DATE
        return _WEDNESDAY
    return _TODAY


# Domain-level incompatibilities that cannot be expressed via predicates alone.
# These are semantic constraints from CLAUDE.md (e.g., a learner cannot reach
# maintenance autonomy without completing onboarding).
_DOMAIN_INCOMPATIBLE = frozenset([
    frozenset(["onboarding", "maintenance"]),
    frozenset(["first-session", "onboarding"]),
    frozenset(["first-session", "return"]),
    frozenset(["first-session", "maintenance"]),
    frozenset(["first-session", "weekly-review"]),
    frozenset(["first-session", "sprint"]),
    frozenset(["first-session", "placement-validation"]),
    frozenset(["first-session", "fluency"]),
])


def _state_satisfying(tmp_path: Path, a: str, b: str) -> Path:
    """Build a state directory satisfying both condition predicates.

    Applies builder[a] then builder[b] (additive composition).
    Raises NotCoSatisfiable if:
      - the pair is in the known domain-incompatibility set, OR
      - after composition, at least one predicate no longer holds.
    """
    if frozenset([a, b]) in _DOMAIN_INCOMPATIBLE:
        raise NotCoSatisfiable(
            f"Conditions '{a}' and '{b}' are domain-incompatible "
            f"(see CLAUDE.md Step 3 + _DOMAIN_INCOMPATIBLE)."
        )
    state = _empty_state(tmp_path)
    _BUILDERS[a](state)
    _BUILDERS[b](state)
    today = _today_for(a, b)
    if not _both_satisfied(state, a, b, today):
        raise NotCoSatisfiable(
            f"Conditions '{a}' and '{b}' cannot be satisfied simultaneously. "
            f"After applying both builders, at least one predicate no longer holds."
        )
    return state


# ---------------------------------------------------------------------------
# Pairwise expected-winner table
# ---------------------------------------------------------------------------
#
# Each tuple: (condition_a, condition_b, expected_winner, reason).
# winner=None means not co-satisfiable; the test asserts NotCoSatisfiable.
#
# NOTE: If you add a row to CLAUDE.md Step 3, add the pair entries here;
# CI will fail with missing-pair failures pointing back to the new row.

PAIRWISE_EXPECTED = [
    # ── Onboarding precedence (CLAUDE.md Step 3 Row 2) ───────────────────
    ("onboarding", "return", "onboarding-with-return-overlay",
     "ROUTE-01: onboarding row layers return diagnostic; does not switch to standalone return"),
    ("onboarding", "weekly-review", "onboarding",
     "Row order: onboarding (Row 2) precedes weekly-review (Row 5)"),
    ("onboarding", "sprint", "onboarding",
     "Row order: onboarding (Row 2) precedes sprint (Row 6)"),
    ("onboarding", "fluency", "onboarding",
     "Row order: onboarding (Row 2) precedes fluency (Row 7)"),
    ("onboarding", "maintenance", None,
     "Not co-satisfiable: onboarding_complete=False implies autonomy_level != maintenance"),

    # ── Return precedence (CLAUDE.md Step 3 Row 3) ───────────────────────
    ("return", "weekly-review", "return",
     "ROUTE-02: return (Row 3) takes priority over weekly-review (Row 5); defer weekly to next session"),
    ("return", "maintenance", "return",
     "Row 3 precedes Row 4 — return fires even for a maintenance-mode learner with a 3+ day gap"),
    ("return", "sprint", "return",
     "Row 3 precedes Row 6 — a 3+ day gap routes to return regardless of sprint.active"),
    ("return", "fluency", "return",
     "Row 3 precedes Row 7 — return wins over fluency-day eligibility"),

    # ── Maintenance + weekly-review overlay (CLAUDE.md Step 3 Rows 4+5) ──
    ("maintenance", "weekly-review", "maintenance-with-weekly-review",
     "ROUTE-07: maintenance learner on weekly_review_day gets maintenance-focus review (Row 4 overlay)"),
    ("maintenance", "sprint", "maintenance",
     "Row 4 precedes Row 6 — maintenance autonomy makes sprint mode non-applicable"),
    ("maintenance", "fluency", "maintenance",
     "Row 4 precedes Row 7 — maintenance wins over fluency-day"),

    # ── Weekly-review (CLAUDE.md Step 3 Row 5) ───────────────────────────
    ("weekly-review", "sprint", "weekly-review",
     "Row 5 precedes Row 6 — weekly-review wins over sprint when both would match"),
    ("weekly-review", "fluency", "weekly-review",
     "Row 5 precedes Row 7 — weekly-review wins over fluency-day"),

    # ── Sprint + placement-validation override (CLAUDE.md Step 3 Row 6) ──
    ("sprint", "placement-validation", "placement-validation",
     "ROUTE-03: placement_validation.active + sessions_completed<3 overrides sprint (Row 6 callout)"),
    ("sprint", "fluency", "sprint",
     "Row 6 precedes Row 7 — sprint wins over fluency-day"),

    # ── Fluency (CLAUDE.md Step 3 Row 7) ─────────────────────────────────
    ("fluency", "standard", "fluency",
     "Row 7 precedes Row 8 — fluency-day eligibility wins over the default standard"),

    # ── Not co-satisfiable: first-session vs everything else ─────────────
    # first-session requires zero session logs; all other rows require at least one.
    ("first-session", "onboarding", None,
     "Not co-satisfiable: first-session requires zero logs; onboarding requires at least one"),
    ("first-session", "return", None,
     "Not co-satisfiable: first-session requires zero logs; return requires gap calculation from a log"),
    ("first-session", "maintenance", None,
     "Not co-satisfiable: first-session requires zero logs; maintenance requires a recent session"),
    ("first-session", "weekly-review", None,
     "Not co-satisfiable: first-session requires zero logs; weekly-review requires a recent session"),
    ("first-session", "sprint", None,
     "Not co-satisfiable: first-session requires zero logs; sprint requires a recent session"),
    ("first-session", "placement-validation", None,
     "Not co-satisfiable: first-session requires zero logs; placement-validation requires sprint active with a session"),
    ("first-session", "fluency", None,
     "Not co-satisfiable: first-session requires zero logs; fluency requires a recent session"),
    ("first-session", "standard", None,
     "Not co-satisfiable: first-session requires zero session logs; the standard builder writes one (and the router only returns 'standard' when row 1 has not fired)."),

    # ── Placement-validation interactions with higher-priority rows ──────
    # placement-validation only fires under sprint.active=True; rows 2-5 all
    # precede the sprint row in CLAUDE.md Step 3, so they win when co-satisfied.
    ("onboarding", "placement-validation", "onboarding",
     "Row order: onboarding (Row 2) precedes sprint/placement-validation (Row 6 override)"),
    ("return", "placement-validation", "return",
     "Row order: return (Row 3) precedes sprint/placement-validation (Row 6 override)"),
    ("maintenance", "placement-validation", "maintenance",
     "Row order: maintenance (Row 4) precedes sprint/placement-validation (Row 6 override)"),
    ("weekly-review", "placement-validation", "weekly-review",
     "Row order: weekly-review (Row 5) precedes sprint/placement-validation (Row 6 override)"),
    ("placement-validation", "fluency", "placement-validation",
     "ROUTE-03 + Row order: placement-validation overrides sprint (Row 6), which precedes fluency (Row 7)"),

    # ── Standard (Row 8 'otherwise') interactions ────────────────────────
    # `standard` is the catch-all that fires only when no Row 1-7 condition
    # matches. The _pred_standard re-validator always returns True (standard
    # is structurally satisfiable for any state), so these pairs verify that
    # whenever a Row 1-7 condition also fires, the router never falls through
    # to 'standard'. Each documented winner is the higher-priority row.
    ("onboarding", "standard", "onboarding",
     "Row order: onboarding (Row 2) fires before the otherwise/standard fallback (Row 8)"),
    ("return", "standard", "return",
     "Row order: return (Row 3) fires before the otherwise/standard fallback (Row 8)"),
    ("maintenance", "standard", "maintenance",
     "Row order: maintenance (Row 4) fires before the otherwise/standard fallback (Row 8)"),
    ("weekly-review", "standard", "weekly-review",
     "Row order: weekly-review (Row 5) fires before the otherwise/standard fallback (Row 8)"),
    ("sprint", "standard", "sprint",
     "Row order: sprint (Row 6) fires before the otherwise/standard fallback (Row 8)"),
    ("placement-validation", "standard", "placement-validation",
     "Row order: placement-validation override (Row 6) fires before the otherwise/standard fallback (Row 8)"),
    # NOTE: fluency × standard is already covered in the "Fluency (Row 7)" block above.
]


# Backstop: with 9 row-equivalence classes, C(9,2) = 36 unordered pairs.
# A future Step 3 row addition must extend both _BUILDERS/_PREDICATES and this
# table. A silent gap = an unmeasured ambiguity surface — fail loudly at import.
assert len(PAIRWISE_EXPECTED) == 36, (
    f"PAIRWISE_EXPECTED has {len(PAIRWISE_EXPECTED)} entries — expected 36 "
    "(C(9,2) for the 9 Step 3 row-equivalence classes). Either a row was added "
    "without adding its pairs, or a pair was removed. Restore coverage in the "
    "ROUTE-FOLLOWUP-02 table above."
)


class TestStep3PairwisePriority:
    """ROUTE-FOLLOWUP-02: for every pair where two CLAUDE.md Step 3 rows could
    match the same input state, the documented precedence produces a single
    deterministic winner.

    Cross-reference: CLAUDE.md Step 3 routing table (row order is load-bearing).
    The 9 row-equivalence classes and their documented priority callouts
    (ROUTE-01, ROUTE-02, ROUTE-03, ROUTE-07) are the source of truth.

    08-03 covers each row in isolation; 08-06 covers the interaction surface —
    pairs where two rows could match the same state.
    """

    @pytest.mark.parametrize("a,b,winner,reason", PAIRWISE_EXPECTED)
    def test_step3_pairwise_priority(self, tmp_path, a, b, winner, reason):
        """ROUTE-FOLLOWUP-02: for every pair where two Step 3 rows could match,
        the documented precedence produces a single deterministic winner.

        CLAUDE.md Step 3 routing table row order is the source of truth.
        If `winner is None`, the pair is not co-satisfiable — assert the helper
        raises NotCoSatisfiable rather than silently producing a misleading result.
        """
        if winner is None:
            with pytest.raises(NotCoSatisfiable):
                _state_satisfying(tmp_path, a, b)
            return

        state = _state_satisfying(tmp_path, a, b)
        today = _today_for(a, b)
        actual = route_session(state, today=today)
        assert actual == winner, (
            f"Pair ({a!r}, {b!r}): expected {winner!r} (reason: {reason}); "
            f"got {actual!r}. See CLAUDE.md Step 3 routing table."
        )
