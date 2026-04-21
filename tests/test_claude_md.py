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


# =============================================================================
# Phase 5 LOAD: Wave 0 RED-scaffolding tests for CLAUDE.md prose edits
# =============================================================================


class TestHomeworkGuardrailCitesEnforcer:
    """LOAD-05 / D-08: CLAUDE.md L179 area rewritten to cite study_time_budget.daily_maximum + today_stretch + check-session-log.py + estimated_minutes."""

    def test_daily_maximum_cited(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        idx_stb = content.find("study_time_budget")
        idx_max = content.find("daily_maximum")
        assert idx_stb != -1 and idx_max != -1, (
            "LOAD-05/D-08: both study_time_budget and daily_maximum must be present in CLAUDE.md"
        )
        assert abs(idx_max - idx_stb) < 300, (
            "LOAD-05/D-08: study_time_budget and daily_maximum must appear close together in CLAUDE.md L179 guardrail"
        )

    def test_today_stretch_cited(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        assert "today_stretch" in content, \
            "LOAD-05/D-08: CLAUDE.md L179 must cite today_stretch"

    def test_enforcer_cited(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        assert "check-session-log.py" in content, \
            "LOAD-05/D-08: CLAUDE.md L179 must name check-session-log.py as the enforcer"

    def test_estimated_minutes_cited(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        assert "estimated_minutes" in content, \
            "LOAD-05/Pitfall-1/D-08: CLAUDE.md L179 must cite estimated_minutes (NOT estimated_duration)"


class TestAcquisitionRuleSplit:
    """LOAD-01 / D-02: CLAUDE.md L191 acquisition rule splits by category.
    Core gate mentions error_rate + grammar AND vocabulary; secondary gate mentions pronunciation/writing/cultural."""

    def test_mentions_grammar_for_core_gate(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        assert "grammar" in content, \
            "LOAD-01/D-02: CLAUDE.md L191 must mention 'grammar' for core gate"

    def test_mentions_vocabulary_for_core_gate(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        assert "vocabulary" in content, (
            "LOAD-01/D-02: CLAUDE.md L191 must mention 'vocabulary' as part of core category "
            "(has error_rate_production on error_tracking)"
        )

    def test_mentions_secondary_category(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        # D-02: secondary is pronunciation/writing/cultural_awareness
        assert ("pronunciation" in content and "cultural" in content) or "secondary" in content.lower(), (
            "LOAD-01/D-02: CLAUDE.md L191 must reference secondary categories (pronunciation, writing, cultural_awareness) OR use the word 'secondary'"
        )


class TestPhaseTransitionGuideReference:
    """LOAD-02 / D-03: CLAUDE.md L192 must reference phase-transition-guide.md for the Core/Secondary prereq split."""

    def test_references_phase_transition_guide(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        assert "phase-transition-guide.md" in content, \
            "LOAD-02/D-03: CLAUDE.md L192 must reference phase-transition-guide.md for prerequisite split"


class TestInputOrchestrationCitesBudget:
    """LOAD-06 / D-09: input-orchestration.md §Section 4 Step 4 cites study_time_budget explicitly."""

    def test_input_orchestration_mentions_budget(self):
        p = REPO_ROOT / "curriculum" / "tutor-guides" / "input-orchestration.md"
        content = p.read_text(encoding="utf-8")
        assert "study_time_budget" in content, (
            "LOAD-06/D-09: curriculum/tutor-guides/input-orchestration.md must cite schedule.yaml.study_time_budget "
            "(Section 4 Step 4 cross-reference per D-09)"
        )

    def test_input_orchestration_mentions_daily_target(self):
        p = REPO_ROOT / "curriculum" / "tutor-guides" / "input-orchestration.md"
        content = p.read_text(encoding="utf-8")
        assert "daily_target" in content, \
            "LOAD-06/D-09: input-orchestration.md §4 Step 4 must cite daily_target"

    def test_input_orchestration_mentions_daily_maximum(self):
        p = REPO_ROOT / "curriculum" / "tutor-guides" / "input-orchestration.md"
        content = p.read_text(encoding="utf-8")
        assert "daily_maximum" in content, \
            "LOAD-06/D-09: input-orchestration.md §4 Step 4 must cite daily_maximum"


class TestHomeworkLoadRatingInReview:
    """LOAD-04 / D-12: CLAUDE.md Review & Warm-up (L94-101) must prompt for homework_load_rating capture."""

    def test_review_mentions_load_rating(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        assert "homework_load_rating" in content, \
            "LOAD-04/D-12: CLAUDE.md Review & Warm-up must reference homework_load_rating capture"
