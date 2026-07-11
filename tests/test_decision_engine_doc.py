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


# ---------------------------------------------------------------------------
# Parse helpers — verify the worked examples' rules/arithmetic instead of
# freezing the exact rendered literals, so legitimate reweighting or a benign
# reflow keeps the tests green while a real math error or winner-flip turns
# them red. (Mirrors the parse-and-verify style of test_regression_beats_
# interest_math below.)
# ---------------------------------------------------------------------------

def _example(doc_content, start, end):
    """Slice the doc to a single worked example."""
    return doc_content[doc_content.index(start):doc_content.index(end)]


def _sum_expression(expr):
    """Sum a '+'/'-' operand list like '10 + 8 + 1.4 + 1 + 0 - 0'.

    Tokens are parsed (not eval()'d), so only the add/subtract operand lists the
    doc actually uses are ever evaluated.
    """
    total = 0.0
    for sign, num in re.findall(r"([+-]?)\s*(\d+(?:\.\d+)?)", expr):
        value = float(num)
        total += -value if sign == "-" else value
    return total


def _single_col_priority(section):
    """Return (computed_sum, stated_total) for a single-column PRIORITY row:
    `| **PRIORITY** | 10 + 8 + 1.4 + 1 + 0 - 0 | **20.4** |`."""
    m = re.search(r"\*\*PRIORITY\*\*\s*\|\s*([^|]+?)\s*\|\s*\*\*([0-9.]+)\*\*", section)
    assert m, "single-column PRIORITY row not found"
    return _sum_expression(m.group(1)), float(m.group(2))


def _two_col_priorities(section):
    """Return {column_label: priority_float} for a two-column worked example.

    Reads the header row (two concept columns) and the bolded PRIORITY row, so
    the test tracks which concept scores higher rather than a frozen number.
    """
    header = None
    for line in section.splitlines():
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 3 and cells[0] == "" and header is None:
                header = (cells[1], cells[2])
                break
    assert header, "two-column header row not found"
    m = re.search(
        r"\*\*PRIORITY\*\*\s*\|\s*\*\*([0-9.]+)\*\*\s*\|\s*\*\*([0-9.]+)\*\*", section
    )
    assert m, "two-column PRIORITY row not found"
    return {header[0]: float(m.group(1)), header[1]: float(m.group(2))}


def _priority_for(priorities, concept_id):
    """Look up a column's PRIORITY by the concept id in its header label."""
    for label, value in priorities.items():
        if concept_id in label:
            return value
    raise AssertionError(f"{concept_id} column not found in {list(priorities)}")


