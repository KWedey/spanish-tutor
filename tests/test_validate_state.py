"""Tests for scripts/validate-state.py validation functions."""
import copy
import sys
from pathlib import Path

import pytest
import yaml

# Ensure scripts/ is importable
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# We need to set up ROOT/STATE before importing validate-state functions
# because the module references STATE at import time.
import importlib

# Import the module with hyphens via importlib
validate_mod = importlib.import_module("validate-state")

# Grab references to functions and the results list
results = validate_mod.results
pass_ = validate_mod.pass_
warn = validate_mod.warn
fail = validate_mod.fail
load_yaml = validate_mod.load_yaml
check_acquired_consistency = validate_mod.check_acquired_consistency
check_performance_enums = validate_mod.check_performance_enums
check_schedule_enums = validate_mod.check_schedule_enums
check_receptive_skills = validate_mod.check_receptive_skills
check_vocab_error_tracking = validate_mod.check_vocab_error_tracking
check_resource_tracker = validate_mod.check_resource_tracker
check_vocab_passive_active = validate_mod.check_vocab_passive_active
check_acquired_zero_practice = validate_mod.check_acquired_zero_practice


@pytest.fixture(autouse=True)
def clear_results():
    """Clear the module-level results list before each test."""
    results.clear()
    yield
    results.clear()


def _fails():
    return [msg for lvl, msg in results if lvl == "FAIL"]


def _warns():
    return [msg for lvl, msg in results if lvl == "WARN"]


def _passes():
    return [msg for lvl, msg in results if lvl == "PASS"]


# ---------------------------------------------------------------------------
# 1. acquired + high error rate
# ---------------------------------------------------------------------------

class TestAcquiredHighErrorRate:
    def test_acquired_high_error_rate_fails(self, skill_map_data):
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"
        sm["grammar"]["A-01-present-regular"]["error_rate_production"] = 0.40
        sm["grammar"]["A-01-present-regular"]["performance_unscaffolded"] = "competent"

        check_acquired_consistency(sm)

        fails = _fails()
        assert len(fails) >= 1
        assert any("error_rate_production=0.4" in f for f in fails)


# ---------------------------------------------------------------------------
# 2. acquired + unscaffolded != competent
# ---------------------------------------------------------------------------

class TestAcquiredUnscaffoldedNotCompetent:
    def test_acquired_struggling_unscaffolded_fails(self, skill_map_data):
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"
        sm["grammar"]["A-01-present-regular"]["error_rate_production"] = 0.05
        sm["grammar"]["A-01-present-regular"]["performance_unscaffolded"] = "struggling"

        check_acquired_consistency(sm)

        fails = _fails()
        assert len(fails) >= 1
        assert any("performance_unscaffolded='struggling'" in f for f in fails)


# ---------------------------------------------------------------------------
# 3. acquired + zero practice (non-exempt)
# ---------------------------------------------------------------------------

class TestAcquiredZeroPractice:
    def test_acquired_zero_practice_warns(self, skill_map_data):
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"
        sm["grammar"]["A-01-present-regular"]["practice_count"] = 0

        profile = {"initial_placement": {"level": None}}
        check_acquired_zero_practice(sm, profile)

        warns = _warns()
        assert len(warns) >= 1
        assert any("practice_count=0" in w for w in warns)


# ---------------------------------------------------------------------------
# 4. receptive_skills invalid listening level
# ---------------------------------------------------------------------------

class TestReceptiveSkillsInvalidLevel:
    def test_invalid_listening_level_fails(self, skill_map_data):
        sm = skill_map_data
        sm["receptive_skills"]["listening"]["current_level"] = "L9"

        check_receptive_skills(sm)

        fails = _fails()
        assert len(fails) >= 1
        assert any("L9" in f for f in fails)


# ---------------------------------------------------------------------------
# 5. vocab error_tracking out of range
# ---------------------------------------------------------------------------

