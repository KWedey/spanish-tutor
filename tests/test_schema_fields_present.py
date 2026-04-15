"""Regression tests: ENGINE schema fields must be present in all canonical locations.

If any field is deleted from schemas, docs, or validators, these tests FAIL.
Follows Phase 2.1 HOOK regression-test-locks-wiring precedent.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCHEMA_SESSION = ROOT / "schemas" / "session-log.schema.yaml"
SCHEMA_SKILL = ROOT / "schemas" / "skill-map.schema.yaml"
SYSTEM_DESIGN = ROOT / "docs" / "system-design.md"
VALIDATE_STATE = ROOT / "scripts" / "validate-state.py"
CHECK_SESSION = ROOT / "scripts" / "check-session-log.py"
DECISION_ENGINE = ROOT / "curriculum" / "tutor-guides" / "decision-engine.md"


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
