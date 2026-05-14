"""RED tests for input-orchestration.md dialect re-filter advisory (Phase 7 CURR-02).

CLAUDE.md Step 4 loads input-orchestration.md for every post-onboarding session,
and Section 1 Step 2 is where dialect preference is filtered. The dialect
re-filter advisory must live there so the tutor surfaces voseo/vosotros
mismatches at assignment time rather than waiting for the learner to be
confused by content that doesn't match `target_dialect`.

Requirements covered: CURR-02.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_ORCHESTRATION = REPO_ROOT / "curriculum" / "tutor-guides" / "input-orchestration.md"


class TestInputOrchestrationDialectRefilter:
    """CURR-02: input-orchestration.md Section 1 Step 2 must document the dialect
    re-filter advisory for mixed/neutral resources containing dialect-specific forms."""

    def _read(self):
        return INPUT_ORCHESTRATION.read_text(encoding="utf-8")

    def test_voseo_advisory_documented(self):
        """An es-AR or es-UY learner receiving a `mixed`/`neutral` resource gets a voseo
        advisory called out in the guide."""
        content = self._read().lower()
        assert "voseo" in content, (
            "CURR-02: input-orchestration.md must mention 'voseo' to document the "
            "advisory for es-AR / es-UY learners assigned `mixed`/`neutral` resources. "
            "See .planning/phases/07-curr-curriculum-content/07-02-PLAN.md."
        )

    def test_vosotros_advisory_documented(self):
        """A non-peninsular learner receiving a `peninsular`/`mixed_with_spain` resource
        gets a vosotros advisory."""
        content = self._read().lower()
        assert "vosotros" in content, (
            "CURR-02: input-orchestration.md must mention 'vosotros' to document the "
            "advisory for non-peninsular learners assigned `peninsular` or "
            "`mixed_with_spain` resources."
        )

    def test_refilter_concept_named(self):
        """The guide explicitly uses 're-filter' or equivalent language so the rule is
        searchable and the audit finding is closed."""
        content = self._read().lower()
        markers = ("re-filter", "refilter", "dialect advisory", "dialect re-filter", "dialect mismatch advisory")
        present = [m for m in markers if m in content]
        assert present, (
            "CURR-02: input-orchestration.md must explicitly name the re-filter / "
            "advisory concept (one of: 're-filter', 'refilter', 'dialect advisory', "
            "'dialect re-filter', 'dialect mismatch advisory')."
        )

    def test_refilter_lives_in_section_1_step_2(self):
        """The advisory must live in Section 1 Step 2 (Filter resources), not buried
        elsewhere. Step 2 is where dialect preference already lives — keep them together."""
        content = self._read()
        step2_idx = content.find("### Step 2 — Filter resources")
        assert step2_idx != -1, "CURR-02: Section 1 Step 2 header not found"
        # Section 1 Step 3 is the natural boundary
        step3_idx = content.find("### Step 3 —", step2_idx)
        assert step3_idx != -1, "CURR-02: Section 1 Step 3 header not found"
        step2_block = content[step2_idx:step3_idx].lower()
        assert "voseo" in step2_block or "vosotros" in step2_block or "re-filter" in step2_block, (
            "CURR-02: the dialect advisory must live inside Section 1 Step 2 "
            "(Filter resources) — found dialect terminology elsewhere in the file but "
            "not in Step 2."
        )