class TestVocabErrorTrackingOutOfRange:
    def test_error_rate_above_one_fails(self, skill_map_data):
        sm = skill_map_data
        sm["vocabulary"]["tier1-greetings-introductions"]["error_tracking"] = {
            "error_rate_production": 1.5,
            "common_errors": [],
        }

        check_vocab_error_tracking(sm)

        fails = _fails()
        assert len(fails) >= 1
        assert any("1.5" in f for f in fails)


# ---------------------------------------------------------------------------
# 6. resource-tracker invalid type
# ---------------------------------------------------------------------------

class TestResourceTrackerInvalidType:
    def test_invalid_resource_type_fails(self, resource_tracker_data):
        rt = resource_tracker_data
        rt["resources"] = [{"name": "Bad Resource", "type": "video"}]

        check_resource_tracker(rt)

        fails = _fails()
        assert len(fails) >= 1
        assert any("video" in f for f in fails)


# ---------------------------------------------------------------------------
# 7. Clean state passes (0 failures)
# ---------------------------------------------------------------------------

class TestCleanState:
    def test_clean_state_zero_failures(self, skill_map_data, resource_tracker_data):
        check_acquired_consistency(skill_map_data)
        check_performance_enums(skill_map_data)
        check_vocab_passive_active(skill_map_data)
        check_receptive_skills(skill_map_data)
        check_vocab_error_tracking(skill_map_data)
        check_resource_tracker(resource_tracker_data)

        fails = _fails()
        assert len(fails) == 0, f"Clean state produced failures: {fails}"


# ---------------------------------------------------------------------------
# 8. Missing file
# ---------------------------------------------------------------------------

class TestMissingFile:
    def test_missing_file_fails(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "ROOT", tmp_path)
        nonexistent = tmp_path / "does-not-exist.yaml"
        result = load_yaml(nonexistent)

        assert result is None
        fails = _fails()
        assert len(fails) >= 1
        assert any("Missing file" in f for f in fails)


# ---------------------------------------------------------------------------
# 9. YAML syntax error
# ---------------------------------------------------------------------------

class TestYAMLSyntaxError:
    def test_malformed_yaml_fails(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "ROOT", tmp_path)
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("key: [unterminated", encoding="utf-8")
        result = load_yaml(bad_yaml)

        assert result is None
        fails = _fails()
        assert len(fails) >= 1
        assert any("YAML syntax error" in f for f in fails)


# ---------------------------------------------------------------------------
# 10. passive_known < active_known
# ---------------------------------------------------------------------------

class TestPassiveActiveMismatch:
    def test_passive_less_than_active_fails(self, skill_map_data):
        sm = skill_map_data
        sm["vocabulary"]["tier1-greetings-introductions"]["passive_known"] = 2
        sm["vocabulary"]["tier1-greetings-introductions"]["active_known"] = 10

        check_vocab_passive_active(sm)

        fails = _fails()
        assert len(fails) >= 1
        assert any("passive_known (2) < active_known (10)" in f for f in fails)


# ---------------------------------------------------------------------------
# 11. performance enum validation — invalid value
# ---------------------------------------------------------------------------

class TestPerformanceEnumValidation:
    def test_invalid_performance_value_fails(self, skill_map_data):
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["performance_scaffolded"] = "excellent"

        check_performance_enums(sm)

        fails = _fails()
        assert len(fails) >= 1
        assert any("excellent" in f for f in fails)


# ---------------------------------------------------------------------------
# 12. schedule enum validation — invalid phase
# ---------------------------------------------------------------------------

class TestScheduleEnumValidation:
    def test_invalid_phase_fails(self):
        sched = {"current_phase": "E-expert", "fluency_accuracy_balance": "balanced", "current_week": 1}

        check_schedule_enums(sched)

        fails = _fails()
        assert len(fails) >= 1
        assert any("E-expert" in f for f in fails)
