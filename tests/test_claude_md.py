"""Doc-prose regression test for CLAUDE.md Step 0 reframe (Phase 3 ENFORCE-10).

This test locks the CLAUDE.md State Updates section to reference post-session.sh
and its Step 0 (snapshot) guarantee. If either phrase is removed, the test fails,
preventing silent regression of the enforcement mechanism documentation.

Requirements covered: ENFORCE-10.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"


class TestStep0Reference:
    def test_post_session_script_referenced(self):
        """ENFORCE-10: CLAUDE.md State Updates bullet 0 must reference post-session.sh."""
        content = CLAUDE_MD.read_text(encoding="utf-8")
        assert "post-session.sh" in content, (
            "ENFORCE-10: CLAUDE.md State Updates bullet 0 must reference post-session.sh"
        )

    def test_guarantees_step_0_phrase(self):
        """ENFORCE-10: CLAUDE.md must contain the phrase 'guarantees Step 0'."""
        content = CLAUDE_MD.read_text(encoding="utf-8")
        assert "guarantees Step 0" in content, (
            "ENFORCE-10: CLAUDE.md must contain the phrase 'guarantees Step 0' "
            "to make the enforcement mechanism explicit (see 03-RESEARCH.md Pattern 6)"
        )
