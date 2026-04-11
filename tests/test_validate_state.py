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

# Grab references to the ValidationResults instance and functions
results = validate_mod.results
load_yaml_validated = validate_mod.load_yaml_validated
check_acquired_consistency = validate_mod.check_acquired_consistency
check_performance_enums = validate_mod.check_performance_enums
check_schedule_enums = validate_mod.check_schedule_enums
check_receptive_skills = validate_mod.check_receptive_skills
check_vocab_error_tracking = validate_mod.check_vocab_error_tracking
check_resource_tracker = validate_mod.check_resource_tracker
check_vocab_passive_active = validate_mod.check_vocab_passive_active
check_acquired_zero_practice = validate_mod.check_acquired_zero_practice
check_session_filenames = validate_mod.check_session_filenames
check_carryover_concepts = validate_mod.check_carryover_concepts
check_placement_validation_consistency = validate_mod.check_placement_validation_consistency
check_integration_tested_with = validate_mod.check_integration_tested_with
check_schedule_refs = validate_mod.check_schedule_refs
check_session_logs = validate_mod.check_session_logs
check_resource_skill_map_levels = validate_mod.check_resource_skill_map_levels
check_curriculum_cross_refs = validate_mod.check_curriculum_cross_refs


@pytest.fixture(autouse=True)
def clear_results():
    """Clear the module-level results before each test."""
    results.clear()
    yield
    results.clear()


def _fails():
    return [msg for lvl, msg in results.items if lvl == "FAIL"]


def _warns():
    return [msg for lvl, msg in results.items if lvl == "WARN"]


def _passes():
    return [msg for lvl, msg in results.items if lvl == "PASS"]


# ---------------------------------------------------------------------------
# 1. acquired + high error rate
# ---------------------------------------------------------------------------

