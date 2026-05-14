"""ROUTE-FOLLOWUP-03: CLAUDE.md is loaded at every session start. Semantic markers
lock the load-bearing structure (Step 3 routing rows + Guardrails section) so a
future edit that weakens routing precedence or removes a guardrail fails CI.

08-00 lands an existence-only stub. 08-07 fills in the row-token + guardrail-heading
assertions. The file lives in the test directory at this path so 08-07 can extend it.

Refresh workflow (for intentional CLAUDE.md edits):
1. Run: python3 -m pytest tests/test_claude_md_golden.py -v
2. Read the failure message — it names exactly which token(s) are now missing.
3. Update STEP3_ROW_TOKENS / PRECEDENCE_CALLOUT_TOKENS / GUARDRAIL_TOKENS to match.
4. Re-run; assert green.
5. Commit both files together so reviewers see the rule change explicitly.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

# Marker set 1 — Step 3 routing row order (condition-column tokens, unique per row)
# Offsets must be strictly increasing to enforce routing precedence order.
# These are the condition-column substrings from the Step 3 table in CLAUDE.md.
STEP3_ROW_TOKENS = [
    "No session logs exist",                        # Row 1: First Session
    "`onboarding_complete` is false",               # Row 2: Onboarding
    "Gap of 3+ days since last session",            # Row 3: Return
    "`autonomy_level` is `maintenance`",            # Row 4: Maintenance
    "Today's day-of-week matches `weekly_review_day`",  # Row 5: Weekly Review
    "`sprint.active` is true",                      # Row 6: Sprint Session
    "Phase B+ and today is a fluency day",          # Row 7: Fluency
    "| Otherwise",                                  # Row 8: Standard Session
]

# Marker set 2 — Precedence callout prose anchors
# ROUTE-IDs are not embedded in CLAUDE.md as literals; these prose phrases are the
# unique load-bearing anchors for each callout. 08-06 pairwise test transcribes
# the same precedence semantics in executable form — keep in sync.
# ROUTE-01: onboarding gap overlay  → "Gap precedence:"
# ROUTE-02: return > weekly review  → "Takes priority over weekly review"
# ROUTE-03: placement-val > sprint  → "placement validation takes priority"
# ROUTE-07: maintenance + weekly    → "Maintenance-mode learners still receive weekly reviews"
PRECEDENCE_CALLOUT_TOKENS = [
    "Gap precedence:",                                           # ROUTE-01
    "Takes priority over weekly review",                        # ROUTE-02
    "placement validation takes priority",                      # ROUTE-03
    "Maintenance-mode learners still receive weekly reviews",   # ROUTE-07
]

# Marker set 3 — Guardrail tokens
# If you intentionally remove or rewrite a guardrail, update this constant in the
# same commit. The diff makes the rule-change explicit in code review.
GUARDRAIL_TOKENS = [
    "Never skip the startup protocol",
    "Never advance to a new concept if 3+ concepts",
    "Never assign homework whose summed",
    "Never make the learner feel tested",
    "Never compare the learner",
    "Always check `curriculum/l1-interference.yaml`",
    "Always verify homework claims",
    "Never add more than 10 new Anki cards",
    "Never introduce more than 1 new grammar concept",
    "If a real-world encounter is mentioned",
    "Communication repair phrases are the highest-priority",
    "Always use the exact YAML schemas",
    "Always apply dialect-appropriate vocabulary",
    'Never mark a CORE concept as "acquired" unless',
    'Never mark a SECONDARY concept as "acquired"',
    "Never advance phases unless all CORE prerequisite",
    "Monitor carryover escalation",
    "Never overwrite vault files",
    "On fluency days, still run decision engine",
    "If the learner disagrees with a status assessment",
]


class TestClaudeMdSemanticMarkers:
    """ROUTE-FOLLOWUP-03: lock the load-bearing semantic structure of CLAUDE.md
    (Step 3 row order + precedence callouts + guardrails) so silent drift fails CI.

    If you intentionally remove or rewrite a guardrail, update GUARDRAIL_TOKENS in
    this file in the same commit. The diff makes the rule-change explicit in review.
    """

    def _content(self):
        return CLAUDE_MD.read_text(encoding="utf-8")

    def test_claude_md_exists(self):
        """CLAUDE.md must exist at repo root for all marker tests to be meaningful."""
        assert CLAUDE_MD.exists(), (
            "ROUTE-FOLLOWUP-03: CLAUDE.md missing — 08-07 cannot anchor markers."
        )

    def test_step3_rows_in_order(self):
        """Step 3 routing row tokens must all appear AND in strictly increasing offset
        order. A row reorder changes routing precedence silently — this catches it."""
        content = self._content()
        offsets = []
        for token in STEP3_ROW_TOKENS:
            idx = content.find(token)
            assert idx >= 0, f"Step 3 row token missing: {token!r}"
            offsets.append((token, idx))
        # Strictly increasing offsets enforce documented row order
        for (a_tok, a_idx), (b_tok, b_idx) in zip(offsets, offsets[1:]):
            assert a_idx < b_idx, (
                f"Step 3 row order violation: {a_tok!r} (@{a_idx}) appears AFTER "
                f"{b_tok!r} (@{b_idx}). Step 3 routing precedence depends on this order."
            )

    def test_precedence_callouts_present(self):
        """Precedence callout prose anchors must all be present in CLAUDE.md.
        08-06 pairwise priority test transcribes the same semantics — keep in sync."""
        content = self._content()
        missing = [t for t in PRECEDENCE_CALLOUT_TOKENS if t not in content]
        assert not missing, (
            f"Precedence callouts missing from CLAUDE.md: {missing}. "
            "08-06 pairwise priority test transcribes these — keep them in sync."
        )

    def test_guardrails_all_present(self):
        """Every guardrail token must be present as a substring of CLAUDE.md.
        If a guardrail was intentionally removed/rewritten, update GUARDRAIL_TOKENS
        in this file in the same commit so the diff is visible in code review."""
        content = self._content()
        missing = [t for t in GUARDRAIL_TOKENS if t not in content]
        assert not missing, (
            f"Guardrail token(s) missing from CLAUDE.md: {missing!r}. "
            "If a guardrail was intentionally removed/rewritten, update "
            "GUARDRAIL_TOKENS in this file in the same commit."
        )
