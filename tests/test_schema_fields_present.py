"""Regression tests: ENGINE schema fields must be present in all canonical locations.

If any field is deleted from schemas, docs, or validators, these tests FAIL.
Follows Phase 2.1 HOOK regression-test-locks-wiring precedent.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT  # alias for Phase 5 LOAD tests

SCHEMA_SESSION = ROOT / "schemas" / "session-log.schema.yaml"
SCHEMA_SKILL = ROOT / "schemas" / "skill-map.schema.yaml"
SCHEMA_SCHEDULE = ROOT / "schemas" / "schedule.schema.yaml"
SYSTEM_DESIGN = ROOT / "docs" / "system-design.md"
VALIDATE_STATE = ROOT / "scripts" / "validate-state.py"
CHECK_SESSION = ROOT / "scripts" / "check-session-log.py"
DECISION_ENGINE = ROOT / "curriculum" / "tutor-guides" / "decision-engine.md"
CLAUDE_MD = ROOT / "CLAUDE.md"


class TestRecastsFieldPresent:
    """recasts field must exist in session-log schema and docs."""

    def test_session_log_schema(self):
        text = SCHEMA_SESSION.read_text()
        assert "recasts:" in text, \
            "ENGINE-03: recasts must be in session-log.schema.yaml"

    def test_system_design_docs(self):
        text = SYSTEM_DESIGN.read_text()
        assert "recasts" in text, \
            "ENGINE-07: recasts must be documented in docs/system-design.md"

    def test_check_session_log(self):
        text = CHECK_SESSION.read_text()
        assert "recasts" in text, \
            "ENGINE-03: recasts enforcement must be in check-session-log.py"


class TestLearnerInterestFieldPresent:
    """learner_interest field must exist in skill-map schema and docs."""

    def test_skill_map_schema(self):
        text = SCHEMA_SKILL.read_text()
        assert "learner_interest:" in text, \
            "ENGINE-01: learner_interest must be in skill-map.schema.yaml"

    def test_system_design_docs(self):
        text = SYSTEM_DESIGN.read_text()
        assert "learner_interest" in text, \
            "ENGINE-07: learner_interest must be documented in docs/system-design.md"

    def test_validate_state(self):
        text = VALIDATE_STATE.read_text()
        assert "learner_interest" in text, \
            "ENGINE-02: learner_interest range check must be in validate-state.py"

    def test_decision_engine(self):
        text = DECISION_ENGINE.read_text()
        assert "learner_interest" in text or "INTEREST" in text, \
            "ENGINE-01: INTEREST dimension must be in decision-engine.md"


class TestRecastUptakeStatsFieldPresent:
    """recast_uptake_stats field must exist in skill-map schema and docs."""

    def test_skill_map_schema(self):
        text = SCHEMA_SKILL.read_text()
        assert "recast_uptake_stats:" in text, \
            "ENGINE-03: recast_uptake_stats must be in skill-map.schema.yaml"

    def test_system_design_docs(self):
        text = SYSTEM_DESIGN.read_text()
        assert "recast_uptake_stats" in text, \
            "ENGINE-07: recast_uptake_stats must be documented in docs/system-design.md"

    def test_validate_state(self):
        text = VALIDATE_STATE.read_text()
        assert "recast_uptake_stats" in text, \
            "D-07: recast_uptake_stats consistency check must be in validate-state.py"


class TestInterestTraceDimensionPresent:
    """INTEREST dimension must exist in session-log schema trace."""

    def test_session_log_schema(self):
        text = SCHEMA_SESSION.read_text()
        assert "INTEREST" in text, \
            "ENGINE-08/D-04: INTEREST must be in session-log.schema.yaml top_candidates"

    def test_system_design_docs(self):
        text = SYSTEM_DESIGN.read_text()
        assert "INTEREST" in text, \
            "ENGINE-07/D-04: INTEREST must be documented in docs/system-design.md"


class TestRegressionSessionCountFieldPresent:
    """regression_session_count field must exist in skill-map schema and docs (ENGINE-05/D-09)."""

    def test_skill_map_schema(self):
        text = SCHEMA_SKILL.read_text()
        assert "regression_session_count:" in text, \
            "ENGINE-05: regression_session_count must be in skill-map.schema.yaml"

    def test_system_design_docs(self):
        text = SYSTEM_DESIGN.read_text()
        assert "regression_session_count" in text, \
            "ENGINE-05: regression_session_count must be documented in docs/system-design.md"

    def test_decision_engine(self):
        text = DECISION_ENGINE.read_text()
        assert "regression_session_count" in text, \
            "ENGINE-05: regression_session_count must be referenced in decision-engine.md Step 0c"


class TestFieldNameConsistency:
    """Pitfall 3: field names must appear in >= 5 files."""

    def test_recast_uptake_stats_cross_file_count(self):
        count = 0
        for f in [SCHEMA_SKILL, SYSTEM_DESIGN, VALIDATE_STATE, DECISION_ENGINE,
                  ROOT / "scripts" / "post-session.sh"]:
            if f.exists() and "recast_uptake_stats" in f.read_text():
                count += 1
        assert count >= 5, \
            f"Pitfall 3: recast_uptake_stats found in {count} files, need >= 5"


# =============================================================================
# Phase 5 LOAD: Wave 0 RED-scaffolding tests
# =============================================================================


class TestStudyTimeBudgetFieldPresent:
    """LOAD-03/05/07: study_time_budget must be in schedule schema, docs, both scripts, and CLAUDE.md."""

    def test_schedule_schema(self):
        text = SCHEMA_SCHEDULE.read_text(encoding="utf-8")
        assert "study_time_budget:" in text, \
            "LOAD-07: study_time_budget: must be in schemas/schedule.schema.yaml"

    def test_system_design_docs(self):
        text = SYSTEM_DESIGN.read_text(encoding="utf-8")
        assert "study_time_budget" in text, \
            "LOAD-07: study_time_budget must be documented in docs/system-design.md"

    def test_check_session_log(self):
        text = CHECK_SESSION.read_text(encoding="utf-8")
        assert "study_time_budget" in text, \
            "LOAD-03: budget enforcement in check-session-log.py must reference study_time_budget"

    def test_validate_state(self):
        text = VALIDATE_STATE.read_text(encoding="utf-8")
        assert "study_time_budget" in text, \
            "LOAD-03: study_time_budget consistency check must exist in validate-state.py"

    def test_claude_md(self):
        text = CLAUDE_MD.read_text(encoding="utf-8")
        assert "study_time_budget" in text, \
            "LOAD-05: CLAUDE.md L179 guardrail must cite study_time_budget"


class TestStudyTimeBudgetTopLevel:
    """LOAD-07: study_time_budget must be a TOP-LEVEL key in schedule.schema.yaml, not nested.

    Note: the schedule schema wraps all field specs under a `fields:` key. This test
    walks into that wrapper — "top-level" here means peer to `current_phase`,
    `sprint`, etc., NOT nested under `placement_validation` or any other map.
    """

    def test_top_level_not_nested(self):
        import yaml
        schema_doc = yaml.safe_load(SCHEMA_SCHEDULE.read_text(encoding="utf-8")) or {}
        fields = schema_doc.get("fields") or schema_doc  # tolerate either layout
        assert "study_time_budget" in fields, (
            "LOAD-07: study_time_budget must be a top-level key in schedule.schema.yaml "
            "(peer to current_phase / sprint — NOT nested under placement_validation or any other map)"
        )
        spec = fields["study_time_budget"]
        assert isinstance(spec, dict), "study_time_budget must be a schema spec (dict), not a scalar"
        assert spec.get("type") == "map", \
            f"LOAD-07/D-04: study_time_budget must be a map (got type={spec.get('type')!r})"
        children = spec.get("children") or {}
        for sub in ("daily_minimum", "daily_target", "daily_maximum", "weekly_goal", "today_stretch"):
            assert sub in children, f"LOAD-07/D-04: study_time_budget must have child '{sub}'"


class TestHomeworkLoadRatingFieldPresent:
    """LOAD-04: homework_load_rating must be in session-log schema, docs, and check-session-log.py."""

    def test_session_log_schema(self):
        text = SCHEMA_SESSION.read_text(encoding="utf-8")
        assert "homework_load_rating:" in text, \
            "LOAD-04: homework_load_rating must be in schemas/session-log.schema.yaml"

    def test_enum_values(self):
        text = SCHEMA_SESSION.read_text(encoding="utf-8")
        # The enum line is the shape-equivalent of session_difficulty_rating at L221-226
        for value in ('"too-much"', '"just-right"', '"too-light"'):
            assert value in text, \
                f"LOAD-04/D-10: homework_load_rating enum must include {value}"

    def test_system_design_docs(self):
        text = SYSTEM_DESIGN.read_text(encoding="utf-8")
        assert "homework_load_rating" in text, \
            "LOAD-04: homework_load_rating must be documented in docs/system-design.md"

    def test_check_session_log_expects_it(self):
        text = CHECK_SESSION.read_text(encoding="utf-8")
        assert "homework_load_rating" in text, \
            "LOAD-04: check-session-log.py must enforce homework_load_rating in EXPECTED_BY_TYPE"


class TestEstimatedMinutesFieldName:
    """Pitfall 1: the authoritative field on assignments[] is estimated_minutes, NOT estimated_duration.
    Lock via tests so no Phase 5 code (or future change) reintroduces the wrong name next to assignments."""

    def test_check_session_log_uses_estimated_minutes(self):
        text = CHECK_SESSION.read_text(encoding="utf-8")
        # Budget sum path must reference estimated_minutes (Pitfall 1)
        assert "estimated_minutes" in text, \
            "LOAD-03/Pitfall-1: check-session-log.py budget sum must reference assignments[].estimated_minutes"

    def test_claude_md_uses_estimated_minutes(self):
        text = CLAUDE_MD.read_text(encoding="utf-8")
        assert "estimated_minutes" in text, \
            "LOAD-05/Pitfall-1/D-08: CLAUDE.md L179 homework guardrail must name estimated_minutes (NOT estimated_duration)"

    def test_no_estimated_duration_on_assignments_in_check(self):
        """Negative assertion: estimated_duration must not appear on the same line as 'assignments' or 'assignment_' in check-session-log.py (that would be the Pitfall-1 regression)."""
        text = CHECK_SESSION.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "estimated_duration" in line and ("assignments" in line or "assignment_" in line):
                assert False, (
                    f"Pitfall-1 regression at line {line_no}: 'estimated_duration' appears next to 'assignments' in check-session-log.py. "
                    f"Use estimated_minutes. Line content: {line!r}"
                )


class TestConsecutiveCountersPresent:
    """D-11: explicit consecutive_too_much_count + consecutive_just_right_count fields in schedule.schema.yaml.
    Skipped if planner deferred to derived-from-logs (05-02 plan owns this decision — recommended explicit per CONTEXT.md §Claude's Discretion)."""

    def test_counters_in_schema(self):
        text = SCHEMA_SCHEDULE.read_text(encoding="utf-8")
        assert "consecutive_too_much_count" in text, \
            "D-11: schedule.schema.yaml must have consecutive_too_much_count (planner chose explicit field)"
        assert "consecutive_just_right_count" in text, \
            "D-11: schedule.schema.yaml must have consecutive_just_right_count"
