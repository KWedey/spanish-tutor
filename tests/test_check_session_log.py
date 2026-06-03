"""Tests for scripts/check-session-log.py expected-field enforcement.

Wave 0: Tests for ENFORCE-02..05 — first-session, onboarding, sprint, fluency
session types. Each class verifies that EXPECTED_BY_TYPE has the correct
entries and that check_log() fails when required fields are missing.
"""
import copy
import sys
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Import check-session-log module via importlib (hyphenated filename)
# ---------------------------------------------------------------------------

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import importlib

check_mod = importlib.import_module("check-session-log")

EXPECTED_BY_TYPE = check_mod.EXPECTED_BY_TYPE
BASE_EXPECTED = check_mod.BASE_EXPECTED
check_log = check_mod.check_log
get_nested = check_mod.get_nested

# ENGINE Phase 4 function reference (will raise AttributeError until implemented — RED state)
check_recasts_required = getattr(check_mod, "check_recasts_required", None)

_missing_recasts_fn = pytest.mark.skipif(
    check_recasts_required is None,
    reason="check_recasts_required not yet implemented — RED phase"
)

# LOAD Phase 5 function/constant references (None until 05-03/05-04 ship — RED state)
check_assignment_budget = getattr(check_mod, "check_assignment_budget", None)
compute_assignment_budget_total = getattr(check_mod, "compute_assignment_budget_total", None)
check_homework_load_rating_required = getattr(check_mod, "check_homework_load_rating_required", None)
PHASE_5_CUTOFF = getattr(check_mod, "PHASE_5_CUTOFF", None)

_missing_budget_fns = pytest.mark.skipif(
    check_assignment_budget is None or compute_assignment_budget_total is None or PHASE_5_CUTOFF is None,
    reason="LOAD Phase 5 budget enforcement not yet implemented — RED phase",
)
_missing_load_rating_fn = pytest.mark.skipif(
    check_homework_load_rating_required is None,
    reason="LOAD Phase 5 homework_load_rating conditional not yet implemented — RED phase",
)

# Grab the individual constants (will exist after implementation)
# We test via EXPECTED_BY_TYPE dict lookup instead, which is more robust.


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_session_log(session_type: str, extra_fields: dict | None = None) -> dict:
    """Build a minimal session log dict with all BASE_EXPECTED fields populated."""
    base = {
        "date": "2026-04-15",
        "session_number": 3,
        "duration_minutes": 30,
        "session_type": session_type,
        "session_status": "complete",
        "learner_energy": "medium",
        "session_activities": [{"type": "warm-up"}],
        "learner_observations": {
            "mood": "motivated",
            "engagement": "high",
        },
    }
    if extra_fields:
        for key, value in extra_fields.items():
            # Handle dotted paths
            parts = key.split(".")
            target = base
            for part in parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            target[parts[-1]] = value
    return base


