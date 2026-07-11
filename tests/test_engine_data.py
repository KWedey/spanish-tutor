"""Engine-data parity tests for the two machine-readable engine banks.

`curriculum/decision-weights.yaml` and `curriculum/error-correction-matrix.yaml`
are the portable, code-executable form of the concept-selection algorithm and the
error-correction matrix (engine-api.md contracts #3/#4/#6 and #5). Each was extracted
from a prose guide that remains the pedagogical source of truth:

    decision-weights.yaml          <- curriculum/tutor-guides/decision-engine.md
    error-correction-matrix.yaml   <- curriculum/activities/error-correction.md

This module is the drift alarm those files' headers promise. It:
  (a) parses both YAML banks and asserts their top-level structure + full
      stage x phase matrix coverage;
  (b) spot-checks load-bearing constants against their prose sources so a number
      cannot silently diverge between the data bank and the guide / CLAUDE.md;
  (c) parses the Step 0b / 0c escalation-ladder markdown tables in decision-engine.md
      and confirms every threshold matches decision-weights.yaml.

Requirements covered: ENGINE-03, ENGINE-05, ENGINE-06.
"""
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DECISION_WEIGHTS = REPO_ROOT / "curriculum" / "decision-weights.yaml"
ERROR_MATRIX = REPO_ROOT / "curriculum" / "error-correction-matrix.yaml"
DECISION_ENGINE_MD = REPO_ROOT / "curriculum" / "tutor-guides" / "decision-engine.md"
ERROR_CORRECTION_MD = REPO_ROOT / "curriculum" / "activities" / "error-correction.md"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

PHASES = ["A", "B", "C", "D"]
STAGES = [1, 2, 3, 4, "fluency"]
CELL_KEYS = {"mode", "timing", "explicit_cap", "explicit_cap_10min", "recast_cap", "notes"}
MODE_ENUM = {"explicit", "recast", "mixed", "meaning_impeding_only"}
TIMING_ENUM = {"immediate", "batched"}


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _section(md, start_marker, end_marker):
    """Return the slice of `md` between the first occurrence of `start_marker`
    and the next occurrence of `end_marker` after it."""
    start = md.index(start_marker)
    end = md.index(end_marker, start + len(start_marker))
    return md[start:end]


def _stage_to_sessions(section):
    """Parse an escalation-ladder markdown table into {normalized_stage: first_int}.

    Each ladder row is `| <sessions> | <stage> | <action> |`; we key by the stage
    cell (normalized to snake_case so 'sprint or deprioritize' == 'sprint_or_deprioritize')
    and value with the leading integer of the sessions cell ('12+' -> 12, '1-5' -> 1).
    Header and separator rows carry no leading integer in the sessions cell and are
    skipped automatically.
    """
    result = {}
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        num = re.match(r"(\d+)", cells[0])
        if not num:
            continue
        stage = cells[1].lower().replace(" ", "_")
        result[stage] = int(num.group(1))
    return result


# ---------------------------------------------------------------------------
# (a) Structure + coverage
# ---------------------------------------------------------------------------

class TestDecisionWeightsStructure:
    """decision-weights.yaml parses and carries every top-level block the
    decision-engine contracts read."""

    def test_parses_to_mapping(self):
        assert isinstance(_load(DECISION_WEIGHTS), dict)

    def test_schema_version(self):
        assert _load(DECISION_WEIGHTS)["schema_version"] == 1

    def test_required_top_level_blocks(self):
        data = _load(DECISION_WEIGHTS)
        for block in (
            "priority_formula", "need", "gap_grammar", "gap_vocabulary", "decay",
            "topic_boost", "interest", "variety_penalty", "modifiers", "selection",
            "concurrent_concept_gate", "acquisition_gate", "carryover_escalation",
            "regression_escalation", "interleaving", "topic_scoring", "fluency_days",
        ):
            assert block in data, f"decision-weights.yaml missing top-level block '{block}'"


