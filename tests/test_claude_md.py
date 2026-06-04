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


class TestD11CounterMaintenance:
    """P1-1 (audit): CLAUDE.md must instruct the tutor to MAINTAIN the D-11 streak
    counters (consecutive_too_much_count / consecutive_just_right_count). They are
    tutor-maintained 'pending-action' flags; without explicit maintenance they stay
    at 0 in production and validate-state's check_daily_target_tier_drift /
    check_just_right_restore_drift can never fire (the D-11 guardrail is dormant)."""

    def test_both_counters_instructed(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        for field in ("consecutive_too_much_count", "consecutive_just_right_count"):
            assert field in content, (
                f"P1-1: CLAUDE.md must instruct maintaining {field} so the D-11 "
                "tier-drift validator can fire (the counter is tutor-maintained)."
            )

    def test_maintenance_lives_in_state_updates(self):
        content = CLAUDE_MD.read_text(encoding="utf-8")
        su = content.find("## State Updates")
        assert su != -1, "CLAUDE.md must have a State Updates section"
        assert content.find("consecutive_too_much_count", su) != -1, (
            "P1-1: the D-11 counter-maintenance bookkeeping must appear in the "
            "State Updates section (where schedule.yaml counters are persisted)."
        )


# =============================================================================
# Phase 6 ROUTE: Wave 0 RED-scaffolding tests for CLAUDE.md Step 3 precedence
# =============================================================================


def _extract_step3_table(content: str) -> str:
    """Return the body of the Step 3 routing table (between table header and the Priority note)."""
    header_idx = content.find("| Condition | Session Type | Load |")
    assert header_idx != -1, "Step 3 routing table header not found in CLAUDE.md"
    end_idx = content.find("**Gap detection:**", header_idx)
    if end_idx == -1:
        end_idx = content.find("**Priority note:**", header_idx)
    assert end_idx != -1, "Step 3 routing table end marker not found in CLAUDE.md"
    return content[header_idx:end_idx]


class TestRoutingPrecedence:
    """ROUTE-01/02/03: CLAUDE.md Step 3 precedence rules must live at the row, not in footnotes or distant guardrails."""

    def test_onboarding_row_states_gap_precedence_inline(self):
        """ROUTE-01: Onboarding row must contain an explicit 'Gap precedence' marker so the
        gap-during-onboarding behavior is co-located with the routing decision, not split
        between Step 1b and a footnote."""
        table = _extract_step3_table(CLAUDE_MD.read_text(encoding="utf-8"))
        # Find the Onboarding row specifically
        onboarding_idx = table.find("Onboarding")
        assert onboarding_idx != -1, "ROUTE-01: Onboarding row missing from Step 3 table"
        # Next row starts at the next '\n|' that introduces 'Gap of 3+ days' or similar
        next_row_idx = table.find("\n| Gap of", onboarding_idx)
        if next_row_idx == -1:
            next_row_idx = table.find("\n| `autonomy_level`", onboarding_idx)
        assert next_row_idx != -1, "ROUTE-01: could not locate Onboarding row boundary"
        onboarding_row = table[onboarding_idx:next_row_idx]
        assert "Gap precedence" in onboarding_row, (
            "ROUTE-01: Onboarding row must contain an explicit '**Gap precedence:**' callout "
            "so the gap-during-onboarding behavior is co-located with the routing decision. "
            "See .planning/phases/06-route-routing-return-session-polish/06-01-PLAN.md."
        )

    def test_return_row_states_weekly_review_precedence_inline(self):
        """ROUTE-02: Return row must state weekly-review precedence inline, not 9 lines below in
        a separate Priority note."""
        table = _extract_step3_table(CLAUDE_MD.read_text(encoding="utf-8"))
        return_idx = table.find("Gap of 3+ days")
        assert return_idx != -1, "ROUTE-02: Return row missing from Step 3 table"
        next_row_idx = table.find("\n| `autonomy_level`", return_idx)
        assert next_row_idx != -1, "ROUTE-02: could not locate Return row boundary"
        return_row = table[return_idx:next_row_idx]
        # The Return row must mention weekly review and the precedence direction
        has_weekly_mention = "weekly review" in return_row.lower()
        has_priority_marker = (
            "takes priority" in return_row.lower()
            or "defer weekly review" in return_row.lower()
            or "overrides weekly" in return_row.lower()
        )
        assert has_weekly_mention and has_priority_marker, (
            "ROUTE-02: Return row must inline the weekly-review precedence — "
            "must mention 'weekly review' AND a priority phrase ('takes priority' / "
            "'defer weekly review' / 'overrides weekly'). "
            "See .planning/phases/06-route-routing-return-session-polish/06-01-PLAN.md."
        )

    def test_sprint_row_states_placement_validation_override(self):
        """ROUTE-03: Sprint row must mention placement_validation override so the rule is
        consistent with the bottom-of-file guardrail. Either the row carries the override
        (preferred), or both row and guardrail must cross-reference each other so they
        cannot diverge."""
        content = CLAUDE_MD.read_text(encoding="utf-8")
        table = _extract_step3_table(content)
        sprint_idx = table.find("sprint.active")
        assert sprint_idx != -1, "ROUTE-03: Sprint row missing from Step 3 table"
        next_row_idx = table.find("\n|", sprint_idx + 1)
        assert next_row_idx != -1, "ROUTE-03: could not locate Sprint row boundary"
        sprint_row = table[sprint_idx:next_row_idx]
        row_mentions_override = (
            "placement_validation" in sprint_row
            or "placement-validation" in sprint_row.lower()
        )
        # Allow the consistency to be achieved by a cross-reference in the bottom guardrail
        bottom_cross_ref = (
            "see CLAUDE.md Step 3 Sprint row" in content
            or "see Sprint row" in content
        )
        assert row_mentions_override or bottom_cross_ref, (
            "ROUTE-03: Sprint row must mention the placement_validation override, OR the bottom "
            "guardrail must explicitly cross-reference the Sprint row. Two rules in two locations "
            "without cross-reference is the bug being fixed. "
            "See .planning/phases/06-route-routing-return-session-polish/06-01-PLAN.md."
        )
