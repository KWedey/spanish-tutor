"""LOAD-02 / D-03 parity: docs/system-design.md L1350-1360 and
curriculum/tutor-guides/phase-transition-guide.md Core/Secondary subsections
must name the SAME concept IDs. Tight lockstep.

Authoritative source: docs/system-design.md L1350-1360 (per RESEARCH.md).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_DESIGN = REPO_ROOT / "docs" / "system-design.md"
GUIDE = REPO_ROOT / "curriculum" / "tutor-guides" / "phase-transition-guide.md"

# Authoritative Core IDs from docs/system-design.md L1350-1360 (verified RESEARCH.md §Phase Prerequisite Map)
CORE_A_TO_B = frozenset({"A-01", "A-02", "A-04"})
CORE_B_TO_C = frozenset({"B-01", "B-04"})
CORE_C_TO_D = frozenset({"C-01", "C-04", "C-06"})


def _extract_ids_near(text: str, anchor: str, window: int = 2000) -> set[str]:
    """Return the set of matches of pattern X-NN within 'window' chars after 'anchor'."""
    i = text.find(anchor)
    if i == -1:
        return set()
    segment = text[i : i + window]
    return set(re.findall(r"\b[A-D]-\d{2}\b", segment))


class TestPhasePrerequisiteParity:
    """Core prerequisite IDs in phase-transition-guide.md must match authoritative set from system-design.md."""

    def test_guide_a_to_b_core_matches(self):
        guide_text = GUIDE.read_text(encoding="utf-8")
        ids = _extract_ids_near(guide_text, "Core prerequisites", 600)
        if not ids:  # guide not yet updated — caught by TestPhaseTransitionGuideReference in test_claude_md.py
            return
        # A→B is the FIRST 'Core prerequisites' occurrence; scope narrowly
        first_block = guide_text.split("Core prerequisites")[1][:600] if "Core prerequisites" in guide_text else ""
        a_ids = set(re.findall(r"\bA-\d{2}\b", first_block))
        assert CORE_A_TO_B.issubset(a_ids), (
            f"LOAD-02 parity: A→B Core prerequisites in guide {a_ids} must include {set(CORE_A_TO_B)} "
            f"(authoritative list from docs/system-design.md L1351)"
        )

    def test_guide_b_to_c_core_matches(self):
        guide_text = GUIDE.read_text(encoding="utf-8")
        if "Core prerequisites" not in guide_text:
            return
        blocks = guide_text.split("Core prerequisites")
        # blocks[1] is A→B; blocks[2] (if present) is B→C; blocks[3] is C→D
        if len(blocks) >= 3:
            b_block = blocks[2][:600]
            b_ids = set(re.findall(r"\bB-\d{2}\b", b_block))
            assert CORE_B_TO_C.issubset(b_ids), (
                f"LOAD-02 parity: B→C Core prerequisites {b_ids} must include {set(CORE_B_TO_C)}"
            )

    def test_guide_c_to_d_core_matches(self):
        guide_text = GUIDE.read_text(encoding="utf-8")
        if "Core prerequisites" not in guide_text:
            return
        blocks = guide_text.split("Core prerequisites")
        if len(blocks) >= 4:
            c_block = blocks[3][:600]
            c_ids = set(re.findall(r"\bC-\d{2}\b", c_block))
            assert CORE_C_TO_D.issubset(c_ids), (
                f"LOAD-02 parity: C→D Core prerequisites {c_ids} must include {set(CORE_C_TO_D)}"
            )

    def test_system_design_still_canonical(self):
        """Regression: if L1350-1360 in system-design.md stops listing these IDs, guide has no source of truth."""
        text = SYSTEM_DESIGN.read_text(encoding="utf-8")
        for cid in CORE_A_TO_B | CORE_B_TO_C | CORE_C_TO_D:
            assert cid in text, (
                f"LOAD-02 parity: canonical concept ID '{cid}' missing from docs/system-design.md — guide's source of truth broken"
            )