class TestErrorMatrixStructure:
    """error-correction-matrix.yaml parses with full stage x phase coverage and a
    uniform cell shape."""

    def test_parses_to_mapping(self):
        assert isinstance(_load(ERROR_MATRIX), dict)

    def test_schema_version(self):
        assert _load(ERROR_MATRIX)["schema_version"] == 1

    def test_required_top_level_blocks(self):
        data = _load(ERROR_MATRIX)
        for block in ("matrix", "metalinguistic_escalation", "escalation_protocol"):
            assert block in data, f"error-correction-matrix.yaml missing block '{block}'"

    def test_full_stage_phase_coverage(self):
        matrix = _load(ERROR_MATRIX)["matrix"]
        assert set(matrix) == set(STAGES), (
            f"matrix stages {sorted(map(str, matrix))} != expected {sorted(map(str, STAGES))}"
        )
        for stage in STAGES:
            assert set(matrix[stage]) == set(PHASES), (
                f"stage {stage} phases {sorted(matrix[stage])} != {PHASES}"
            )

    def test_every_cell_has_uniform_shape(self):
        matrix = _load(ERROR_MATRIX)["matrix"]
        for stage in STAGES:
            for phase in PHASES:
                cell = matrix[stage][phase]
                assert set(cell) == CELL_KEYS, f"cell [{stage}][{phase}] keys {set(cell)} != {CELL_KEYS}"
                assert cell["mode"] in MODE_ENUM, f"cell [{stage}][{phase}] bad mode {cell['mode']!r}"
                assert cell["timing"] in TIMING_ENUM, f"cell [{stage}][{phase}] bad timing {cell['timing']!r}"
                for cap in ("explicit_cap", "explicit_cap_10min", "recast_cap"):
                    assert cell[cap] is None or isinstance(cell[cap], int), (
                        f"cell [{stage}][{phase}].{cap} must be int or null, got {cell[cap]!r}"
                    )

    def test_stage_1_and_2_share_controlled_practice_row(self):
        """Stage 1 and Stage 2 are the same 'controlled practice' row (YAML anchor)."""
        matrix = _load(ERROR_MATRIX)["matrix"]
        assert matrix[1] == matrix[2]


# ---------------------------------------------------------------------------
# (b) Load-bearing constants vs. their prose sources
# ---------------------------------------------------------------------------

class TestDecisionWeightConstantsMatchGuide:
    """Load-bearing decision-weights numbers must also appear in decision-engine.md."""

    def test_phase_prerequisite_need_is_10_in_both(self):
        weights = _load(DECISION_WEIGHTS)
        assert weights["need"]["phase_prerequisite"] == 10
        md = DECISION_ENGINE_MD.read_text(encoding="utf-8")
        assert re.search(r"Phase prerequisite[^\n|]*\|\s*10\s*\|", md), (
            "decision-engine.md NEED table must score 'Phase prerequisite' as 10"
        )

    def test_interest_cap_is_3_in_both(self):
        weights = _load(DECISION_WEIGHTS)
        assert weights["interest"]["cap"] == 3
        md = DECISION_ENGINE_MD.read_text(encoding="utf-8")
        assert re.search(r"maximum contribution is\s+3\b", md, re.I), (
            "decision-engine.md must document INTEREST 'Maximum contribution is 3'"
        )
        assert re.search(r"score\s*>\s*3\s*=\s*FAIL", md), (
            "decision-engine.md must document the INTEREST '>3 = FAIL' validator rule"
        )


class TestAcquisitionGateMatchesClaudeMd:
    """acquisition_gate error-rate thresholds must equal the CLAUDE.md 'acquired' gate."""

    def test_gate_thresholds_are_010(self):
        gate = _load(DECISION_WEIGHTS)["acquisition_gate"]
        assert gate["error_rate_drills_max"] == 0.10
        assert gate["error_rate_production_max"] == 0.10

    def test_claude_md_acquired_gate_uses_010(self):
        claude = CLAUDE_MD.read_text(encoding="utf-8")
        assert re.search(r"error_rate_drills`?\s*<\s*0\.10", claude), (
            "CLAUDE.md acquired gate must require error_rate_drills < 0.10"
        )
        assert re.search(r"error_rate_production`?\s*<\s*0\.10", claude), (
            "CLAUDE.md acquired gate must require error_rate_production < 0.10"
        )


