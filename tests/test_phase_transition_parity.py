"""LOAD-02 / D-03 parity: curriculum/tutor-guides/phase-transition-guide.md and
docs/system-design.md (Advancement Rules section) must name the SAME CORE
prerequisite concept IDs as scripts/phase_prereqs.py — the single code-side source
of truth that validate-state.py (check_phase_prereqs_acquired) enforces.

Tight lockstep: EQUALITY (not subset), and the Core ID set is extracted strictly
from the slice BETWEEN the 'Core prerequisites' and 'Secondary prerequisites'
headers. The previous fixed-width window leaked Secondary IDs into the Core set
and used issubset, so a concept demoted Core->Secondary passed undetected (audit
P1-5). Equality + the Core-only slice + an explicit Secondary-overlap check now
catch add, remove, AND Core<->Secondary misclassification.
"""

import re
from pathlib import Path

from phase_prereqs import CORE_A_TO_B, CORE_B_TO_C, CORE_C_TO_D

REPO_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_DESIGN = REPO_ROOT / "docs" / "system-design.md"
GUIDE = REPO_ROOT / "curriculum" / "tutor-guides" / "phase-transition-guide.md"


def _core_slice(guide_text: str, occurrence: int) -> str:
    """Text of the Nth (1-based) 'Core prerequisites' block, scoped to the slice
    BETWEEN that header and the next 'Secondary prerequisites' header so Secondary
    IDs cannot leak into the Core set."""
    parts = guide_text.split("Core prerequisites")
    if len(parts) <= occurrence:
        return ""
    after = parts[occurrence]
    end = after.find("Secondary prerequisites")
    return after[:end] if end != -1 else after


def _ids(text: str, letter: str) -> set:
    return set(re.findall(rf"\b{letter}-\d{{2}}\b", text))


class TestPhasePrerequisiteParity:
    """The guide's Core prereq IDs must EQUAL scripts/phase_prereqs.py per transition."""

    def test_guide_a_to_b_core_matches(self):
        a_ids = _ids(_core_slice(GUIDE.read_text(encoding="utf-8"), 1), "A")
        assert a_ids == set(CORE_A_TO_B), (
            f"LOAD-02 parity: A->B Core in guide {a_ids} != phase_prereqs {set(CORE_A_TO_B)}"
        )

    def test_guide_b_to_c_core_matches(self):
        b_ids = _ids(_core_slice(GUIDE.read_text(encoding="utf-8"), 2), "B")
        assert b_ids == set(CORE_B_TO_C), (
            f"LOAD-02 parity: B->C Core in guide {b_ids} != phase_prereqs {set(CORE_B_TO_C)}"
        )

    def test_guide_c_to_d_core_matches(self):
        c_ids = _ids(_core_slice(GUIDE.read_text(encoding="utf-8"), 3), "C")
        assert c_ids == set(CORE_C_TO_D), (
            f"LOAD-02 parity: C->D Core in guide {c_ids} != phase_prereqs {set(CORE_C_TO_D)}"
        )

    def test_core_ids_not_in_secondary_block(self):
        """A Core prereq ID must NOT also appear under its Secondary block — the exact
        Core->Secondary demotion the old fixed-width issubset window failed to detect."""
        guide = GUIDE.read_text(encoding="utf-8")
        sec_parts = guide.split("Secondary prerequisites")
        for occ, letter, core in ((1, "A", CORE_A_TO_B), (2, "B", CORE_B_TO_C), (3, "C", CORE_C_TO_D)):
            sec_block = sec_parts[occ] if len(sec_parts) > occ else ""
            overlap = set(core) & _ids(sec_block, letter)
            assert not overlap, (
                f"LOAD-02 parity: Core prereq(s) {overlap} also appear under the "
                f"{letter}-transition Secondary block — Core/Secondary misclassification."
            )

    def test_system_design_still_canonical(self):
        """Regression: every Core ID must still appear in docs/system-design.md so the
        guide + phase_prereqs retain a documented source of truth."""
        text = SYSTEM_DESIGN.read_text(encoding="utf-8")
        for cid in CORE_A_TO_B | CORE_B_TO_C | CORE_C_TO_D:
            assert cid in text, (
                f"LOAD-02 parity: canonical concept ID '{cid}' missing from docs/system-design.md"
            )
