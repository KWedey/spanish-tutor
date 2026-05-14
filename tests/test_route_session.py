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
        state = _write_state(
            tmp_path,
            schedule={
                "onboarding_complete": True,
                "last_session_date": "2026-05-13",
                "current_phase": "B",
                "fluency_days_per_week": 1,
                "last_fluency_day": "2026-05-06",
            },
            sessions=[{"date": "2026-05-13"}],
        )
        assert route_session(state, today=date(2026, 5, 14)) == "fluency"

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