class TestStage4CapsMatchProse:
    """Matrix Stage-4 explicit caps (3, and 5 for a 10-min segment) must agree with
    both error-correction.md and the CLAUDE.md Error Correction quick-reference table."""

    def test_matrix_stage4_caps(self):
        matrix = _load(ERROR_MATRIX)["matrix"]
        # Phases A/B/C are the scaling free-conversation cells.
        for phase in ("A", "B", "C"):
            cell = matrix[4][phase]
            assert cell["explicit_cap"] == 3, f"Stage 4 / Phase {phase} explicit_cap must be 3"
            assert cell["explicit_cap_10min"] == 5, (
                f"Stage 4 / Phase {phase} explicit_cap_10min must be 5"
            )

    def test_error_correction_md_stage4_caps(self):
        ec = ERROR_CORRECTION_MD.read_text(encoding="utf-8")
        assert re.search(r"3 explicit per segment", ec), (
            "error-correction.md Stage 4 row must state 'max 3 explicit per segment'"
        )
        assert re.search(r"5 for a 10-min segment", ec), (
            "error-correction.md Stage 4 row must state 'up to 5 for a 10-min segment'"
        )

    def test_claude_md_stage4_caps(self):
        claude = CLAUDE_MD.read_text(encoding="utf-8")
        assert re.search(r"[Mm]ax 3 explicit corrections per segment", claude), (
            "CLAUDE.md Error Correction table must state 'Max 3 explicit corrections per segment'"
        )
        assert re.search(r"scale to 5 for 10-min", claude), (
            "CLAUDE.md Error Correction table must state 'scale to 5 for 10-min segments'"
        )


class TestMetalinguisticAndEscalationConstants:
    """The metalinguistic trigger and Escalation Protocol thresholds in the matrix YAML
    must match the prose in error-correction.md."""

    def test_metalinguistic_trigger_is_2(self):
        meta = _load(ERROR_MATRIX)["metalinguistic_escalation"]
        assert meta["trigger_failed_explicit_corrections"] == 2
        assert meta["max_concepts_per_session"] == 1
        ec = ERROR_CORRECTION_MD.read_text(encoding="utf-8")
        assert re.search(r"explicit correction 2\+ times", ec), (
            "error-correction.md must state the metalinguistic trigger '2+' explicit corrections"
        )

    def test_escalation_protocol_thresholds_3_5_8(self):
        ladder = _load(ERROR_MATRIX)["escalation_protocol"]
        assert [e["at_sessions"] for e in ladder] == [3, 5, 8]
        ec = ERROR_CORRECTION_MD.read_text(encoding="utf-8")
        for n in (3, 5, 8):
            assert re.search(rf"{n}\+ sessions", ec), (
                f"error-correction.md Escalation Protocol must list a '{n}+ sessions' threshold"
            )


# ---------------------------------------------------------------------------
# (c) Escalation ladders vs. Step 0b / 0c markdown tables
# ---------------------------------------------------------------------------

class TestEscalationLaddersMatchTables:
    """Every carryover/regression escalation threshold in decision-weights.yaml must
    equal the leading session number of its named-stage row in the decision-engine.md
    Step 0b / 0c markdown tables."""

    def _md(self):
        return DECISION_ENGINE_MD.read_text(encoding="utf-8")

    def _assert_ladder(self, ladder, section):
        table = _stage_to_sessions(section)
        for entry in ladder:
            stage = entry["stage"]
            assert stage in table, (
                f"stage '{stage}' from decision-weights.yaml not found in the doc table "
                f"(parsed stages: {sorted(table)})"
            )
            assert table[stage] == entry["at_sessions"], (
                f"stage '{stage}': decision-weights says {entry['at_sessions']} sessions, "
                f"doc table says {table[stage]}"
            )

    def test_carryover_prerequisite(self):
        md = self._md()
        section = _section(md, "### Prerequisite Carryover", "### Non-Prerequisite Carryover")
        self._assert_ladder(_load(DECISION_WEIGHTS)["carryover_escalation"]["prerequisite"], section)

    def test_carryover_non_prerequisite(self):
        md = self._md()
        section = _section(md, "### Non-Prerequisite Carryover", "## Step 0c")
        self._assert_ladder(
            _load(DECISION_WEIGHTS)["carryover_escalation"]["non_prerequisite"], section
        )

    def test_regression_prerequisite(self):
        md = self._md()
        section = _section(md, "### Prerequisite Regression", "### Non-Prerequisite Regression")
        self._assert_ladder(_load(DECISION_WEIGHTS)["regression_escalation"]["prerequisite"], section)

    def test_regression_non_prerequisite(self):
        md = self._md()
        section = _section(md, "### Non-Prerequisite Regression", "## Step 1")
        self._assert_ladder(
            _load(DECISION_WEIGHTS)["regression_escalation"]["non_prerequisite"], section
        )