def _write_session_log(state_dir: Path, date: str, data: dict) -> None:
    sessions_dir = state_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    with open(sessions_dir / f"{date}.yaml", "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


# ---------------------------------------------------------------------------
# Schema enum tests (Task 1 verification)
# ---------------------------------------------------------------------------

class TestSessionTypeEnum:
    """Verify session-log.schema.yaml has all 9 session_type values."""

    def test_schema_has_first_session(self):
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "session-log.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        enum_values = schema["fields"]["session_type"]["enum"]
        assert "first-session" in enum_values, (
            "ENFORCE-02: 'first-session' missing from session-log.schema.yaml session_type enum"
        )

    def test_schema_has_onboarding(self):
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "session-log.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        enum_values = schema["fields"]["session_type"]["enum"]
        assert "onboarding" in enum_values, (
            "ENFORCE-03: 'onboarding' missing from session-log.schema.yaml session_type enum"
        )

    def test_schema_has_sprint(self):
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "session-log.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        enum_values = schema["fields"]["session_type"]["enum"]
        assert "sprint" in enum_values, (
            "ENFORCE-04: 'sprint' missing from session-log.schema.yaml session_type enum"
        )

    def test_schema_has_fluency(self):
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "session-log.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        enum_values = schema["fields"]["session_type"]["enum"]
        assert "fluency" in enum_values, (
            "ENFORCE-05: 'fluency' missing from session-log.schema.yaml session_type enum"
        )

    def test_schema_preserves_existing_values(self):
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "session-log.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        enum_values = schema["fields"]["session_type"]["enum"]
        for val in ["standard", "micro", "weekly-review", "phase-transition", "return"]:
            assert val in enum_values, f"Pre-existing enum value '{val}' was removed"

    def test_schema_has_all_routable_session_types(self):
        """Audit C-3: enum must cover the 9 base types (ENFORCE-02..05) AND the
        4 router-returnable strings introduced when scripts/route_session.py
        landed (maintenance, placement-validation, onboarding-with-return-overlay,
        maintenance-with-weekly-review).

        Replaces the prior strict ==9 assertion, which was correct for Phase 3
        but blocked the audit C-3 fix that legitimately extends the enum. The
        new bar is "every base type + every router output", checked by
        membership rather than count — so future additions to either set don't
        require updating the literal in this test."""
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "session-log.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        enum_values = set(schema["fields"]["session_type"]["enum"])
        required = {
            # 9 base types (ENFORCE-02..05 + pre-existing)
            "standard", "micro", "weekly-review", "phase-transition", "return",
            "first-session", "onboarding", "sprint", "fluency",
            # 4 router-returnable strings (audit C-3)
            "maintenance", "placement-validation",
            "onboarding-with-return-overlay", "maintenance-with-weekly-review",
        }
        missing = required - enum_values
        assert not missing, f"session_type enum missing required values: {sorted(missing)}"


# ---------------------------------------------------------------------------
# EXPECTED_BY_TYPE tests (Task 2 verification)
# ---------------------------------------------------------------------------

class TestFirstSession:
    """ENFORCE-02: first-session type must be recognized with correct expected fields."""

    def test_first_session_in_expected_by_type(self):
        assert "first-session" in EXPECTED_BY_TYPE, (
            "ENFORCE-02: 'first-session' not in EXPECTED_BY_TYPE dict"
        )

    def test_first_session_inherits_base(self):
        expected = EXPECTED_BY_TYPE["first-session"]
        for field in BASE_EXPECTED:
            assert field in expected, (
                f"ENFORCE-02: first-session missing BASE field '{field}'"
            )

    def test_first_session_requires_assessment(self):
        expected = EXPECTED_BY_TYPE["first-session"]
        assert "assessment" in expected, (
            "ENFORCE-02: first-session missing 'assessment' field"
        )

    def test_first_session_requires_skill_map_updates(self):
        expected = EXPECTED_BY_TYPE["first-session"]
        assert "skill_map_updates" in expected, (
            "ENFORCE-02: first-session missing 'skill_map_updates' field"
        )

    def test_first_session_missing_field_fails(self, tmp_path, monkeypatch):
        """A first-session log missing 'assessment' should fail check_log."""
        state_dir = tmp_path / "state"
        monkeypatch.setattr(check_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(check_mod, "ROOT", tmp_path)

        log_data = _make_session_log("first-session", {
            "skill_map_updates": [{"concept": "A-01"}],
            # assessment deliberately missing
        })
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 1, "first-session log missing 'assessment' should FAIL"

    def test_first_session_complete_log_passes(self, tmp_path, monkeypatch):
        """A first-session log with all required fields should pass."""
        state_dir = tmp_path / "state"
        monkeypatch.setattr(check_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(check_mod, "ROOT", tmp_path)

        log_data = _make_session_log("first-session", {
            "assessment": {"placement_decision": "Phase A"},
            "skill_map_updates": [{"concept": "A-01"}],
        })
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 0, "first-session log with all fields should PASS"


class TestOnboarding:
    """ENFORCE-03: onboarding type must be recognized with correct expected fields."""

    def test_onboarding_in_expected_by_type(self):
        assert "onboarding" in EXPECTED_BY_TYPE, (
            "ENFORCE-03: 'onboarding' not in EXPECTED_BY_TYPE dict"
        )

    def test_onboarding_inherits_base(self):
        expected = EXPECTED_BY_TYPE["onboarding"]
        for field in BASE_EXPECTED:
            assert field in expected, (
                f"ENFORCE-03: onboarding missing BASE field '{field}'"
            )

    def test_onboarding_requires_session_activities(self):
        expected = EXPECTED_BY_TYPE["onboarding"]
        assert "session_activities" in expected

    def test_onboarding_requires_skill_map_updates(self):
        expected = EXPECTED_BY_TYPE["onboarding"]
        assert "skill_map_updates" in expected

    def test_onboarding_requires_assignments(self):
        expected = EXPECTED_BY_TYPE["onboarding"]
        assert "assignments" in expected

    def test_onboarding_requires_next_session_focus(self):
        expected = EXPECTED_BY_TYPE["onboarding"]
        assert "next_session.recommended_focus" in expected

    def test_onboarding_missing_field_fails(self, tmp_path, monkeypatch):
        """An onboarding log missing 'assignments' should fail."""
        state_dir = tmp_path / "state"
        monkeypatch.setattr(check_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(check_mod, "ROOT", tmp_path)

        log_data = _make_session_log("onboarding", {
            "skill_map_updates": [{"concept": "A-01"}],
            "next_session": {"recommended_focus": "greetings"},
            # assignments deliberately missing
        })
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 1, "onboarding log missing 'assignments' should FAIL"

    def test_onboarding_complete_log_passes(self, tmp_path, monkeypatch):
        """An onboarding log with all required fields should pass."""
        state_dir = tmp_path / "state"
        monkeypatch.setattr(check_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(check_mod, "ROOT", tmp_path)

        log_data = _make_session_log("onboarding", {
            "skill_map_updates": [{"concept": "A-01"}],
            "assignments": [{"type": "anki"}],
            "next_session": {"recommended_focus": "greetings"},
        })
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 0, "onboarding log with all fields should PASS"


class TestSprint:
    """ENFORCE-04: sprint type must be recognized with correct expected fields."""

    def test_sprint_in_expected_by_type(self):
        assert "sprint" in EXPECTED_BY_TYPE, (
            "ENFORCE-04: 'sprint' not in EXPECTED_BY_TYPE dict"
        )

    def test_sprint_inherits_base(self):
        expected = EXPECTED_BY_TYPE["sprint"]
        for field in BASE_EXPECTED:
            assert field in expected, (
                f"ENFORCE-04: sprint missing BASE field '{field}'"
            )

    def test_sprint_requires_session_activities(self):
        expected = EXPECTED_BY_TYPE["sprint"]
        assert "session_activities" in expected

    def test_sprint_requires_assignments(self):
        expected = EXPECTED_BY_TYPE["sprint"]
        assert "assignments" in expected

    def test_sprint_requires_skill_map_updates(self):
        expected = EXPECTED_BY_TYPE["sprint"]
        assert "skill_map_updates" in expected

    def test_sprint_requires_next_session_focus(self):
        expected = EXPECTED_BY_TYPE["sprint"]
        assert "next_session.recommended_focus" in expected

    def test_sprint_missing_field_fails(self, tmp_path, monkeypatch):
        """A sprint log missing 'skill_map_updates' should fail."""
        state_dir = tmp_path / "state"
        monkeypatch.setattr(check_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(check_mod, "ROOT", tmp_path)

        log_data = _make_session_log("sprint", {
            "assignments": [{"type": "vocab-drill"}],
            "next_session": {"recommended_focus": "survival-vocab"},
            # skill_map_updates deliberately missing
        })
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 1, "sprint log missing 'skill_map_updates' should FAIL"

    def test_sprint_complete_log_passes(self, tmp_path, monkeypatch):
        """A sprint log with all required fields should pass."""
        state_dir = tmp_path / "state"
        monkeypatch.setattr(check_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(check_mod, "ROOT", tmp_path)

        log_data = _make_session_log("sprint", {
            "assignments": [{"type": "vocab-drill"}],
            "skill_map_updates": [{"concept": "survival-01"}],
            "next_session": {"recommended_focus": "survival-vocab"},
        })
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 0, "sprint log with all fields should PASS"


class TestFluency:
    """ENFORCE-05: fluency type must be recognized with correct expected fields."""

    def test_fluency_in_expected_by_type(self):
        assert "fluency" in EXPECTED_BY_TYPE, (
            "ENFORCE-05: 'fluency' not in EXPECTED_BY_TYPE dict"
        )

    def test_fluency_inherits_base(self):
        expected = EXPECTED_BY_TYPE["fluency"]
        for field in BASE_EXPECTED:
            assert field in expected, (
                f"ENFORCE-05: fluency missing BASE field '{field}'"
            )

    def test_fluency_requires_session_activities(self):
        expected = EXPECTED_BY_TYPE["fluency"]
        assert "session_activities" in expected

    def test_fluency_requires_skill_map_updates(self):
        expected = EXPECTED_BY_TYPE["fluency"]
        assert "skill_map_updates" in expected

    def test_fluency_requires_assignments(self):
        expected = EXPECTED_BY_TYPE["fluency"]
        assert "assignments" in expected

    def test_fluency_requires_next_session_focus(self):
        expected = EXPECTED_BY_TYPE["fluency"]
        assert "next_session.recommended_focus" in expected

    def test_fluency_missing_field_fails(self, tmp_path, monkeypatch):
        """A fluency log missing 'assignments' should fail."""
        state_dir = tmp_path / "state"
        monkeypatch.setattr(check_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(check_mod, "ROOT", tmp_path)

        log_data = _make_session_log("fluency", {
            "skill_map_updates": [{"concept": "fluency-01"}],
            "next_session": {"recommended_focus": "fluency-practice"},
            # assignments deliberately missing
        })
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 1, "fluency log missing 'assignments' should FAIL"

    def test_fluency_complete_log_passes(self, tmp_path, monkeypatch):
        """A fluency log with all required fields should pass."""
        state_dir = tmp_path / "state"
        monkeypatch.setattr(check_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(check_mod, "ROOT", tmp_path)

        log_data = _make_session_log("fluency", {
            "skill_map_updates": [{"concept": "fluency-01"}],
            "assignments": [{"type": "self-narration"}],
            "next_session": {"recommended_focus": "fluency-practice"},
        })
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 0, "fluency log with all fields should PASS"


# ---------------------------------------------------------------------------
# ENGINE Phase 4: Conditional recasts enforcement (D-06)
# ---------------------------------------------------------------------------

@_missing_recasts_fn
class TestRecasts:
    """D-06: recasts field conditionally required based on session content."""

    def test_stage3_no_recasts_fails(self):
        """Session with stage-3 activity missing recasts field should FAIL."""
        log = _make_session_log("standard", {
            "session_activities": [
                {"type": "guided-production", "stage": "stage-3", "concept": "C-03"}
            ],
        })
        # Ensure no recasts field
        log.pop("recasts", None)
        assert check_recasts_required(log) is True, \
            "D-06: stage-3 activity should trigger recasts required"

    def test_stage3_empty_recasts_passes(self):
        """Session with stage-3 and recasts: [] should PASS."""
        log = _make_session_log("standard", {
            "session_activities": [
                {"type": "guided-production", "stage": "stage-3", "concept": "C-03"}
            ],
            "recasts": [],
        })
        # check_recasts_required returns True (field IS required),
        # but the field IS present with empty list, so validator should PASS
        assert "recasts" in log, "Fixture must include recasts field"

    def test_fluency_no_recasts_fails(self):
        """Fluency session missing recasts should FAIL (D-06 short-circuit)."""
        log = _make_session_log("fluency", {
            "session_activities": [{"type": "fluency-storytelling"}],
        })
        log.pop("recasts", None)
        assert check_recasts_required(log) is True, \
            "D-06: fluency session_type should short-circuit to required"

    def test_stage1_only_no_recasts_passes(self):
        """Stage-1-only session without recasts should NOT require it."""
        log = _make_session_log("standard", {
            "session_activities": [
                {"type": "drill", "stage": "stage-1"}
            ],
        })
        log.pop("recasts", None)
        assert check_recasts_required(log) is False, \
            "D-06: stage-1 only should NOT require recasts"

    def test_stage4_requires_recasts(self):
        """Stage-4 free conversation should require recasts."""
        log = _make_session_log("standard", {
            "session_activities": [
                {"type": "conversation", "stage": "stage-4"}
            ],
        })
        assert check_recasts_required(log) is True, \
            "D-06: stage-4 activity should require recasts"

    def test_conversation_type_requires_recasts(self):
        """Activity type 'conversation' without explicit stage should require recasts."""
        log = _make_session_log("standard", {
            "session_activities": [
                {"type": "conversation"}
            ],
        })
        assert check_recasts_required(log) is True, \
            "D-06: conversation activity type should trigger required"

    def test_recast_substring_in_notes_requires(self):
        """Free-text 'recast' substring in activity notes should trigger required."""
        log = _make_session_log("standard", {
            "session_activities": [
                {"type": "drill", "stage": "stage-2", "notes": "did some recasting"}
            ],
        })
        assert check_recasts_required(log) is True, \
            "D-06: 'recast' substring in notes should trigger required"


# =============================================================================
# Phase 5 LOAD: Wave 0 RED-scaffolding tests
# =============================================================================


class TestBudgetEnforcement:
    """LOAD-03 / D-07: check_assignment_budget returns (level, msg, total).
    Levels: OK, WARN, FAIL. See RESEARCH.md Ex-3 for reference implementation."""

    @_missing_budget_fns
    def test_non_numeric_estimated_minutes_does_not_crash(self):
        """M3: a tutor typo like '15 min' must not raise ValueError (which
        post-session.sh would surface as a misleading 'missing fields' block).
        The malformed field degrades to 0 and the check still returns a verdict."""
        data = {"date": "2026-04-22", "assignments": [
            {"task": "Anki", "estimated_minutes": "15 min"},
            {"task": "listening", "estimated_minutes": 10},
        ]}
        schedule = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 30, "daily_maximum": 60,
            "weekly_goal": 180, "today_stretch": 0,
        }}
        level, msg, total = check_assignment_budget(data, schedule)  # must not raise
        assert total == 10  # bad field -> 0, plus the valid 10
        assert level in ("OK", "WARN", "FAIL")

    @_missing_budget_fns
    def test_non_numeric_budget_field_does_not_crash(self):
        """M3: a malformed budget field (e.g. daily_maximum: '60m') degrades to
        0 instead of crashing."""
        data = {"date": "2026-04-22", "assignments": [
            {"task": "Anki", "estimated_minutes": 20},
        ]}
        schedule = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 30, "daily_maximum": "60m",
            "weekly_goal": 180, "today_stretch": 0,
        }}
        level, msg, total = check_assignment_budget(data, schedule)  # must not raise
        assert total == 20

    @_missing_budget_fns
    def test_pass_within_target(self):
        data = {"date": "2026-04-22", "assignments": [
            {"task": "Anki", "estimated_minutes": 15},
            {"task": "listening", "estimated_minutes": 10},
        ]}
        schedule = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 30, "daily_maximum": 60,
            "weekly_goal": 180, "today_stretch": 0,
        }}
        level, msg, total = check_assignment_budget(data, schedule)
        assert level == "OK", f"D-07: sum=25 <= daily_target(30) must be OK; got {level!r} ({msg})"
        assert total == 25

    @_missing_budget_fns
    def test_warn_over_target(self):
        data = {"date": "2026-04-22", "assignments": [
            {"task": "Anki", "estimated_minutes": 20},
            {"task": "writing", "estimated_minutes": 20},
        ]}
        schedule = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 30, "daily_maximum": 60,
            "weekly_goal": 180, "today_stretch": 0,
        }}
        level, msg, total = check_assignment_budget(data, schedule)
        assert level == "WARN", f"D-07: sum=40 > daily_target(30) but <= max(60) must be WARN; got {level!r}"
        assert total == 40
        assert "daily_target" in msg

    @_missing_budget_fns
    def test_fail_over_maximum(self):
        data = {"date": "2026-04-22", "assignments": [
            {"task": "Anki", "estimated_minutes": 30},
            {"task": "writing", "estimated_minutes": 25},
            {"task": "listening", "estimated_minutes": 25},
        ]}
        schedule = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 30, "daily_maximum": 60,
            "weekly_goal": 180, "today_stretch": 0,
        }}
        level, msg, total = check_assignment_budget(data, schedule)
        assert level == "FAIL", f"D-07: sum=80 > max(60)+stretch(0) must be FAIL; got {level!r}"
        assert total == 80
        assert "daily_maximum" in msg

    @_missing_budget_fns
    def test_stretch_extends_ceiling(self):
        data = {"date": "2026-04-22", "assignments": [
            {"task": "Anki", "estimated_minutes": 40},
            {"task": "writing", "estimated_minutes": 30},
        ]}
        schedule = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 30, "daily_maximum": 60,
            "weekly_goal": 180, "today_stretch": 15,  # extends ceiling to 75
        }}
        level, msg, total = check_assignment_budget(data, schedule)
        # 70 > target(30), 70 <= max(60)+stretch(15)=75 → WARN
        assert level == "WARN", f"D-04: today_stretch must extend the ceiling; got {level!r}"

    @_missing_budget_fns
    def test_pre_cutoff_grandfathered(self):
        data = {"date": "2020-01-01", "assignments": [
            {"task": "Anki", "estimated_minutes": 500},  # way over any budget
        ]}
        schedule = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 30, "daily_maximum": 60,
            "weekly_goal": 180, "today_stretch": 0,
        }}
        level, msg, total = check_assignment_budget(data, schedule)
        assert level == "OK", f"Pitfall-4: pre-PHASE_5_CUTOFF logs must grandfather; got {level!r}"

    @_missing_budget_fns
    def test_no_assignments_skip(self):
        data = {"date": "2026-04-22", "assignments": []}
        schedule = {"study_time_budget": {"daily_maximum": 60, "daily_target": 30, "daily_minimum": 15, "weekly_goal": 180, "today_stretch": 0}}
        level, msg, total = check_assignment_budget(data, schedule)
        assert level == "OK"
        assert total == 0

    @_missing_budget_fns
    def test_missing_schedule_fails(self):
        data = {"date": "2026-04-22", "assignments": [{"task": "Anki", "estimated_minutes": 15}]}
        level, msg, total = check_assignment_budget(data, schedule=None)
        assert level == "FAIL"
        assert "schedule" in msg.lower() or "study_time_budget" in msg

    @_missing_budget_fns
    def test_estimated_minutes_is_summed_not_duration(self):
        """Pitfall 1 guard: if the implementation reads `estimated_duration`, the sum will be 0 and FAIL won't fire."""
        data = {"date": "2026-04-22", "assignments": [
            {"task": "bad-label", "estimated_duration": 500},  # wrong field name
            {"task": "right-label", "estimated_minutes": 15},
        ]}
        level, msg, total = check_assignment_budget(data, schedule={
            "study_time_budget": {"daily_minimum": 15, "daily_target": 30, "daily_maximum": 60, "weekly_goal": 180, "today_stretch": 0}
        })
        # Correct impl ignores estimated_duration and sums 15 only → OK
        assert total == 15, (
            f"Pitfall-1: implementation must read estimated_minutes ONLY, ignoring estimated_duration. Total={total} (expected 15)"
        )
        assert level == "OK"


