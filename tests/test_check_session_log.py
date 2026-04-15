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

    def test_schema_has_exactly_nine_values(self):
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "session-log.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        enum_values = schema["fields"]["session_type"]["enum"]
        assert len(enum_values) == 9, (
            f"Expected 9 session_type enum values, got {len(enum_values)}: {enum_values}"
        )


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
