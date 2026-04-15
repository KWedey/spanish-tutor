"""Tests for decision-engine.md content integrity.

Validates that the decision engine documentation contains required sections,
scoring dimensions, worked examples, and cross-references.
"""

import re
from pathlib import Path

import pytest

DECISION_ENGINE_PATH = Path(__file__).parent.parent / "curriculum" / "tutor-guides" / "decision-engine.md"


@pytest.fixture
def doc_content():
    """Load decision-engine.md content."""
    return DECISION_ENGINE_PATH.read_text()


class TestInterestDimension:
    """Verify INTEREST dimension exists in Step 2 with correct structure."""

    def test_interest_heading_exists(self, doc_content):
        """INTEREST subsection exists with 0-3 range."""
        assert "### INTEREST (0-3)" in doc_content

    def test_interest_between_topic_and_variety(self, doc_content):
        """INTEREST appears between TOPIC_BOOST and VARIETY_PENALTY."""
        topic_pos = doc_content.index("### TOPIC_BOOST")
        interest_pos = doc_content.index("### INTEREST (0-3)")
        variety_pos = doc_content.index("### VARIETY_PENALTY")
        assert topic_pos < interest_pos < variety_pos

    def test_interest_in_priority_formula(self, doc_content):
        """PRIORITY formula includes INTEREST term."""
        assert "PRIORITY = NEED + GAP + DECAY_ADJUSTED + TOPIC_BOOST + INTEREST - VARIETY_PENALTY" in doc_content

    def test_interest_scoring_rubric(self, doc_content):
        """INTEREST has a 4-level scoring rubric (0-3)."""
        # Check all four score levels exist in the rubric
        assert "| 3 |" in doc_content
        assert "| 2 |" in doc_content
        assert "| 1 |" in doc_content
        assert "| 0 |" in doc_content

    def test_interest_signal_sources(self, doc_content):
        """Signal sources are documented."""
        assert "parking-lot.md" in doc_content
        assert "learner_observations" in doc_content
        assert "real-world-debrief.md" in doc_content
        assert "journal entries" in doc_content

    def test_interest_stale_decay(self, doc_content):
        """Stale decay rule documented (28 days)."""
        assert "28 days" in doc_content
        assert "stale decay" in doc_content.lower()

    def test_interest_storage_documented(self, doc_content):
        """Storage format documented with skill-map reference."""
        assert "learner_interest" in doc_content
        assert "skill-map.yaml" in doc_content
        assert "last_inferred" in doc_content
        assert "signal_source" in doc_content

    def test_interest_step3_reference(self, doc_content):
        """Step 3 modifiers section references stale interest decay."""
        step3_match = doc_content[doc_content.index("## Step 3"):]
        step4_pos = step3_match.index("## Step 4")
        step3_section = step3_match[:step4_pos]
        assert "Stale interest decay" in step3_section


class TestInterestCap:
    """Verify INTEREST cap mechanics are documented."""

    def test_cap_value_documented(self, doc_content):
        """Maximum contribution is 3."""
        assert "Maximum contribution is 3" in doc_content

    def test_cap_validator_reference(self, doc_content):
        """validate-state.py enforcement referenced."""
        assert "validate-state.py" in doc_content
        assert "score > 3 = FAIL" in doc_content

    def test_regression_beats_interest_math(self, doc_content):
        """Cap explanation shows regression baseline beats max interest."""
        assert "NEED 10 + GAP 10 = 20 baseline" in doc_content
        assert "NEED 7 + GAP 3 + INTEREST 3 = 13" in doc_content


class TestWorkedExamplesUpdated:
    """Verify worked examples include INTEREST dimension."""

    def test_example1_has_interest_row(self, doc_content):
        """Example 1 includes INTEREST row."""
        ex1_start = doc_content.index("### Example 1")
        ex2_start = doc_content.index("### Example 2")
        ex1 = doc_content[ex1_start:ex2_start]
        assert "INTEREST" in ex1
        assert "No explicit signal" in ex1

    def test_example1_priority_unchanged(self, doc_content):
        """Example 1 PRIORITY is 20.4 (INTEREST=0 doesn't change total)."""
        ex1_start = doc_content.index("### Example 1")
        ex2_start = doc_content.index("### Example 2")
        ex1 = doc_content[ex1_start:ex2_start]
        assert "**20.4**" in ex1

    def test_example2_has_interest_row(self, doc_content):
        """Example 2 includes INTEREST row."""
        ex2_start = doc_content.index("### Example 2")
        ex3_start = doc_content.index("### Example 3")
        ex2 = doc_content[ex2_start:ex3_start]
        assert "INTEREST" in ex2
        assert "No signal" in ex2

    def test_example2_priority_unchanged(self, doc_content):
        """Example 2 PRIORITY is 3.1 (INTEREST=0 doesn't change total)."""
        ex2_start = doc_content.index("### Example 2")
        ex3_start = doc_content.index("### Example 3")
        ex2 = doc_content[ex2_start:ex3_start]
        assert "**3.1**" in ex2

    def test_example3_c04_interest_2(self, doc_content):
        """Example 3 C-04 has INTEREST=2 (parking-lot question)."""
        ex3_start = doc_content.index("### Example 3")
        ex4_start = doc_content.index("### Example 4")
        ex3 = doc_content[ex3_start:ex4_start]
        assert "Parking-lot question" in ex3
        assert "2" in ex3  # INTEREST score

    def test_example3_c04_priority_17(self, doc_content):
        """Example 3 C-04 PRIORITY is 17.0."""
        ex3_start = doc_content.index("### Example 3")
        ex4_start = doc_content.index("### Example 4")
        ex3 = doc_content[ex3_start:ex4_start]
        assert "**17.0**" in ex3

    def test_example3_c01_priority_15(self, doc_content):
        """Example 3 C-01 PRIORITY is 15.0."""
        ex3_start = doc_content.index("### Example 3")
        ex4_start = doc_content.index("### Example 4")
        ex3 = doc_content[ex3_start:ex4_start]
        assert "**15.0**" in ex3

    def test_example3_c04_wins(self, doc_content):
        """Example 3 prose says C-04 wins (no longer a tie)."""
        ex3_start = doc_content.index("### Example 3")
        ex4_start = doc_content.index("### Example 4")
        ex3 = doc_content[ex3_start:ex4_start]
        assert "C-04 wins" in ex3

    def test_example4_exists(self, doc_content):
        """Example 4 exists (regression beats interest)."""
        assert "### Example 4" in doc_content
        assert "ENGINE-02 demonstration" in doc_content

    def test_example4_regression_wins(self, doc_content):
        """Example 4: A-02 (regressed) PRIORITY = 20.6 beats C-05 = 19.0."""
        ex4_start = doc_content.index("### Example 4")
        ex4_end = doc_content.index("## Naturally-Acquired Concepts")
        ex4 = doc_content[ex4_start:ex4_end]
        assert "**20.6**" in ex4
        assert "**19.0**" in ex4
        assert "A-02 wins" in ex4

    def test_example4_interest_values(self, doc_content):
        """Example 4: A-02 INTEREST=0, C-05 INTEREST=3."""
        ex4_start = doc_content.index("### Example 4")
        ex4_end = doc_content.index("## Naturally-Acquired Concepts")
        ex4 = doc_content[ex4_start:ex4_end]
        assert "No signal" in ex4
        assert "Asked unprompted" in ex4