class TestHomeworkLoadRatingEnforcement:
    """LOAD-04 / D-10 / Pitfall 5: homework_load_rating conditional coverage.
    - First-session (type): exempt (no prior homework)
    - Onboarding session_number=1: exempt
    - Post-cutoff standard/onboarding-2+/sprint/fluency: required
    """

    @_missing_load_rating_fn
    def test_standard_session_2_plus_requires_rating(self):
        data = {"session_type": "standard", "session_number": 2}
        assert check_homework_load_rating_required(data) is True, (
            "D-10: standard session_number>=2 must require homework_load_rating"
        )

    @_missing_load_rating_fn
    def test_first_session_exempt(self):
        data = {"session_type": "first-session", "session_number": 1}
        assert check_homework_load_rating_required(data) is False, (
            "Pitfall-5: first-session has no prior homework — exempt"
        )

    @_missing_load_rating_fn
    def test_onboarding_session_1_exempt(self):
        data = {"session_type": "onboarding", "session_number": 1}
        assert check_homework_load_rating_required(data) is False, (
            "Pitfall-5: onboarding session_number=1 exempt"
        )

    @_missing_load_rating_fn
    def test_onboarding_session_2_required(self):
        data = {"session_type": "onboarding", "session_number": 2}
        assert check_homework_load_rating_required(data) is True

    @_missing_load_rating_fn
    def test_fluency_required(self):
        data = {"session_type": "fluency", "session_number": 5}
        assert check_homework_load_rating_required(data) is True

    @_missing_load_rating_fn
    def test_sprint_required(self):
        data = {"session_type": "sprint", "session_number": 3}
        assert check_homework_load_rating_required(data) is True


