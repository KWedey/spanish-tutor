"""Tests for error-correction.md and CLAUDE.md consistency (ENGINE-04, -06).

RED stubs -- all fail until error-correction.md and CLAUDE.md are edited in Plan 04-02.
"""
from pathlib import Path

EC_DOC = Path(__file__).resolve().parent.parent / "curriculum" / "activities" / "error-correction.md"
CLAUDE_DOC = Path(__file__).resolve().parent.parent / "CLAUDE.md"


class TestStagePhaseMatrix:
    """ENGINE-06: Stage x Phase matrix must exist and be source of truth."""

    def test_matrix_section_exists(self):
        text = EC_DOC.read_text()
        assert "## Stage" in text and "Phase" in text and "Matrix" in text, \
            "ENGINE-06: error-correction.md must have a Stage x Phase Matrix section"

    def test_matrix_has_four_phases(self):
        text = EC_DOC.read_text()
        for phase in ["Phase A", "Phase B", "Phase C", "Phase D"]:
            assert phase in text, \
                f"ENGINE-06: matrix must include {phase}"

    def test_matrix_has_four_stages(self):
        text = EC_DOC.read_text()
        for stage in ["Stage 1-2", "Stage 3", "Stage 4", "Fluency"]:
            assert stage in text, \
                f"ENGINE-06: matrix must include {stage}"


class TestMetalinguisticProtocol:
    """ENGINE-04: explicit metalinguistic feedback protocol."""

    def test_protocol_section_exists(self):
        text = EC_DOC.read_text()
        assert "## Metalinguistic Feedback Protocol" in text, \
            "ENGINE-04: error-correction.md must have Metalinguistic Feedback Protocol section"

    def test_when_to_use(self):
        text = EC_DOC.read_text()
        assert "When to use" in text or "**When to use:**" in text, \
            "ENGINE-04: protocol must define when to use metalinguistic feedback"

    def test_what_not_to_do(self):
        text = EC_DOC.read_text()
        assert "What NOT to do" in text or "**What NOT to do:**" in text, \
            "ENGINE-04: protocol must define what NOT to do"

    def test_one_concept_per_session_limit(self):
        text = EC_DOC.read_text()
        assert "1 concept per session" in text or "one concept per session" in text.lower(), \
            "ENGINE-04/D-08: protocol must limit metalinguistic to 1 concept per session"


class TestClaudeMdConsistency:
    """ENGINE-06: CLAUDE.md table must cite error-correction.md as source of truth."""

    def test_footnote_exists(self):
        text = CLAUDE_DOC.read_text()
        assert "source of truth" in text.lower() and "error-correction.md" in text, \
            "ENGINE-06: CLAUDE.md must have footnote citing error-correction.md as source of truth"

    def test_metalinguistic_mentioned(self):
        text = CLAUDE_DOC.read_text()
        assert "metalinguistic" in text.lower(), \
            "ENGINE-06/D-08: CLAUDE.md must mention metalinguistic mode"

    def test_stage_mode_phase_frequency_annotation(self):
        text = CLAUDE_DOC.read_text()
        # D-08 requires this exact framing
        assert "MODE" in text and ("FREQUENCY" in text or "frequency" in text), \
            "ENGINE-06/D-08: CLAUDE.md must annotate Stage=MODE, Phase=FREQUENCY"
