"""Doc-prose test for onboarding-guide.md gap-in-onboarding section (Phase 6 ROUTE-06).

CLAUDE.md Step 3 Onboarding row implies a gap-during-onboarding resume path
(load return-session.md, run diagnostic, resume from same session number).
The guide it loads must document that path so CLAUDE.md and the guide agree.

Requirements covered: ROUTE-06.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ONBOARDING_GUIDE_MD = REPO_ROOT / "curriculum" / "tutor-guides" / "onboarding-guide.md"


class TestOnboardingGuideGap:
    """ROUTE-06: onboarding-guide.md must document the gap-in-onboarding resume path."""

    def test_gap_during_onboarding_section_exists(self):
        content = ONBOARDING_GUIDE_MD.read_text(encoding="utf-8")
        # A heading containing 'gap' (any case) at any heading level (## or ###)
        has_gap_heading = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") and "gap" in stripped.lower():
                has_gap_heading = True
                break
        assert has_gap_heading, (
            "ROUTE-06: onboarding-guide.md must contain a heading mentioning 'gap' "
            "(e.g., '## Gap During Onboarding'). "
            "See .planning/phases/06-route-routing-return-session-polish/06-03-PLAN.md."
        )

    def test_gap_section_describes_same_step_resume(self):
        content = ONBOARDING_GUIDE_MD.read_text(encoding="utf-8").lower()
        # The section must describe resuming from the same session number, not advancing.
        same_step_phrases = (
            "same session number",
            "resume from the same",
            "do not advance",
            "don't advance",
            "do not skip",
            "don't skip",
            "same `current_onboarding_session`",
            "same current_onboarding_session",
        )
        present = [p for p in same_step_phrases if p in content]
        assert present, (
            "ROUTE-06: the gap-during-onboarding section must describe the resume rule "
            "(stay on the same session number, do not advance). Expected one of: "
            f"{same_step_phrases}. "
            "See .planning/phases/06-route-routing-return-session-polish/06-03-PLAN.md."
        )

    def test_gap_section_references_return_session_guide(self):
        content = ONBOARDING_GUIDE_MD.read_text(encoding="utf-8")
        assert "return-session.md" in content, (
            "ROUTE-06: gap-during-onboarding section must cross-reference "
            "`return-session.md` (CLAUDE.md Onboarding row already loads it; the guide "
            "should acknowledge the interaction). "
            "See .planning/phases/06-route-routing-return-session-polish/06-03-PLAN.md."
        )