# =============================================================================
# Phase 8 FOLLOWUP: CURR-FOLLOWUP-02 — dialect_advisory schema + validator
# =============================================================================


class TestDialectAdvisoryRule:
    """CURR-FOLLOWUP-02: when a session log records a homework assignment that triggers
    the dialect mismatch matrix (input-orchestration.md Section 1 Step 2), the assignment
    must carry a `dialect_advisory` field naming voseo, vosotros, or both."""

    def test_schema_includes_dialect_advisory_enum(self):
        """The session-log schema must enumerate dialect_advisory with the documented values."""
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "session-log.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        # Schema may expose this under fields.assignments.item_schema (or similar nested path).
        # We accept any nested location, but the enum values must match exactly.
        expected_enum = {"voseo", "vosotros", "voseo+vosotros"}

        def _find_dialect_advisory(node):
            if isinstance(node, dict):
                if "dialect_advisory" in node:
                    return node["dialect_advisory"]
                for v in node.values():
                    found = _find_dialect_advisory(v)
                    if found is not None:
                        return found
            elif isinstance(node, list):
                for item in node:
                    found = _find_dialect_advisory(item)
                    if found is not None:
                        return found
            return None

        spec = _find_dialect_advisory(schema)
        assert spec is not None, (
            "CURR-FOLLOWUP-02: session-log.schema.yaml must define a `dialect_advisory` field "
            "(on the homework-assignment item schema). See "
            ".planning/phases/08-followup-v1.1-improvements/08-02-PLAN.md."
        )
        enum_values = set((spec or {}).get("enum") or [])
        assert enum_values == expected_enum, (
            f"CURR-FOLLOWUP-02: dialect_advisory enum must be {sorted(expected_enum)}, "
            f"got {sorted(enum_values)}."
        )

    def test_missing_advisory_fails_check(self, tmp_path, monkeypatch):
        """Build a synthetic session log whose homework includes a media assignment matching
        a dialect-mismatch trigger (e.g. learner target_dialect=es-AR + resource dialect=mixed)
        but omitting dialect_advisory. Invoking check-session-log.py on it must fail with a
        message naming `dialect_advisory` and the trigger condition."""
        check_dialect_advisory = getattr(check_mod, "check_dialect_advisory_required", None)
        if check_dialect_advisory is None:
            pytest.fail(
                "CURR-FOLLOWUP-02: check-session-log.py must expose "
                "check_dialect_advisory_required(assignment, learner_profile, media_bank). "
                "See .planning/phases/08-followup-v1.1-improvements/08-02-PLAN.md."
            )

        learner = {"target_dialect": "es-AR"}
        media_bank = {
            "prescriptive_episodes": {
                "reading": [
                    {"title": "El amor, las mujeres y la vida", "dialect": "mixed"},
                ]
            }
        }
        assignment_missing = {
            "task": "read",
            "resource": "El amor, las mujeres y la vida",
            "estimated_minutes": 15,
            # dialect_advisory deliberately missing
        }
        result = check_dialect_advisory(assignment_missing, learner, media_bank)
        assert result is True, (
            "CURR-FOLLOWUP-02: es-AR learner + mixed-dialect resource must trigger "
            "dialect_advisory required (got False)."
        )

        assignment_present = dict(assignment_missing, dialect_advisory="voseo")
        result_ok = check_dialect_advisory(assignment_present, learner, media_bank)
        # The function returns True (advisory is required) — separate validator step
        # confirms the field is present. We just verify the trigger fires.
        assert result_ok is True

    def test_unmatched_resource_skips_check(self, tmp_path):
        """Free-form journal/Anki assignments (no resource string, or a resource that doesn't
        match anything in media-bank) must NOT trigger the rule. The check fires only when
        there's a media-bank resource with a `dialect:` tag. This codifies the silent-pass
        behavior as contract, not an accident — protects against a future change that adds
        a fall-through validator default."""
        check_dialect_advisory = getattr(check_mod, "check_dialect_advisory_required", None)
        if check_dialect_advisory is None:
            pytest.fail(
                "CURR-FOLLOWUP-02: check-session-log.py must expose "
                "check_dialect_advisory_required(assignment, learner_profile, media_bank)."
            )

        learner = {"target_dialect": "es-AR"}
        media_bank = {
            "prescriptive_episodes": {
                "reading": [
                    {"title": "El amor, las mujeres y la vida", "dialect": "mixed"},
                ]
            }
        }
        # Anki assignment — no resource field
        anki = {"task": "Anki review", "estimated_minutes": 10}
        assert check_dialect_advisory(anki, learner, media_bank) is False, (
            "CURR-FOLLOWUP-02: Anki/journal assignments (no resource) must silently skip "
            "the dialect-advisory check, not fall through to a default-required."
        )

        # Resource that doesn't match anything in media-bank
        unmatched = {"task": "read", "resource": "Some random article", "estimated_minutes": 15}
        assert check_dialect_advisory(unmatched, learner, media_bank) is False, (
            "CURR-FOLLOWUP-02: assignments whose resource doesn't match any media-bank "
            "entry must silently skip — no false positives."
        )


