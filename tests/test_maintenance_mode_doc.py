"""Doc-prose test for maintenance-mode.md weekly-review coexistence (Phase 6 ROUTE-07).

CLAUDE.md Step 3 Maintenance row says 'Maintenance-mode learners still receive weekly
reviews — when weekly_review_day matches today, run the weekly review with
maintenance-specific focus.' The maintenance-mode guide must document this so the
routing decision and the guide content stay aligned.

Requirements covered: ROUTE-07.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAINTENANCE_MODE_MD = REPO_ROOT / "curriculum" / "tutor-guides" / "maintenance-mode.md"


def _extract_weekly_review_section(content: str) -> str | None:
    """Return the body of the first section whose heading mentions 'weekly review'
    (case-insensitive), bounded by the next same-or-higher-level heading. Returns
    None if no such heading exists."""
    lines = content.splitlines()
    start_idx = None
    start_level = 0
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped.startswith("#") and "weekly review" in stripped.lower():
            # Count leading '#' to know heading level
            start_level = len(stripped) - len(stripped.lstrip("#"))
            start_idx = i
            break
    if start_idx is None:
        return None
    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        s = lines[j].strip()
        if s.startswith("#"):
            level = len(s) - len(s.lstrip("#"))
            if level <= start_level:
                end_idx = j
                break
    return "\n".join(lines[start_idx:end_idx])


class TestMaintenanceWeeklyReview:
    """ROUTE-07: maintenance-mode.md must document weekly-review coexistence."""

    def test_weekly_review_section_exists(self):
        content = MAINTENANCE_MODE_MD.read_text(encoding="utf-8")
        section = _extract_weekly_review_section(content)
        assert section is not None, (
            "ROUTE-07: maintenance-mode.md must contain a heading mentioning 'Weekly Review' "
            "(e.g., '## Weekly Review in Maintenance Mode'). "
            "See .planning/phases/06-route-routing-return-session-polish/06-03-PLAN.md."
        )

    def test_weekly_review_section_describes_maintenance_specific_focus(self):
        content = MAINTENANCE_MODE_MD.read_text(encoding="utf-8")
        section = _extract_weekly_review_section(content)
        assert section is not None, (
            "ROUTE-07: weekly-review section is missing — cannot check focus phrases. "
            "Add the section first (see test_weekly_review_section_exists)."
        )
        section_lower = section.lower()
        focus_phrases = (
            "retention check",
            "motivation pulse",
            "parking-lot triage",
            "parking lot triage",
            "spot-check",
            "spot check",
            "maintenance-specific",
            "maintenance specific",
        )
        present = [p for p in focus_phrases if p in section_lower]
        assert present, (
            "ROUTE-07: maintenance weekly-review section must describe maintenance-specific "
            "focus (e.g., 'retention check', 'motivation pulse', 'parking-lot triage', "
            "'spot-check'). None found in the Weekly Review section. "
            "See .planning/phases/06-route-routing-return-session-polish/06-03-PLAN.md."
        )

    def test_weekly_review_section_references_weekly_review_day(self):
        content = MAINTENANCE_MODE_MD.read_text(encoding="utf-8")
        assert "weekly_review_day" in content, (
            "ROUTE-07: maintenance weekly-review section must reference the "
            "`weekly_review_day` field (the trigger CLAUDE.md routes on). "
            "See .planning/phases/06-route-routing-return-session-polish/06-03-PLAN.md."
        )
