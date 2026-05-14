"""STATE-FOLLOWUP-01: docs/canary-first-session.md must exist and document the
four-phase canary protocol (pre-session, during, post-session, rollback)."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANARY_DOC = REPO_ROOT / "docs" / "canary-first-session.md"


class TestCanaryFirstSessionDoc:
    def test_doc_exists(self):
        assert CANARY_DOC.exists(), (
            "STATE-FOLLOWUP-01: docs/canary-first-session.md must exist. "
            "See .planning/phases/08-followup-v1.1-improvements/08-08-PLAN.md."
        )

    def test_required_sections_present(self):
        """The protocol must cover four phases — pre-session, during, post-session,
        rollback — each as a level-2 `##` heading line. Heading-anchored regex
        prevents the substring `during` matching body prose like
        "capture observations during the session"."""
        import re
        content = CANARY_DOC.read_text(encoding="utf-8")
        required_heading_patterns = [
            (r"^##\s+.*pre-session", "## Pre-session"),
            (r"^##\s+.*during", "## During session"),
            (r"^##\s+.*post-session", "## Post-session"),
            (r"^##\s+.*rollback", "## Rollback"),
        ]
        missing = [
            label for pat, label in required_heading_patterns
            if not re.search(pat, content, re.MULTILINE | re.IGNORECASE)
        ]
        assert not missing, (
            f"STATE-FOLLOWUP-01: canary doc missing required `##` heading(s): "
            f"{missing}. Each phase must be a level-2 heading; substring matches "
            "elsewhere in the doc do not count."
        )