def _interest_row_values(section):
    """Return the trailing INTEREST score of each column from the INTEREST row:
    `| INTEREST | No signal → 0 | Asked unprompted → 3 |` → [0, 3]."""
    for line in section.splitlines():
        if line.strip().startswith("| INTEREST |"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            return [int(re.search(r"(\d+)\s*$", c).group(1)) for c in cells[1:]]
    raise AssertionError("INTEREST row not found")


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
        """INTEREST's maximum contribution is documented as 3.

        Whitespace/format-tolerant: asserts the rule (cap == 3), not the exact
        prose, so reflowing the sentence can't silently break the test.
        """
        assert re.search(r"maximum contribution is\s+3\b", doc_content, re.I), (
            "INTEREST cap of 3 not documented (expected 'Maximum contribution is 3')"
        )

    def test_cap_validator_reference(self, doc_content):
        """validate-state.py enforcement referenced with the >3 FAIL rule."""
        assert "validate-state.py" in doc_content
        assert re.search(r"score\s*>\s*3\s*=\s*FAIL", doc_content), (
            "INTEREST >3 validator FAIL rule not documented (expected 'score > 3 = FAIL')"
        )

    def test_regression_beats_interest_math(self, doc_content):
        """Cap explanation shows a regression baseline beats max interest.

        Asserts the RULE — by parsing the operands and checking the stated sums
        are internally consistent AND that the regression baseline outscores the
        interest-inflated total — rather than transcribing the exact arithmetic
        prose. Reformatting the example keeps the test green; a genuine math
        error in the doc (or a cap that no longer wins) turns it red.
        """
        m_base = re.search(
            r"NEED\s+(\d+)\s*\+\s*GAP\s+(\d+)\s*=\s*(\d+)\s*baseline", doc_content
        )
        assert m_base, "regression-baseline arithmetic line missing from cap explanation"
        need_b, gap_b, base_total = (int(g) for g in m_base.groups())
        assert need_b + gap_b == base_total, (
            f"baseline arithmetic is internally inconsistent in the doc: "
            f"{need_b} + {gap_b} != {base_total}"
        )

        m_int = re.search(
            r"NEED\s+(\d+)\s*\+\s*GAP\s+(\d+)\s*\+\s*INTEREST\s+(\d+)\s*=\s*(\d+)",
            doc_content,
        )
        assert m_int, "interest-inflated arithmetic line missing from cap explanation"
        need_i, gap_i, interest_i, int_total = (int(g) for g in m_int.groups())
        assert need_i + gap_i + interest_i == int_total, (
            f"interest-inflated arithmetic is internally inconsistent in the doc: "
            f"{need_i} + {gap_i} + {interest_i} != {int_total}"
        )
        # The example's INTEREST operand must respect the documented cap of 3.
        assert interest_i <= 3, (
            f"cap-explanation example uses INTEREST={interest_i}, exceeding the "
            f"documented maximum contribution of 3"
        )

        assert base_total > int_total, (
            f"cap explanation must show the regression baseline ({base_total}) "
            f"beating the max-interest total ({int_total}) — that is the rule the "
            f"INTEREST cap exists to guarantee"
        )


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
        """Example 1 PRIORITY equals its own operand sum (INTEREST=0 term
        included). Verifies the doc's arithmetic rather than freezing 20.4."""
        ex1 = _example(doc_content, "### Example 1", "### Example 2")
        computed, stated = _single_col_priority(ex1)
        assert computed == pytest.approx(stated), (
            f"Example 1 PRIORITY row is internally inconsistent: "
            f"operands sum to {computed}, stated total is {stated}"
        )

    def test_example2_has_interest_row(self, doc_content):
        """Example 2 includes INTEREST row."""
        ex2_start = doc_content.index("### Example 2")
        ex3_start = doc_content.index("### Example 3")
        ex2 = doc_content[ex2_start:ex3_start]
        assert "INTEREST" in ex2
        assert "No signal" in ex2

    def test_example2_priority_unchanged(self, doc_content):
        """Example 2 PRIORITY equals its own operand sum (INTEREST=0 term
        included). Verifies the doc's arithmetic rather than freezing 3.1."""
        ex2 = _example(doc_content, "### Example 2", "### Example 3")
        computed, stated = _single_col_priority(ex2)
        assert computed == pytest.approx(stated), (
            f"Example 2 PRIORITY row is internally inconsistent: "
            f"operands sum to {computed}, stated total is {stated}"
        )

    def test_example3_c04_interest_2(self, doc_content):
        """Example 3 C-04 has INTEREST=2 (parking-lot question)."""
        ex3_start = doc_content.index("### Example 3")
        ex4_start = doc_content.index("### Example 4")
        ex3 = doc_content[ex3_start:ex4_start]
        assert "Parking-lot question" in ex3
        assert "2" in ex3  # INTEREST score

    def test_example3_c04_priority_17(self, doc_content):
        """Example 3 C-04 is the higher-scoring column (structural: winner has
        the max PRIORITY), rather than freezing the literal 17.0."""
        ex3 = _example(doc_content, "### Example 3", "### Example 4")
        priorities = _two_col_priorities(ex3)
        assert _priority_for(priorities, "C-04") == max(priorities.values())

    def test_example3_c01_priority_15(self, doc_content):
        """Example 3 C-01 is the lower-scoring column, rather than freezing the
        literal 15.0."""
        ex3 = _example(doc_content, "### Example 3", "### Example 4")
        priorities = _two_col_priorities(ex3)
        assert _priority_for(priorities, "C-01") == min(priorities.values())

    def test_example3_c04_wins(self, doc_content):
        """C-04 wins on score: its column carries a strictly higher PRIORITY
        than C-01. Checks the rule instead of the exact prose 'C-04 wins'."""
        ex3 = _example(doc_content, "### Example 3", "### Example 4")
        priorities = _two_col_priorities(ex3)
        assert _priority_for(priorities, "C-04") > _priority_for(priorities, "C-01")

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
        """Example 4 INTEREST row: A-02 (regressed) = 0, C-05 (high interest)
        = 3 (the documented max). Parses the row's values instead of freezing
        the 'No signal'/'Asked unprompted' prose, and confirms C-05 respects
        the cap of 3."""
        ex4 = _example(doc_content, "### Example 4", "## Naturally-Acquired Concepts")
        a02_interest, c05_interest = _interest_row_values(ex4)
        assert a02_interest == 0
        assert c05_interest == 3


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
