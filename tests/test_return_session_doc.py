"""Doc-prose tests for return-session.md warmth + non-clinical framing (Phase 6 ROUTE-04, ROUTE-05).

Each tier of return-session.md must open with warm tutor-facing prose before any numbered
mechanical step, and the word 'regression' must not appear in tutor-spoken or
learner-facing instructional prose — only in internal state-file references (skill-map,
system-health, error_rate fields, etc.).

Requirements covered: ROUTE-04, ROUTE-05.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RETURN_SESSION_MD = REPO_ROOT / "curriculum" / "tutor-guides" / "return-session.md"

# Words/phrases that mark an internal/state-file context — `regression` is allowed in
# lines containing any of these markers because they describe internal data fields,
# not tutor-spoken or learner-facing prose.
INTERNAL_MARKERS = (
    "skill-map",
    "skill_map",
    "state file",
    "state-file",
    "state/",
    "system-health",
    "system_health",
    "error_rate",
    "performance_unscaffolded",
    "performance_scaffolded",
    "(internal:",
    "internal:",
)

REGRESSION_PATTERN = re.compile(r"\bregress(ion|ions|ed|ing)\b", re.IGNORECASE)


def _read() -> str:
    return RETURN_SESSION_MD.read_text(encoding="utf-8")


def _extract_tier_block(content: str, tier_heading: str) -> str:
    """Return text between '### {tier_heading}' and the next '### ' heading (or section break)."""
    start_idx = content.find(f"### {tier_heading}")
    assert start_idx != -1, f"Tier section '### {tier_heading}' not found in return-session.md"
    # Find next H3 after this one
    next_h3 = content.find("\n### ", start_idx + 1)
    next_h2 = content.find("\n## ", start_idx + 1)
    candidates = [i for i in (next_h3, next_h2) if i != -1]
    end_idx = min(candidates) if candidates else len(content)
    return content[start_idx:end_idx]


class TestReturnSessionTierOpenings:
    """ROUTE-04: Each tier must open with warm tutor-facing prose before mechanical steps."""

    def _assert_tier_has_warm_opening(self, tier_heading: str):
        block = _extract_tier_block(_read(), tier_heading)
        # Plan 06-02 spec: each tier gets a '**Tutor's opening' marker.
        assert "**Tutor's opening" in block or "Tutor's opening" in block, (
            f"ROUTE-04: '### {tier_heading}' tier must include a 'Tutor's opening' line "
            "with warm acknowledgment prose BEFORE the numbered steps. "
            "See .planning/phases/06-route-routing-return-session-polish/06-02-PLAN.md."
        )

    def test_short_break_opens_with_warmth(self):
        self._assert_tier_has_warm_opening("Short Break (3-7 days)")

    def test_extended_break_opens_with_warmth(self):
        self._assert_tier_has_warm_opening("Extended Break (8-21 days)")

    def test_major_break_opens_with_warmth(self):
        self._assert_tier_has_warm_opening("Major Break (22+ days)")

    def test_extended_absence_opens_with_warmth(self):
        # The current heading is "Extended Absence (90+ days)" — match it loosely.
        content = _read()
        ea_idx = content.find("Extended Absence")
        assert ea_idx != -1, "ROUTE-04: 'Extended Absence' tier missing entirely"
        # Find next heading after this one
        next_h3 = content.find("\n### ", ea_idx + 1)
        next_h2 = content.find("\n## ", ea_idx + 1)
        candidates = [i for i in (next_h3, next_h2) if i != -1]
        end_idx = min(candidates) if candidates else len(content)
        block = content[ea_idx:end_idx]
        assert "**Tutor's opening" in block or "Tutor's opening" in block, (
            "ROUTE-04: 'Extended Absence (90+ days)' tier must include a 'Tutor's opening' line "
            "with warm acknowledgment prose BEFORE the numbered steps."
        )


class TestReturnSessionNoRegressionInProse:
    """ROUTE-05: 'regression' / 'regressed' must not appear in learner-facing or tutor-spoken
    prose. It may appear only in lines that reference internal state fields, or inside fenced
    code blocks."""

    def test_no_regression_word_in_learner_facing_prose(self):
        content = _read()
        offending_lines = []
        in_code_block = False
        for lineno, raw_line in enumerate(content.splitlines(), start=1):
            stripped = raw_line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            if not REGRESSION_PATTERN.search(raw_line):
                continue
            lower = raw_line.lower()
            if any(marker.lower() in lower for marker in INTERNAL_MARKERS):
                # Internal-only line — `regression` is allowed here as a state-field term.
                continue
            offending_lines.append((lineno, raw_line.rstrip()))
        assert not offending_lines, (
            "ROUTE-05: 'regression'/'regressed' must not appear in tutor-spoken or learner-facing "
            "prose. Either reword the line, or mark it as internal-only by referencing a state "
            "field (skill-map, system-health, error_rate, etc.) or adding an explicit '(internal:' "
            "marker. Offending lines:\n"
            + "\n".join(f"  L{n}: {text}" for n, text in offending_lines)
            + "\nSee .planning/phases/06-route-routing-return-session-polish/06-02-PLAN.md."
        )


class TestReturnSessionNeutralFraming:
    """ROUTE-05: The diagnostic must be describable in neutral terms learners can hear without
    the clinical 'regression' word."""

    def test_neutral_framing_phrase_present(self):
        content = _read().lower()
        neutral_phrases = (
            "see what's stuck",
            "see what stuck",
            "see what stayed",
            "stayed with you",
            "needs a refresh",
            "see how things landed",
            "how it landed",
            "what's still there",
        )
        present = [p for p in neutral_phrases if p in content]
        assert present, (
            "ROUTE-05: return-session.md must include at least one neutral framing phrase that "
            "describes the diagnostic in learner-facing language (e.g., 'see what's stuck', "
            "'needs a refresh', 'stayed with you'). None found. "
            "See .planning/phases/06-route-routing-return-session-polish/06-02-PLAN.md."
        )