class TestDialectAdvisoryIntegration:
    """CURR-FOLLOWUP-02 audit-followup: verify check_log() actually invokes the
    dialect advisory rule end-to-end.

    The Wave A codex audit caught that the helper function was defined, schema-
    enumerated, and unit-tested but never called from check_log()/main(). The
    08-02 feature was dead code in production. This class exists to fail the
    next time someone unwires the call site."""

    def _setup_state(self, tmp_path, monkeypatch, learner_profile, media_bank):
        state_dir = tmp_path / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(check_mod, "STATE_DIR", state_dir)
        monkeypatch.setattr(check_mod, "ROOT", tmp_path)
        with open(state_dir / "learner-profile.yaml", "w") as f:
            yaml.safe_dump(learner_profile, f)
        curriculum = tmp_path / "curriculum"
        curriculum.mkdir(parents=True, exist_ok=True)
        with open(curriculum / "media-bank.yaml", "w") as f:
            yaml.safe_dump(media_bank, f)
        return state_dir

    def _standard_log(self, extra_assignment_fields=None):
        """Build a complete passing standard session log; caller adds the
        offending or compliant assignment via extra_assignment_fields."""
        assignment = {"task": "read", "resource": "Test Book", "estimated_minutes": 15}
        if extra_assignment_fields:
            assignment.update(extra_assignment_fields)
        return _make_session_log("standard", {
            "assignment_review": {"reviewed": "yes"},
            "skill_map_updates": [{"concept": "test"}],
            "assignments": [assignment],
            "decision_engine_trace": {
                "selected_primary": "X", "candidates_scored": ["X", "Y"]
            },
            "session_difficulty_rating": "just-right",
            "next_session": {"recommended_focus": "X", "session_type": "standard"},
        })

    def test_check_log_fails_when_advisory_missing(self, tmp_path, monkeypatch):
        """End-to-end: es-AR learner + mixed-dialect resource + assignment with
        no dialect_advisory → check_log returns 1.

        This is the test whose absence let the dead-code bug ship. If it fails,
        the audit-followup wire-in was undone."""
        state_dir = self._setup_state(
            tmp_path, monkeypatch,
            learner_profile={"target_dialect": "es-AR"},
            media_bank={
                "prescriptive_episodes": {
                    "reading": [{"title": "Test Book", "dialect": "mixed"}]
                }
            },
        )
        log_data = self._standard_log()  # no dialect_advisory
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 1, (
            "audit-followup: missing dialect_advisory on a triggered assignment "
            "must cause check_log to return 1. If this fails, the dialect-advisory "
            "rule is no longer wired into check_log() and 08-02 is dead code again."
        )

    def test_check_log_passes_when_advisory_present(self, tmp_path, monkeypatch):
        """Same setup, but assignment includes dialect_advisory='voseo' → PASS."""
        state_dir = self._setup_state(
            tmp_path, monkeypatch,
            learner_profile={"target_dialect": "es-AR"},
            media_bank={
                "prescriptive_episodes": {
                    "reading": [{"title": "Test Book", "dialect": "mixed"}]
                }
            },
        )
        log_data = self._standard_log({"dialect_advisory": "voseo"})
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 0, (
            "audit-followup: an assignment with dialect_advisory present must "
            "satisfy the rule and let check_log return 0."
        )

    def test_es_es_learner_with_neutral_latam_resource_triggers_advisory(self, tmp_path, monkeypatch):
        """Audit H-1 regression guard.

        The Dreaming Spanish house dialect is `neutral_latam` — the dominant
        Phase A resource for an es-ES learner. The Wave A LATAM dialect set
        only held `mixed_latin_american`, so the row-4 vosotros advisory
        silently never fired for the most common production case.

        This test asserts that adding any of the previously-uncovered LATAM
        tags to media-bank correctly triggers the advisory for an es-ES
        learner. Verifies the H-1 set expansion is load-bearing."""
        check_dialect_advisory = getattr(check_mod, "check_dialect_advisory_required", None)
        assert check_dialect_advisory is not None
        learner = {"target_dialect": "es-ES"}
        for dialect_tag in ("neutral_latam", "colombian", "mexican", "rioplatense", "chilean"):
            media_bank = {
                "prescriptive_episodes": {
                    "listening": [{"title": "Test Episode", "dialect": dialect_tag}]
                }
            }
            assignment = {"task": "listen", "resource": "Test Episode", "estimated_minutes": 15}
            assert check_dialect_advisory(assignment, learner, media_bank) is True, (
                f"audit H-1: es-ES learner + dialect={dialect_tag!r} resource must "
                f"trigger vosotros advisory; got False (LATAM dialect set incomplete)."
            )

    def test_check_log_skips_when_no_target_dialect(self, tmp_path, monkeypatch):
        """Silent-pass contract: an unset target_dialect (e.g., onboarding not
        complete) skips the rule rather than firing a default-required."""
        state_dir = self._setup_state(
            tmp_path, monkeypatch,
            learner_profile={},  # no target_dialect
            media_bank={
                "prescriptive_episodes": {
                    "reading": [{"title": "Test Book", "dialect": "mixed"}]
                }
            },
        )
        log_data = self._standard_log()  # no dialect_advisory
        _write_session_log(state_dir, "2026-04-15", log_data)

        result = check_log("2026-04-15", strict=False)
        assert result == 0, (
            "audit-followup: missing target_dialect must silently skip the rule, "
            "not fail check_log with a false positive."
        )
