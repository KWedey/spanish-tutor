"""Tests for scripts/validate-state.py validation functions.

scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
"""
import copy
from pathlib import Path

import pytest
import yaml

# We need to set up ROOT/STATE before importing validate-state functions
# because the module references STATE at import time.
import importlib

# Import the module with hyphens via importlib
validate_mod = importlib.import_module("validate-state")

# Grab references to the ValidationResults instance and functions
results = validate_mod.results
load_yaml_validated = validate_mod.load_yaml_validated
check_required_fields = validate_mod.check_required_fields
check_learner_profile = validate_mod.check_learner_profile
check_skill_map = validate_mod.check_skill_map
check_schedule = validate_mod.check_schedule
check_system_health = validate_mod.check_system_health
check_acquired_consistency = validate_mod.check_acquired_consistency
check_performance_enums = validate_mod.check_performance_enums
check_schedule_enums = validate_mod.check_schedule_enums
check_onboarding_counter_range = validate_mod.check_onboarding_counter_range
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

# Hard references — these validators shipped long ago. Binding them directly
# (not via getattr-with-default + skipif) means a rename or deletion fails LOUD
# at collection instead of silently skipping the gated tests. The old RED-phase
# scaffolding was a permanent silent-pass channel once the code landed —
# exactly the project's tested-but-unwired defect, in the harness itself.
check_learner_interest_range = validate_mod.check_learner_interest_range
check_recast_uptake_stats_consistency = validate_mod.check_recast_uptake_stats_consistency
check_learner_interest_staleness = validate_mod.check_learner_interest_staleness
check_study_time_budget_consistency = validate_mod.check_study_time_budget_consistency
check_daily_target_tier_drift = validate_mod.check_daily_target_tier_drift
check_just_right_restore_drift = validate_mod.check_just_right_restore_drift


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
# 1b. acquired + high error_rate_drills (ENFORCE-07)
# ---------------------------------------------------------------------------

