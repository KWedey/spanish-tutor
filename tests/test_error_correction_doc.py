"""Doc-prose regression tests for error-correction.md and CLAUDE.md error correction sections.

Verifies:
- Stage x Phase Correction Matrix exists with correct structure (ENGINE-06)
- Metalinguistic Feedback Protocol section exists with required subsections (ENGINE-04)
- CLAUDE.md footnote references error-correction.md as source of truth (ENGINE-06)
- No contradiction between CLAUDE.md quick-reference table and the matrix

Requirements covered: ENGINE-04, ENGINE-06.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ERROR_CORRECTION_MD = REPO_ROOT / "curriculum" / "activities" / "error-correction.md"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"


class TestStagePhaseMatrix:
    """Verify the Stage x Phase Correction Matrix in error-correction.md."""

    def setup_method(self):
        self.content = ERROR_CORRECTION_MD.read_text(encoding="utf-8")

    def test_matrix_heading_exists(self):
        """ENGINE-06: error-correction.md must have a Stage x Phase matrix heading."""
        assert re.search(
            r"^##\s+.*Stage.*Phase.*Matrix", self.content, re.MULTILINE | re.IGNORECASE
        ), "Missing '## Stage x Phase Correction Matrix' heading in error-correction.md"

    def test_matrix_has_phase_columns(self):
        """ENGINE-06: Matrix must have Phase A, B, C, D columns."""
        for phase in ["Phase A", "Phase B", "Phase C", "Phase D"]:
            assert phase in self.content, (
                f"Matrix missing column header '{phase}' in error-correction.md"
            )

    def test_matrix_has_stage_rows(self):
        """ENGINE-06: Matrix must have Stage 1-2, Stage 3, Stage 4, Fluency rows."""
        for stage in ["Stage 1-2", "Stage 3", "Stage 4", "Fluency"]:
            assert stage in self.content, (
                f"Matrix missing row label '{stage}' in error-correction.md"
            )

    def test_matrix_is_a_table(self):
        """ENGINE-06: The matrix must be a markdown table (pipes and dashes)."""
        # Find the matrix section and verify it contains a markdown table
        matrix_match = re.search(
            r"##\s+.*Stage.*Phase.*Matrix\s*\n([\s\S]*?)(?=\n##\s|\Z)",
            self.content,
            re.IGNORECASE,
        )
        assert matrix_match, "Could not find the Stage x Phase Matrix section"
        section = matrix_match.group(1)
        # Must have table separator row (e.g., |-------|---------|)
        assert re.search(r"\|-+\|", section), (
            "Matrix section does not contain a markdown table"
        )

    def test_source_of_truth_declaration(self):
        """ENGINE-06: Matrix section must declare itself as source of truth."""
        assert re.search(r"source of truth", self.content, re.IGNORECASE), (
            "error-correction.md must declare the matrix as 'source of truth'"
        )

    def test_old_dichotomy_removed(self):
        """ENGINE-06: The old 'Recasting vs explicit correction' prose must be replaced."""
        # The old prose started with "**Recasting:** Tutor restates"
        assert "**Recasting:** Tutor restates" not in self.content, (
            "Old 'Recasting vs explicit correction' dichotomy prose still present — "
            "should have been replaced by Stage x Phase Matrix"
        )

    def test_recast_salience_preserved(self):
        """ENGINE-06: Recast salience techniques section must be preserved."""
        assert "Recast salience techniques" in self.content, (
            "Recast salience techniques section was accidentally removed"
        )

    def test_escalation_crosslink(self):
        """ENGINE-06: Escalation Protocol must cross-link to decision-engine.md Step 0c."""
        assert "decision-engine.md" in self.content, (
            "Escalation Protocol must reference decision-engine.md"
        )
        assert "Step 0c" in self.content, (
            "Escalation Protocol must reference Step 0c (Regression Escalation Ladder)"
        )


class TestMetalinguisticProtocol:
    """Verify the Metalinguistic Feedback Protocol section in error-correction.md."""

    def setup_method(self):
        self.content = ERROR_CORRECTION_MD.read_text(encoding="utf-8")

    def test_heading_exists(self):
        """ENGINE-04: error-correction.md must have a Metalinguistic Feedback Protocol heading."""
        assert re.search(
            r"^##\s+Metalinguistic Feedback Protocol",
            self.content,
            re.MULTILINE,
        ), "Missing '## Metalinguistic Feedback Protocol' heading"

    def test_when_to_use_subsection(self):
        """ENGINE-04: Must have 'When to use' subsection."""
        assert "**When to use:**" in self.content, (
            "Metalinguistic Feedback Protocol missing 'When to use' subsection"
        )

    def test_how_to_phrase_subsection(self):
        """ENGINE-04: Must have 'How to phrase' subsection."""
        assert "**How to phrase:**" in self.content, (
            "Metalinguistic Feedback Protocol missing 'How to phrase' subsection"
        )

    def test_what_not_to_do_subsection(self):
        """ENGINE-04: Must have 'What NOT to do' subsection."""
        assert "**What NOT to do:**" in self.content, (
            "Metalinguistic Feedback Protocol missing 'What NOT to do' subsection"
        )

    def test_one_concept_per_session_limit(self):
        """ENGINE-04: Must limit metalinguistic corrections to 1 concept per session."""
        assert re.search(
            r"(1|one)\s+concept\s+per\s+session", self.content, re.IGNORECASE
        ), "Metalinguistic protocol must specify '1 concept per session' limit"

    def test_prohibits_stage4_phase_ab(self):
        """ENGINE-04: Must prohibit metalinguistic mode during Stage 4 in Phase A-B."""
        # Check that Stage 4 + Phase A-B prohibition exists
        assert re.search(
            r"Stage 4.*Phase A-B|free conversation.*Phase A-B",
            self.content,
            re.IGNORECASE,
        ), "Must prohibit metalinguistic mode during Stage 4 / free conversation in Phase A-B"

    def test_protocol_after_matrix(self):
        """ENGINE-04: Metalinguistic Protocol must appear after Stage x Phase Matrix."""
        matrix_pos = self.content.find("Stage x Phase Correction Matrix")
        protocol_pos = self.content.find("Metalinguistic Feedback Protocol")
        assert matrix_pos > 0, "Stage x Phase Correction Matrix not found"
        assert protocol_pos > 0, "Metalinguistic Feedback Protocol not found"
        assert protocol_pos > matrix_pos, (
            "Metalinguistic Feedback Protocol must appear AFTER Stage x Phase Matrix"
        )


class TestClaudeMdConsistency:
    """Verify CLAUDE.md error correction footnote and consistency."""

    def setup_method(self):
        self.claude_content = CLAUDE_MD.read_text(encoding="utf-8")
        self.ec_content = ERROR_CORRECTION_MD.read_text(encoding="utf-8")

    def test_source_of_truth_footnote(self):
        """ENGINE-06: CLAUDE.md must have 'source of truth' near Error Correction."""
        assert re.search(r"source of truth", self.claude_content, re.IGNORECASE), (
            "CLAUDE.md must contain 'source of truth' referencing error-correction.md"
        )

    def test_error_correction_md_reference(self):
        """ENGINE-06: CLAUDE.md must reference error-correction.md."""
        assert "error-correction.md" in self.claude_content, (
            "CLAUDE.md must reference 'error-correction.md' in the footnote"
        )

    def test_metalinguistic_mention(self):
        """ENGINE-04: CLAUDE.md must mention metalinguistic feedback."""
        assert re.search(r"metalinguistic", self.claude_content, re.IGNORECASE), (
            "CLAUDE.md must mention 'metalinguistic' feedback"
        )

    def test_mode_and_frequency_terms(self):
        """ENGINE-06: CLAUDE.md footnote must use MODE and FREQUENCY terms."""
        assert "MODE" in self.claude_content, (
            "CLAUDE.md footnote must contain 'MODE'"
        )
        assert re.search(r"FREQUENCY|frequency", self.claude_content), (
            "CLAUDE.md footnote must contain 'FREQUENCY' or 'frequency'"
        )

    def test_table_rows_preserved(self):
        """ENGINE-06: CLAUDE.md Error Correction table rows must be preserved."""
        for stage in [
            "Stage 1-2 (controlled practice)",
            "Stage 3 (guided production)",
            "Stage 4 (free conversation)",
            "Fluency activities",
        ]:
            assert stage in self.claude_content, (
                f"CLAUDE.md Error Correction table row '{stage}' was removed or modified"
            )