class TestAcquiredHighErrorRate:
    def test_acquired_high_error_rate_fails(self, skill_map_data):
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"
        sm["grammar"]["A-01-present-regular"]["error_rate_production"] = 0.40
        sm["grammar"]["A-01-present-regular"]["performance_unscaffolded"] = "competent"

        check_acquired_consistency(sm, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("error_rate_production=0.4" in f for f in fails)

    def test_acquired_error_at_boundary_fails(self, skill_map_data):
        """E-05: error > 0.10 should fail (was > 0.15 before)."""
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"
        sm["grammar"]["A-01-present-regular"]["error_rate_production"] = 0.12
        sm["grammar"]["A-01-present-regular"]["performance_unscaffolded"] = "competent"

        check_acquired_consistency(sm, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("0.12" in f for f in fails)

    def test_acquired_error_at_ten_percent_passes(self, skill_map_data):
        """E-05: error == 0.10 should pass (boundary)."""
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"
        sm["grammar"]["A-01-present-regular"]["error_rate_production"] = 0.10
        sm["grammar"]["A-01-present-regular"]["performance_unscaffolded"] = "competent"

        check_acquired_consistency(sm, results)

        fails = _fails()
        assert len(fails) == 0


# ---------------------------------------------------------------------------
# 2. acquired + unscaffolded != competent
# ---------------------------------------------------------------------------

class TestAcquiredUnscaffoldedNotCompetent:
    def test_acquired_struggling_unscaffolded_fails(self, skill_map_data):
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"
        sm["grammar"]["A-01-present-regular"]["error_rate_production"] = 0.05
        sm["grammar"]["A-01-present-regular"]["performance_unscaffolded"] = "struggling"

        check_acquired_consistency(sm, results)

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
        check_acquired_zero_practice(sm, profile, results)

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

        check_receptive_skills(sm, results)

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

        check_vocab_error_tracking(sm, results)

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

        check_resource_tracker(rt, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("video" in f for f in fails)


# ---------------------------------------------------------------------------
# 7. Clean state passes (0 failures)
# ---------------------------------------------------------------------------

class TestCleanState:
    def test_clean_state_zero_failures(self, skill_map_data, resource_tracker_data):
        check_acquired_consistency(skill_map_data, results)
        check_performance_enums(skill_map_data, results)
        check_vocab_passive_active(skill_map_data, results)
        check_receptive_skills(skill_map_data, results)
        check_vocab_error_tracking(skill_map_data, results)
        check_resource_tracker(resource_tracker_data, results)

        fails = _fails()
        assert len(fails) == 0, f"Clean state produced failures: {fails}"


# ---------------------------------------------------------------------------
# 8. Missing file
# ---------------------------------------------------------------------------

class TestMissingFile:
    def test_missing_file_fails(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "ROOT", tmp_path)
        nonexistent = tmp_path / "does-not-exist.yaml"
        result = load_yaml_validated(nonexistent, results)

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
        result = load_yaml_validated(bad_yaml, results)

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

        check_vocab_passive_active(sm, results)

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

        check_performance_enums(sm, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("excellent" in f for f in fails)


# ---------------------------------------------------------------------------
# 12. schedule enum validation — invalid phase
# ---------------------------------------------------------------------------

class TestScheduleEnumValidation:
    def test_invalid_phase_fails(self):
        sched = {"current_phase": "E-expert", "fluency_accuracy_balance": "balanced", "current_week": 1}

        check_schedule_enums(sched, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("E-expert" in f for f in fails)


# ---------------------------------------------------------------------------
# 13. session filename validation — non-date filename warns
# ---------------------------------------------------------------------------

class TestSessionFilenameNonDate:
    def test_non_date_filename_warns(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "STATE", tmp_path)
        sdir = tmp_path / "sessions"
        sdir.mkdir()
        (sdir / "notes.yaml").write_text("key: value", encoding="utf-8")

        check_session_filenames(results)

        warns = _warns()
        assert len(warns) >= 1
        assert any("notes.yaml" in w for w in warns)


# ---------------------------------------------------------------------------
# 14. carryover concept with acquired status warns
# ---------------------------------------------------------------------------

class TestCarryoverAcquiredWarns:
    def test_acquired_in_carryover_warns(self, skill_map_data):
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"

        sched = {"carryover_concepts": ["A-01-present-regular"]}

        check_carryover_concepts(sched, sm, results)

        warns = _warns()
        assert len(warns) >= 1
        assert any("acquired" in w for w in warns)


# ---------------------------------------------------------------------------
# 15. placement_validation active with onboarding incomplete fails
# ---------------------------------------------------------------------------

class TestPlacementValidationOnboardingIncomplete:
    def test_active_pv_onboarding_false_fails(self):
        sched = {
            "placement_validation": {"active": True, "sessions_completed": 0},
            "onboarding_complete": False,
        }

        check_placement_validation_consistency(sched, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("onboarding" in f.lower() for f in fails)


# ---------------------------------------------------------------------------
# 16. integration_tested_with references non-existent concept
# ---------------------------------------------------------------------------

class TestIntegrationTestedWithBadRef:
    def test_nonexistent_ref_fails(self, skill_map_data):
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["integration_tested_with"] = ["Z-99-fake-concept"]

        check_integration_tested_with(sm, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("Z-99-fake-concept" in f for f in fails)


# ---------------------------------------------------------------------------
# 17. schedule active_grammar.primary references missing concept
# ---------------------------------------------------------------------------

class TestScheduleRefsMissingConcept:
    def test_primary_not_in_skill_map_fails(self, skill_map_data):
        sched = {"active_grammar": {"primary": "X-99-nonexistent"}}

        check_schedule_refs(sched, skill_map_data, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("X-99-nonexistent" in f for f in fails)


# ---------------------------------------------------------------------------
# 18. E-29: schedule secondary/maintenance/vocab/pronunciation cross-refs
# ---------------------------------------------------------------------------

class TestScheduleRefsExtended:
    def test_secondary_not_in_skill_map_fails(self, skill_map_data):
        sched = {"active_grammar": {"secondary": "X-99-nonexistent"}}

        check_schedule_refs(sched, skill_map_data, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("secondary" in f and "X-99-nonexistent" in f for f in fails)

    def test_maintenance_not_in_skill_map_fails(self, skill_map_data):
        sched = {"active_grammar": {"maintenance": ["X-99-nonexistent"]}}

        check_schedule_refs(sched, skill_map_data, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("maintenance" in f and "X-99-nonexistent" in f for f in fails)

    def test_vocabulary_primary_not_in_skill_map_fails(self, skill_map_data):
        sched = {"active_grammar": {}, "active_vocabulary": {"primary": "tier9-fake"}}

        check_schedule_refs(sched, skill_map_data, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("active_vocabulary.primary" in f and "tier9-fake" in f for f in fails)

    def test_pronunciation_not_in_skill_map_fails(self, skill_map_data):
        sched = {"active_grammar": {}, "active_pronunciation": {"focus": "fake-sound"}}

        check_schedule_refs(sched, skill_map_data, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("active_pronunciation.focus" in f and "fake-sound" in f for f in fails)

    def test_valid_refs_pass(self, skill_map_data):
        sched = {
            "active_grammar": {
                "primary": "A-01-present-regular",
                "secondary": "B-01-preterite-regular",
                "maintenance": ["A-01-present-regular"],
            },
            "active_vocabulary": {"primary": "tier1-greetings-introductions"},
            "active_pronunciation": {"focus": "vowel-sounds"},
        }

        check_schedule_refs(sched, skill_map_data, results)

        fails = _fails()
        assert len(fails) == 0


# ---------------------------------------------------------------------------
# 19. E-30: resource-tracker / skill-map cross-validation
# ---------------------------------------------------------------------------

class TestResourceSkillMapLevels:
    def test_mismatched_listening_level_warns(self, skill_map_data, resource_tracker_data):
        resource_tracker_data["input_summary"]["current_listening_level"] = "L3"
        skill_map_data["receptive_skills"]["listening"]["current_level"] = "L1"

        check_resource_skill_map_levels(resource_tracker_data, skill_map_data, results)

        warns = _warns()
        assert len(warns) >= 1
        assert any("listening" in w and "L3" in w and "L1" in w for w in warns)

    def test_mismatched_reading_level_warns(self, skill_map_data, resource_tracker_data):
        resource_tracker_data["input_summary"]["current_reading_level"] = "R4"
        skill_map_data["receptive_skills"]["reading"]["current_level"] = "R1"

        check_resource_skill_map_levels(resource_tracker_data, skill_map_data, results)

        warns = _warns()
        assert len(warns) >= 1
        assert any("reading" in w and "R4" in w and "R1" in w for w in warns)

    def test_matching_levels_pass(self, skill_map_data, resource_tracker_data):
        check_resource_skill_map_levels(resource_tracker_data, skill_map_data, results)

        warns = _warns()
        level_warns = [w for w in warns if "Receptive skill level mismatch" in w]
        assert len(level_warns) == 0


# ---------------------------------------------------------------------------
# 20. E-03: session log validation
# ---------------------------------------------------------------------------

class TestSessionLogValidation:
    def test_valid_session_log_passes(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "STATE", tmp_path)
        sdir = tmp_path / "sessions"
        sdir.mkdir()
        log = {
            "date": "2026-04-10",
            "session_number": 1,
            "duration_minutes": 30,
            "session_type": "standard",
            "session_status": "complete",
        }
        (sdir / "2026-04-10.yaml").write_text(
            yaml.dump(log, default_flow_style=False), encoding="utf-8"
        )

        check_session_logs(results)

        fails = _fails()
        assert len(fails) == 0

    def test_missing_required_field_fails(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "STATE", tmp_path)
        sdir = tmp_path / "sessions"
        sdir.mkdir()
        log = {
            "date": "2026-04-10",
            # missing session_number, duration_minutes, session_type, session_status
        }
        (sdir / "2026-04-10.yaml").write_text(
            yaml.dump(log, default_flow_style=False), encoding="utf-8"
        )

        check_session_logs(results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("missing required field" in f for f in fails)

    def test_invalid_enum_value_fails(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "STATE", tmp_path)
        sdir = tmp_path / "sessions"
        sdir.mkdir()
        log = {
            "date": "2026-04-10",
            "session_number": 1,
            "duration_minutes": 30,
            "session_type": "invalid-type",
            "session_status": "complete",
        }
        (sdir / "2026-04-10.yaml").write_text(
            yaml.dump(log, default_flow_style=False), encoding="utf-8"
        )

        check_session_logs(results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("invalid-type" in f for f in fails)

    def test_archive_dir_skipped(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "STATE", tmp_path)
        sdir = tmp_path / "sessions"
        sdir.mkdir()
        archive = sdir / "archive"
        archive.mkdir()
        # Put a bad file in archive — should not be checked
        (archive / "2020-01-01.yaml").write_text("not: valid: yaml: [", encoding="utf-8")

        check_session_logs(results)

        fails = _fails()
        assert len(fails) == 0


# ---------------------------------------------------------------------------
# 21. S-18: pronunciation cross-reference validation
# ---------------------------------------------------------------------------

class TestPronunciationCrossRef:
    def test_missing_pronunciation_file_fails(self, skill_map_data, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "CURRICULUM", tmp_path / "curriculum")
        monkeypatch.setattr(validate_mod, "ROOT", tmp_path)
        (tmp_path / "curriculum" / "pronunciation").mkdir(parents=True)

        sched = {"active_pronunciation": {"focus": "nonexistent-sound"}}

        check_curriculum_cross_refs(skill_map_data, sched, results)

        fails = _fails()
        assert any("nonexistent-sound" in f for f in fails)