class TestAcquiredHighErrorRateDrills:
    def test_drills_0_40_fails(self, skill_map_data):
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"
        sm["grammar"]["A-01-present-regular"]["error_rate_drills"] = 0.40
        sm["grammar"]["A-01-present-regular"]["error_rate_production"] = 0.05
        sm["grammar"]["A-01-present-regular"]["performance_unscaffolded"] = "competent"

        check_acquired_consistency(sm, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("error_rate_drills=0.4" in f for f in fails)

    def test_drills_0_12_fails(self, skill_map_data):
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"
        sm["grammar"]["A-01-present-regular"]["error_rate_drills"] = 0.12
        sm["grammar"]["A-01-present-regular"]["error_rate_production"] = 0.05
        sm["grammar"]["A-01-present-regular"]["performance_unscaffolded"] = "competent"

        check_acquired_consistency(sm, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("0.12" in f for f in fails)

    def test_drills_0_10_boundary_passes(self, skill_map_data):
        """ENFORCE-07: error_rate_drills == 0.10 should pass (threshold is >, not >=)."""
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["status"] = "acquired"
        sm["grammar"]["A-01-present-regular"]["error_rate_drills"] = 0.10
        sm["grammar"]["A-01-present-regular"]["error_rate_production"] = 0.05
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
# 12b. onboarding counter range (C1 fix — guards the never-incremented stall)
# ---------------------------------------------------------------------------

class TestOnboardingCounterRange:
    def test_counter_one_in_progress_passes(self):
        # Seed state: onboarding in progress, counter at 1 — valid (pre/at session 1)
        check_onboarding_counter_range(
            {"onboarding_complete": False, "current_onboarding_session": 1}, results
        )
        assert len(_fails()) == 0

    def test_counter_in_range_passes(self):
        check_onboarding_counter_range(
            {"onboarding_complete": False, "current_onboarding_session": 7}, results
        )
        assert len(_fails()) == 0

    def test_counter_above_range_fails(self):
        check_onboarding_counter_range(
            {"onboarding_complete": False, "current_onboarding_session": 11}, results
        )
        fails = _fails()
        assert len(fails) >= 1
        assert any("11" in f for f in fails)

    def test_counter_zero_fails(self):
        check_onboarding_counter_range(
            {"onboarding_complete": False, "current_onboarding_session": 0}, results
        )
        assert len(_fails()) >= 1

    def test_counter_unconstrained_when_complete(self):
        # Once onboarding_complete, the counter is unused — even 11 is fine
        check_onboarding_counter_range(
            {"onboarding_complete": True, "current_onboarding_session": 11}, results
        )
        assert len(_fails()) == 0

    def test_counter_null_pre_first_session_passes(self):
        check_onboarding_counter_range(
            {"onboarding_complete": False, "current_onboarding_session": None}, results
        )
        assert len(_fails()) == 0


# ---------------------------------------------------------------------------
# 12c. nested enum validation in session logs (M10)
# ---------------------------------------------------------------------------

class TestSessionLogNestedEnums:
    def _write_log(self, tmp_path, monkeypatch, log: dict):
        monkeypatch.setattr(validate_mod, "STATE", tmp_path)
        sdir = tmp_path / "sessions"
        sdir.mkdir()
        (sdir / "2026-06-03.yaml").write_text(yaml.safe_dump(log), encoding="utf-8")

    def _valid_base(self):
        return {
            "date": "2026-06-03", "session_number": 2, "duration_minutes": 30,
            "session_type": "standard", "session_status": "complete",
            "learner_energy": "medium", "session_activities": [],
            "learner_observations": {"mood": "ok", "engagement": "high"},
        }

    def test_bad_recast_uptake_fails(self, tmp_path, monkeypatch):
        log = self._valid_base()
        log["recasts"] = [{"concept_id": "A-01", "error_form": "x",
                           "corrected_form": "y", "uptake": "YES"}]
        self._write_log(tmp_path, monkeypatch, log)
        check_session_logs(results)
        assert any("uptake" in f and "YES" in f for f in _fails())

    def test_valid_recast_uptake_passes(self, tmp_path, monkeypatch):
        log = self._valid_base()
        log["recasts"] = [{"concept_id": "A-01", "error_form": "x",
                           "corrected_form": "y", "uptake": "landed"}]
        self._write_log(tmp_path, monkeypatch, log)
        check_session_logs(results)
        assert not any("uptake" in f for f in _fails())

    def test_bad_dialect_advisory_fails(self, tmp_path, monkeypatch):
        log = self._valid_base()
        log["assignments"] = [{"task": "x", "type": "writing",
                               "estimated_minutes": 10, "dialect_advisory": "klingon"}]
        self._write_log(tmp_path, monkeypatch, log)
        check_session_logs(results)
        assert any("dialect_advisory" in f and "klingon" in f for f in _fails())


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


# ---------------------------------------------------------------------------
# 22. E-16: check_required_fields — generic required-field checker
# ---------------------------------------------------------------------------

class TestCheckRequiredFields:
    def test_all_required_fields_present_passes(self, system_health_data):
        check_required_fields(system_health_data, "system-health", "system-health", results)

        fails = _fails()
        assert len(fails) == 0
        passes = _passes()
        assert any("required fields present" in p for p in passes)

    def test_missing_required_field_fails(self):
        # system-health has ~15 required fields; provide only schema_version
        data = {"schema_version": 1}
        check_required_fields(data, "system-health", "system-health", results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("missing required field" in f for f in fails)

    def test_reports_each_missing_field(self):
        data = {}  # missing everything including schema_version
        check_required_fields(data, "learner-profile", "learner-profile", results)

        fails = _fails()
        # learner-profile requires: schema_version, name, native_language, target_dialect
        assert len(fails) >= 4
        assert any("schema_version" in f for f in fails)
        assert any("name" in f for f in fails)


# ---------------------------------------------------------------------------
# 23. E-16: check_learner_profile
# ---------------------------------------------------------------------------

class TestCheckLearnerProfile:
    def test_valid_profile_passes(self, profile_data):
        check_learner_profile(profile_data, has_sessions=False, res=results)

        fails = _fails()
        assert len(fails) == 0

    def test_missing_required_field_fails(self):
        data = {"schema_version": 1}  # missing name, native_language, target_dialect
        check_learner_profile(data, has_sessions=False, res=results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("missing required field" in f for f in fails)

    def test_empty_name_after_session_warns(self, profile_data):
        profile_data["name"] = ""
        check_learner_profile(profile_data, has_sessions=True, res=results)

        warns = _warns()
        assert any("'name' is empty" in w for w in warns)

    def test_empty_name_before_sessions_no_warn(self, profile_data):
        profile_data["name"] = ""
        check_learner_profile(profile_data, has_sessions=False, res=results)

        warns = _warns()
        assert not any("'name' is empty" in w for w in warns)

    def test_empty_target_dialect_after_session_warns(self, profile_data):
        profile_data["target_dialect"] = ""
        check_learner_profile(profile_data, has_sessions=True, res=results)

        warns = _warns()
        assert any("'target_dialect' is empty" in w for w in warns)


# ---------------------------------------------------------------------------
# 24. E-16: check_schedule
# ---------------------------------------------------------------------------

class TestCheckSchedule:
    def test_valid_schedule_passes(self, schedule_data):
        check_schedule(schedule_data, results)

        fails = _fails()
        assert len(fails) == 0

    def test_missing_required_field_fails(self):
        data = {"schema_version": 1}  # missing current_phase, current_week, onboarding_complete, fluency_accuracy_balance
        check_schedule(data, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("missing required field" in f for f in fails)

    def test_missing_all_fields_reports_multiple(self):
        data = {}
        check_schedule(data, results)

        fails = _fails()
        # schedule requires: schema_version, current_phase, current_week,
        # onboarding_complete, fluency_accuracy_balance
        assert len(fails) >= 5


# ---------------------------------------------------------------------------
# 25. E-16: check_system_health
# ---------------------------------------------------------------------------

class TestCheckSystemHealth:
    def test_valid_system_health_passes(self, system_health_data):
        check_system_health(system_health_data, results)

        fails = _fails()
        assert len(fails) == 0

    def test_missing_required_field_fails(self):
        data = {"schema_version": 1}
        check_system_health(data, results)

        fails = _fails()
        assert len(fails) >= 1
        assert any("missing required field" in f for f in fails)

    def test_missing_all_fields_reports_many(self):
        data = {}
        check_system_health(data, results)

        fails = _fails()
        # system-health has ~16 required fields
        assert len(fails) >= 15


# ---------------------------------------------------------------------------
# 26. E-16: check_curriculum_cross_refs (additional coverage)
# ---------------------------------------------------------------------------

class TestCurriculumCrossRefsExtended:
    def test_no_schedule_still_checks_grammar_vocab(self, skill_map_data, tmp_path, monkeypatch):
        """Cross-refs should check grammar/vocab even when schedule is None."""
        monkeypatch.setattr(validate_mod, "CURRICULUM", tmp_path / "curriculum")
        monkeypatch.setattr(validate_mod, "ROOT", tmp_path)

        check_curriculum_cross_refs(skill_map_data, None, results)

        # With no curriculum files on disk, grammar concepts should fail
        fails = _fails()
        assert any("A-01-present-regular" in f or "curriculum file" in f for f in fails)

    def test_existing_pronunciation_file_passes(self, skill_map_data, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "CURRICULUM", tmp_path / "curriculum")
        monkeypatch.setattr(validate_mod, "ROOT", tmp_path)
        pron_dir = tmp_path / "curriculum" / "pronunciation"
        pron_dir.mkdir(parents=True)
        (pron_dir / "vowel-sounds.md").write_text("# Vowel Sounds", encoding="utf-8")

        sched = {"active_pronunciation": {"focus": "vowel-sounds"}}

        check_curriculum_cross_refs(skill_map_data, sched, results)

        passes = _passes()
        assert any("vowel-sounds" in p for p in passes)


# ---------------------------------------------------------------------------
# 27. E-03: session log validation (additional: empty sessions directory)
# ---------------------------------------------------------------------------

class TestSessionLogEmpty:
    def test_empty_sessions_dir_passes(self, tmp_path, monkeypatch):
        monkeypatch.setattr(validate_mod, "STATE", tmp_path)
        sdir = tmp_path / "sessions"
        sdir.mkdir()

        check_session_logs(results)

        fails = _fails()
        assert len(fails) == 0
        passes = _passes()
        assert any("No session logs to validate" in p for p in passes)


# ---------------------------------------------------------------------------
# 28. E-16: check_skill_map
# ---------------------------------------------------------------------------

class TestCheckSkillMap:
    def test_valid_skill_map_passes(self, skill_map_data):
        check_skill_map(skill_map_data, results)

        fails = _fails()
        assert len(fails) == 0

    def test_missing_grammar_section_fails(self):
        data = {"schema_version": 1, "vocabulary": {"tier1": {}}}
        check_skill_map(data, results)

        fails = _fails()
        assert any("grammar" in f and "missing" in f for f in fails)

    def test_missing_vocabulary_section_fails(self):
        data = {"schema_version": 1, "grammar": {"A-01-present-regular": {"status": "unseen", "practice_count": 0, "prerequisites": []}}}
        check_skill_map(data, results)

        fails = _fails()
        assert any("vocabulary" in f and "missing" in f for f in fails)

    def test_grammar_entry_missing_required_field_fails(self):
        data = {
            "schema_version": 1,
            "grammar": {
                "A-01-present-regular": {
                    "status": "unseen",
                    # missing practice_count and prerequisites
                },
            },
            "vocabulary": {"tier1": {}},
        }
        check_skill_map(data, results)

        fails = _fails()
        assert any("A-01-present-regular" in f and "missing" in f for f in fails)


# ---------------------------------------------------------------------------
# 29. ENFORCE-06: last_session_date drift detection + auto-fix
# ---------------------------------------------------------------------------

check_last_session_date = validate_mod.check_last_session_date



class TestLastSessionDateDrift:
    def test_detects_drift(self, tmp_path, monkeypatch):
        """ENFORCE-06: stale last_session_date is auto-fixed and logged to system-health."""
        monkeypatch.setattr(validate_mod, "STATE", tmp_path)

        # Create sessions directory with a session log
        sdir = tmp_path / "sessions"
        sdir.mkdir()
        (sdir / "2026-04-12.yaml").write_text("date: 2026-04-12\n", encoding="utf-8")

        # Create schedule.yaml with stale date
        sched_data = {"last_session_date": "2026-04-10", "current_phase": "A-foundation"}
        sched_path = tmp_path / "schedule.yaml"
        with sched_path.open("w") as f:
            yaml.dump(sched_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Create system-health.yaml
        health_data = {"schema_version": 1, "auto_fixes": []}
        health_path = tmp_path / "system-health.yaml"
        with health_path.open("w") as f:
            yaml.dump(health_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        check_last_session_date(sched_data, results, dry_run=False)

        # schedule dict should be updated in-memory
        assert sched_data["last_session_date"] == "2026-04-12"

        # schedule.yaml file should be updated on disk
        updated_sched = yaml.safe_load(sched_path.read_text(encoding="utf-8"))
        assert updated_sched["last_session_date"] == "2026-04-12"

        # system-health.yaml should have an auto_fixes entry
        updated_health = yaml.safe_load(health_path.read_text(encoding="utf-8"))
        fixes = updated_health.get("auto_fixes", [])
        assert len(fixes) == 1
        assert fixes[0]["field"] == "schedule.last_session_date"
        assert fixes[0]["old_value"] == "2026-04-10"
        assert fixes[0]["new_value"] == "2026-04-12"

        # Should be a PASS (auto-fixed)
        passes = _passes()
        assert any("Auto-fixed" in p for p in passes)


class TestLastSessionDateDriftDryRun:
    def test_dry_run_does_not_mutate(self, tmp_path, monkeypatch):
        """ENFORCE-06: --dry-run flag prevents writes, emits WARN."""
        monkeypatch.setattr(validate_mod, "STATE", tmp_path)

        # Create sessions directory with a session log
        sdir = tmp_path / "sessions"
        sdir.mkdir()
        (sdir / "2026-04-12.yaml").write_text("date: 2026-04-12\n", encoding="utf-8")

        # Create schedule.yaml with stale date
        sched_data = {"last_session_date": "2026-04-10", "current_phase": "A-foundation"}
        sched_path = tmp_path / "schedule.yaml"
        with sched_path.open("w") as f:
            yaml.dump(sched_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Create system-health.yaml
        health_data = {"schema_version": 1, "auto_fixes": []}
        health_path = tmp_path / "system-health.yaml"
        with health_path.open("w") as f:
            yaml.dump(health_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        check_last_session_date(sched_data, results, dry_run=True)

        # schedule dict should NOT be updated
        assert sched_data["last_session_date"] == "2026-04-10"

        # schedule.yaml file should NOT be updated on disk
        unchanged_sched = yaml.safe_load(sched_path.read_text(encoding="utf-8"))
        assert unchanged_sched["last_session_date"] == "2026-04-10"

        # system-health.yaml should NOT have any auto_fixes entries
        unchanged_health = yaml.safe_load(health_path.read_text(encoding="utf-8"))
        fixes = unchanged_health.get("auto_fixes", [])
        assert len(fixes) == 0

        # Should be a WARN (dry-run detected drift)
        warns = _warns()
        assert any("dry-run" in w for w in warns)


# ---------------------------------------------------------------------------
# ENGINE Phase 4 tests
# ---------------------------------------------------------------------------

class TestLearnerInterestRange:
    """ENGINE-02 / D-02: learner_interest.score must be 0-3."""

    def test_score_in_range_passes(self, skill_map_data):
        """Score of 2 should pass validation."""
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["learner_interest"] = {
            "score": 2, "last_inferred": "2026-04-15", "signal_source": "debrief"
        }
        res = validate_mod.ValidationResults()
        check_learner_interest_range(sm, res)
        assert not any(level == "FAIL" for level, _ in res._items), \
            "ENGINE-02: score=2 should not FAIL"

    def test_score_above_3_fails(self, skill_map_data):
        """Score of 5 must FAIL."""
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["learner_interest"] = {
            "score": 5, "last_inferred": "2026-04-15", "signal_source": "debrief"
        }
        res = validate_mod.ValidationResults()
        check_learner_interest_range(sm, res)
        assert any(level == "FAIL" for level, _ in res._items), \
            "ENGINE-02: score=5 must FAIL (exceeds 0-3 cap)"

    def test_score_negative_fails(self, skill_map_data):
        """Negative score must FAIL."""
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["learner_interest"] = {
            "score": -1, "last_inferred": "2026-04-15", "signal_source": "debrief"
        }
        res = validate_mod.ValidationResults()
        check_learner_interest_range(sm, res)
        assert any(level == "FAIL" for level, _ in res._items), \
            "ENGINE-02: score=-1 must FAIL"

    def test_missing_field_does_not_fail(self, skill_map_data):
        """Missing learner_interest field is backward-compatible (D-10)."""
        sm = skill_map_data
        # No learner_interest field at all
        res = validate_mod.ValidationResults()
        check_learner_interest_range(sm, res)
        assert not any(level == "FAIL" for level, _ in res._items), \
            "D-10: missing learner_interest must NOT fail"

    def test_vocabulary_concept_checked(self, skill_map_data):
        """learner_interest range check applies to vocabulary too (D-03)."""
        sm = skill_map_data
        # Add learner_interest to a vocabulary entry with out-of-range score
        first_vocab = next(iter(sm.get("vocabulary", {})))
        sm["vocabulary"][first_vocab]["learner_interest"] = {
            "score": 4, "last_inferred": "2026-04-15", "signal_source": "engagement"
        }
        res = validate_mod.ValidationResults()
        check_learner_interest_range(sm, res)
        assert any(level == "FAIL" for level, _ in res._items), \
            "ENGINE-02/D-03: vocabulary score=4 must FAIL"


class TestRecastUptakeStatsConsistency:
    """D-07: landed + missed + partial must be <= recasts_given."""

    def test_consistent_stats_pass(self, skill_map_data):
        """3 + 2 + 1 = 6 <= 8 should pass."""
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["recast_uptake_stats"] = {
            "recasts_given": 8, "landed": 3, "missed": 2, "partial": 1,
            "last_updated": "2026-04-15"
        }
        res = validate_mod.ValidationResults()
        check_recast_uptake_stats_consistency(sm, res)
        assert not any(level == "FAIL" for level, _ in res._items), \
            "D-07: 3+2+1 <= 8 should pass"

    def test_inconsistent_stats_fail(self, skill_map_data):
        """5 + 3 + 2 = 10 > 8 must FAIL."""
        sm = skill_map_data
        sm["grammar"]["A-01-present-regular"]["recast_uptake_stats"] = {
            "recasts_given": 8, "landed": 5, "missed": 3, "partial": 2,
            "last_updated": "2026-04-15"
        }
        res = validate_mod.ValidationResults()
        check_recast_uptake_stats_consistency(sm, res)
        assert any(level == "FAIL" for level, _ in res._items), \
            "D-07: 5+3+2=10 > 8 must FAIL"

    def test_missing_stats_does_not_fail(self, skill_map_data):
        """Missing recast_uptake_stats is backward-compatible (D-10)."""
        sm = skill_map_data
        res = validate_mod.ValidationResults()
        check_recast_uptake_stats_consistency(sm, res)
        assert not any(level == "FAIL" for level, _ in res._items), \
            "D-10: missing recast_uptake_stats must NOT fail"


class TestLearnerInterestStaleness:
    """D-03: staleness > 28 days should WARN (not FAIL)."""

    def test_stale_interest_warns(self, skill_map_data):
        """Interest last inferred 35 days ago should WARN."""
        from datetime import date, timedelta
        sm = skill_map_data
        stale_date = (date.today() - timedelta(days=35)).isoformat()
        sm["grammar"]["A-01-present-regular"]["learner_interest"] = {
            "score": 2, "last_inferred": stale_date, "signal_source": "debrief"
        }
        res = validate_mod.ValidationResults()
        check_learner_interest_staleness(sm, res)
        assert any(level == "WARN" for level, _ in res._items), \
            "D-03: stale interest (>28 days) should WARN"

    def test_fresh_interest_no_warn(self, skill_map_data):
        """Interest inferred 5 days ago should not WARN."""
        from datetime import date, timedelta
        sm = skill_map_data
        fresh_date = (date.today() - timedelta(days=5)).isoformat()
        sm["grammar"]["A-01-present-regular"]["learner_interest"] = {
            "score": 2, "last_inferred": fresh_date, "signal_source": "debrief"
        }
        res = validate_mod.ValidationResults()
        check_learner_interest_staleness(sm, res)
        assert not any(level == "WARN" for level, _ in res._items), \
            "D-03: fresh interest should not WARN"


# =============================================================================
# Phase 5 LOAD: Wave 0 RED-scaffolding tests
# =============================================================================


class TestStudyTimeBudgetConsistency:
    """LOAD-03 / D-04 / D-06: validate-state.py check_study_time_budget_consistency.

    Invariants:
    - null pre-session-1 → PASS
    - null with sessions → FAIL (D-06)
    - min > target → FAIL
    - today_stretch < 0 → FAIL
    - all populated + invariant holds → PASS
    - missing subfield after sessions → FAIL
    """

    def test_null_pre_session_1_passes(self):
        sched = {"study_time_budget": None}
        check_study_time_budget_consistency(sched, has_sessions=False, res=results)
        assert _fails() == []
        assert any("pre-first-session" in m for m in _passes())

    def test_null_after_sessions_fails(self):
        sched = {"study_time_budget": None}
        check_study_time_budget_consistency(sched, has_sessions=True, res=results)
        fails = _fails()
        assert any("null but sessions exist" in m or "required after first-session" in m for m in fails), (
            f"D-06: expected FAIL with 'required after first-session'; got {fails!r}"
        )

    def test_invariant_violation_min_gt_target(self):
        sched = {"study_time_budget": {
            "daily_minimum": 45, "daily_target": 30, "daily_maximum": 60,
            "weekly_goal": 180, "today_stretch": 0,
        }}
        check_study_time_budget_consistency(sched, has_sessions=True, res=results)
        fails = _fails()
        assert any("invariant" in m.lower() for m in fails), (
            f"D-04: expected invariant FAIL; got {fails!r}"
        )

    def test_invariant_violation_target_gt_max(self):
        sched = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 90, "daily_maximum": 60,
            "weekly_goal": 180, "today_stretch": 0,
        }}
        check_study_time_budget_consistency(sched, has_sessions=True, res=results)
        assert any("invariant" in m.lower() for m in _fails())

    def test_negative_today_stretch_fails(self):
        sched = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 30, "daily_maximum": 60,
            "weekly_goal": 180, "today_stretch": -5,
        }}
        check_study_time_budget_consistency(sched, has_sessions=True, res=results)
        assert any("today_stretch" in m and "negative" in m.lower() for m in _fails())

    def test_all_populated_passes(self):
        sched = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 30, "daily_maximum": 60,
            "weekly_goal": 180, "today_stretch": 0,
        }}
        check_study_time_budget_consistency(sched, has_sessions=True, res=results)
        assert _fails() == [], f"Expected no FAILs; got {_fails()!r}"
        assert any("consistency OK" in m for m in _passes())

    def test_missing_subfield_after_session_fails(self):
        sched = {"study_time_budget": {
            "daily_minimum": 15, "daily_target": 30,  # missing daily_maximum, weekly_goal
            "today_stretch": 0,
        }}
        check_study_time_budget_consistency(sched, has_sessions=True, res=results)
        fails = _fails()
        assert any("daily_maximum" in m and "null" in m.lower() for m in fails), (
            f"D-06: expected missing-subfield FAIL naming daily_maximum; got {fails!r}"
        )


class TestDailyTargetTierDrift:
    """LOAD-04 / D-11: drift detector catches the case where the learner rated
    "too-much" twice consecutively but schedule.study_time_budget.daily_target
    was never reduced (tutor forgot the tier adjustment)."""

    def test_drift_detected_when_counter_ignored(self):
        sched = {
            "study_time_budget": {"daily_target": 30, "daily_maximum": 60, "daily_minimum": 15, "weekly_goal": 180, "today_stretch": 0},
            "consecutive_too_much_count": 2,
        }
        session_logs = [
            {"date": "2026-04-22", "homework_load_rating": "too-much"},
            {"date": "2026-04-23", "homework_load_rating": "too-much"},
        ]
        check_daily_target_tier_drift(sched, session_logs, results)
        fails = _fails()
        assert any("daily_target" in m and ("drift" in m.lower() or "reduce" in m.lower() or "consecutive_too_much" in m) for m in fails), (
            f"D-11: expected drift FAIL (2 too-much + daily_target unchanged); got {fails!r}"
        )

    def test_reduced_correctly_passes(self):
        # daily_target was 30, reduced 20% → 24, rounded to nearest 5 → 25
        sched = {
            "study_time_budget": {"daily_target": 25, "daily_maximum": 60, "daily_minimum": 15, "weekly_goal": 180, "today_stretch": 0},
            "consecutive_too_much_count": 0,  # reset after reduction per D-11
        }
        session_logs = [
            {"date": "2026-04-22", "homework_load_rating": "too-much"},
            {"date": "2026-04-23", "homework_load_rating": "too-much"},
        ]
        check_daily_target_tier_drift(sched, session_logs, results)
        # should NOT fail — reduction already applied, counter reset
        assert not any("drift" in m.lower() for m in _fails())

    def test_single_too_much_no_reduction_passes(self):
        sched = {
            "study_time_budget": {"daily_target": 30, "daily_maximum": 60, "daily_minimum": 15, "weekly_goal": 180, "today_stretch": 0},
            "consecutive_too_much_count": 1,
        }
        session_logs = [
            {"date": "2026-04-23", "homework_load_rating": "too-much"},
        ]
        check_daily_target_tier_drift(sched, session_logs, results)
        # 1 too-much does not trigger reduction per D-11
        assert not any("drift" in m.lower() for m in _fails())


class TestJustRightRestoreDrift:
    """A4 / D-11 (restore side): companion to TestDailyTargetTierDrift. The
    too-much ladder has check_daily_target_tier_drift guarding it; the
    +10%-restore-after-3-just-right ladder had no validator, so if the tutor
    never reset consecutive_just_right_count after restoring (or never restored
    despite the counter reaching 3), nothing noticed. This locks the parity.
    """

    def test_restore_drift_detected_when_counter_ignored(self):
        # 3 consecutive 'just-right' AND counter pinned at 3 => the +10% restore
        # (and the counter reset) is pending but unapplied => FAIL.
        sched = {
            "study_time_budget": {"daily_target": 25, "daily_maximum": 60, "daily_minimum": 15, "weekly_goal": 180, "today_stretch": 0},
            "consecutive_just_right_count": 3,
        }
        session_logs = [
            {"date": "2026-04-22", "homework_load_rating": "just-right"},
            {"date": "2026-04-23", "homework_load_rating": "just-right"},
            {"date": "2026-04-24", "homework_load_rating": "just-right"},
        ]
        check_just_right_restore_drift(sched, session_logs, results)
        fails = _fails()
        assert any(
            "daily_target" in m
            and ("restore" in m.lower() or "just_right" in m.lower() or "just-right" in m.lower())
            for m in fails
        ), f"A4/D-11: expected restore-drift FAIL (3 just-right + counter=3); got {fails!r}"

    def test_restored_correctly_passes(self):
        # daily_target restored +10% (25 -> 27.5 -> nearest 5 = 30) and counter reset.
        sched = {
            "study_time_budget": {"daily_target": 30, "daily_maximum": 60, "daily_minimum": 15, "weekly_goal": 180, "today_stretch": 0},
            "consecutive_just_right_count": 0,  # reset after restore per D-11
        }
        session_logs = [
            {"date": "2026-04-22", "homework_load_rating": "just-right"},
            {"date": "2026-04-23", "homework_load_rating": "just-right"},
            {"date": "2026-04-24", "homework_load_rating": "just-right"},
        ]
        check_just_right_restore_drift(sched, session_logs, results)
        assert not any("restore" in m.lower() for m in _fails())

    def test_two_just_right_below_threshold_passes(self):
        # Only 2 consecutive just-right — below the 3-rating restore threshold.
        sched = {
            "study_time_budget": {"daily_target": 25, "daily_maximum": 60, "daily_minimum": 15, "weekly_goal": 180, "today_stretch": 0},
            "consecutive_just_right_count": 2,
        }
        session_logs = [
            {"date": "2026-04-23", "homework_load_rating": "just-right"},
            {"date": "2026-04-24", "homework_load_rating": "just-right"},
        ]
        check_just_right_restore_drift(sched, session_logs, results)
        assert not any("restore" in m.lower() for m in _fails())

    def test_no_study_time_budget_passes(self):
        check_just_right_restore_drift({"consecutive_just_right_count": 3}, [], results)
        assert not any("restore" in m.lower() for m in _fails())


class TestAcquiredConsistencyCoreOnly:
    """LOAD-01 / D-02: check_acquired_consistency must scope to grammar only.
    Cultural/pronunciation/writing concepts with status: acquired must NOT trigger a FAIL
    from this check (they have no error_rate_drills field by design).

    This test RUNS NOW — it locks the currently-correct behavior (L237-256 iterates grammar only)
    so a future refactor can't silently broaden scope."""

    def test_cultural_acquired_does_not_fail(self):
        # Cultural concept has no error_rate_drills. Injecting it at status=acquired
        # must not produce a FAIL from check_acquired_consistency.
        sm = {
            "grammar": {},
            "cultural_awareness": {
                "politeness-formulas": {
                    "status": "acquired",
                    # NO error_rate_drills field by design
                }
            },
        }
        check_acquired_consistency(sm, results)
        fails = _fails()
        assert not any("politeness-formulas" in m or "cultural" in m for m in fails), (
            f"LOAD-01/D-02: cultural acquired entry must NOT trigger FAIL from check_acquired_consistency; got {fails!r}"
        )

    def test_pronunciation_acquired_does_not_fail(self):
        sm = {
            "grammar": {},
            "pronunciation": {
                "rr-trill": {"status": "acquired"},
            },
        }
        check_acquired_consistency(sm, results)
        assert not any("rr-trill" in m or "pronunciation" in m for m in _fails())

    def test_writing_acquired_does_not_fail(self):
        sm = {
            "grammar": {},
            "writing": {
                "paragraph-cohesion": {"status": "acquired"},
            },
        }
        check_acquired_consistency(sm, results)
        assert not any("paragraph-cohesion" in m or "writing" in m for m in _fails())

    def test_grammar_acquired_with_high_error_still_fails(self):
        """Regression: ensure the check still flags core concepts with bad data."""
        sm = {"grammar": {"A-01-present-regular": {
            "status": "acquired",
            "error_rate_drills": 0.35,
            "error_rate_production": 0.05,
            "performance_unscaffolded": "competent",
        }}}
        check_acquired_consistency(sm, results)
        fails = _fails()
        assert any("A-01" in m and ("error_rate_drills" in m or "0.35" in m) for m in fails), (
            f"LOAD-01: grammar regression — acquired+high-error must still FAIL; got {fails!r}"
        )


class TestSessionLogEnumsHomeworkLoad:
    """LOAD-04: The existing schema-driven enum loop in check_session_logs
    automatically validates every enum field in session-log.schema.yaml. Once
    homework_load_rating is added (plan 05-04), invalid values must FAIL via this loop."""

    def test_valid_values_accepted(self):
        """Placeholder — exercises the enum loop via minimal session-log fixture with valid value."""
        import yaml
        from pathlib import Path
        schema_path = Path(__file__).resolve().parent.parent / "schemas" / "session-log.schema.yaml"
        schema_doc = yaml.safe_load(schema_path.read_text()) or {}
        # Schedule/session-log schemas wrap field specs under `fields:` — tolerate either layout.
        fields = schema_doc.get("fields") or schema_doc
        assert "homework_load_rating" in fields, (
            "LOAD-04: homework_load_rating must be present in session-log.schema.yaml"
        )
        spec = fields["homework_load_rating"] or {}
        enum = spec.get("enum") or []
        assert "too-much" in enum, "LOAD-04: 'too-much' must be in homework_load_rating enum"
        assert "just-right" in enum, "LOAD-04: 'just-right' must be in homework_load_rating enum"
        assert "too-light" in enum, "LOAD-04: 'too-light' must be in homework_load_rating enum"
        assert None in enum, "LOAD-04: null must be in homework_load_rating enum"
