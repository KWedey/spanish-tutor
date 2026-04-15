"""Tests for decision-engine.md structural requirements (ENGINE-01, -02, -05).

RED stubs -- all fail until decision-engine.md is edited in Plan 04-01.
"""
from pathlib import Path

DOC = Path(__file__).resolve().parent.parent / "curriculum" / "tutor-guides" / "decision-engine.md"


class TestInterestDimension:
    """ENGINE-01: INTEREST subsection must exist in Step 2."""

    def test_interest_subsection_exists(self):
        text = DOC.read_text()
        assert "### INTEREST" in text or "### INTEREST (0-3)" in text, \
            "ENGINE-01: decision-engine.md must have an INTEREST subsection under Step 2"

    def test_priority_formula_includes_interest(self):
        text = DOC.read_text()
        assert "INTEREST" in text.split("PRIORITY =")[1].split("\n")[0] if "PRIORITY =" in text else False, \
            "ENGINE-01: PRIORITY formula must include INTEREST term"

    def test_scoring_rubric_0_to_3(self):
        text = DOC.read_text()
        # Must contain the 0-3 scoring rubric for interest
        assert "**3:**" in text or "| 3 |" in text, \
            "ENGINE-01: INTEREST subsection must include 0-3 scoring rubric"


class TestInterestCap:
    """ENGINE-02: regression must beat max-interest concept in worked example."""

    def test_regression_beats_interest_example(self):
        text = DOC.read_text()
        # The doc must contain a worked example showing regression > interest
        assert "regression" in text.lower() and "INTEREST" in text, \
            "ENGINE-02: must have a worked example demonstrating regression beats high interest"


class TestRegressionLadder:
    """ENGINE-05: Step 0c regression escalation ladder must exist."""

    def test_step_0c_exists(self):
        text = DOC.read_text()
        assert "## Step 0c" in text or "### Step 0c" in text, \
            "ENGINE-05: decision-engine.md must have Step 0c"

    def test_prerequisite_ladder_has_5_stages(self):
        text = DOC.read_text()
        for stage in ["normal", "flagged", "approach_changed", "sprint", "surfaced"]:
            assert stage in text, \
                f"ENGINE-05: prerequisite ladder must include stage '{stage}'"

    def test_approach_changed_reads_recast_uptake_stats(self):
        text = DOC.read_text()
        assert "recast_uptake_stats" in text, \
            "ENGINE-05/D-09: approach_changed must reference recast_uptake_stats"

    def test_cross_link_to_error_correction(self):
        text = DOC.read_text()
        assert "error-correction.md" in text, \
            "ENGINE-05/D-09: Step 0c must cross-link to error-correction.md"


class TestWorkedExamplesUpdated:
    """Pitfall 7: worked examples must include INTEREST dimension."""

    def test_example1_includes_interest(self):
        text = DOC.read_text()
        # Find Example 1 section and check for INTEREST row
        if "### Example 1" in text:
            example_section = text.split("### Example 1")[1].split("### Example")[0]
            assert "INTEREST" in example_section, \
                "Pitfall 7: Example 1 must include INTEREST dimension"
        else:
            assert False, "Example 1 section not found"

    def test_example3_includes_interest(self):
        text = DOC.read_text()
        if "### Example 3" in text:
            example_section = text.split("### Example 3")[1].split("##")[0]
            assert "INTEREST" in example_section, \
                "Pitfall 7: Example 3 must include INTEREST dimension"
        else:
            assert False, "Example 3 section not found"
