"""ROUTE-FOLLOWUP-03: CLAUDE.md is loaded at every session start. Semantic markers
lock the load-bearing structure (Step 3 routing rows + Guardrails section) so a
future edit that weakens routing precedence or removes a guardrail fails CI.

08-00 lands an existence-only stub. 08-07 fills in the row-token + guardrail-heading
assertions. The file lives in the test directory at this path so 08-07 can extend it.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"


class TestClaudeMdSemanticMarkers:
    def test_claude_md_exists(self):
        """RED-on-arrival via 08-07 expanding this class. Today this passes (CLAUDE.md
        exists); 08-07 turns it into a full marker check."""
        assert CLAUDE_MD.exists(), (
            "ROUTE-FOLLOWUP-03: CLAUDE.md missing — 08-07 cannot anchor markers."
        )

    def test_step3_routing_markers_present(self):
        """RED stub. 08-07 fills this in: asserts the Step 3 routing row tokens
        ('First Session', 'Onboarding', 'Return', 'Maintenance', 'Weekly Review',
        'Sprint Session', 'Fluency', 'Standard Session') appear in CLAUDE.md in the
        documented row order. Today this fails by design (assertion not yet wired)."""
        pytest.fail(
            "ROUTE-FOLLOWUP-03: filled in by 08-07. See "
            ".planning/phases/08-followup-v1.1-improvements/08-07-PLAN.md."
        )