class TestRegressionLadder:
    """Verify Step 0c regression escalation ladder exists with correct structure."""

    def test_step0c_exists(self, doc_content):
        """Step 0c section exists."""
        assert re.search(r"## Step 0c", doc_content)

    def test_step0c_before_step1(self, doc_content):
        """Step 0c appears before Step 1."""
        step0c_pos = doc_content.index("Step 0c")
        step1_pos = doc_content.index("## Step 1")
        assert step0c_pos < step1_pos

    def test_step0c_after_step0b(self, doc_content):
        """Step 0c appears after Step 0b."""
        step0b_pos = doc_content.index("## Step 0b")
        step0c_pos = doc_content.index("## Step 0c")
        assert step0b_pos < step0c_pos

    def test_prerequisite_regression_table(self, doc_content):
        """Prerequisite regression table exists with 5 stages."""
        assert "### Prerequisite Regression" in doc_content

    def test_non_prerequisite_regression_table(self, doc_content):
        """Non-prerequisite regression table exists."""
        assert "### Non-Prerequisite Regression" in doc_content

    def test_all_stage_names_present(self, doc_content):
        """All 5 named stages exist: normal, flagged, approach_changed, sprint, surfaced."""
        step0c_start = doc_content.index("## Step 0c")
        step1_start = doc_content.index("## Step 1")
        step0c = doc_content[step0c_start:step1_start]
        assert "normal" in step0c
        assert "flagged" in step0c
        assert "approach_changed" in step0c
        assert "sprint" in step0c
        assert "surfaced" in step0c

    def test_recast_uptake_stats_referenced(self, doc_content):
        """recast_uptake_stats referenced in Step 0c."""
        step0c_start = doc_content.index("## Step 0c")
        step1_start = doc_content.index("## Step 1")
        step0c = doc_content[step0c_start:step1_start]
        assert "recast_uptake_stats" in step0c

    def test_error_correction_crosslink(self, doc_content):
        """Cross-link to error-correction.md Escalation Protocol."""
        step0c_start = doc_content.index("## Step 0c")
        step1_start = doc_content.index("## Step 1")
        step0c = doc_content[step0c_start:step1_start]
        assert re.search(r"error-correction\.md.*Escalation Protocol", step0c)

    def test_data_insufficiency_threshold(self, doc_content):
        """Data-insufficiency threshold documented (recasts_given >= 5)."""
        step0c_start = doc_content.index("## Step 0c")
        step1_start = doc_content.index("## Step 1")
        step0c = doc_content[step0c_start:step1_start]
        assert "recasts_given" in step0c

    def test_uptake_rate_threshold(self, doc_content):
        """Uptake rate threshold documented (landed/given < 0.60)."""
        step0c_start = doc_content.index("## Step 0c")
        step1_start = doc_content.index("## Step 1")
        step0c = doc_content[step0c_start:step1_start]
        assert "landed/given" in step0c
        assert "0.60" in step0c

    def test_approach_change_modes(self, doc_content):
        """Approach change reads recast_uptake_stats for mode selection."""
        step0c_start = doc_content.index("## Step 0c")
        step1_start = doc_content.index("## Step 1")
        step0c = doc_content[step0c_start:step1_start]
        # Low uptake -> escalate mode
        assert "recast" in step0c.lower()
        assert "explicit" in step0c.lower()
        assert "metalinguistic" in step0c.lower()

    def test_data_insufficiency_fallback(self, doc_content):
        """Data-insufficiency fallback to context/modality change."""
        step0c_start = doc_content.index("## Step 0c")
        step1_start = doc_content.index("## Step 1")
        step0c = doc_content[step0c_start:step1_start]
        assert "recasts_given < 5" in step0c
