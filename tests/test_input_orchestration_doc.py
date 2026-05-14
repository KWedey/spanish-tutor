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


# =============================================================================
# Phase 8 FOLLOWUP: CURR-FOLLOWUP-04 — reading debrief Section 2c
# =============================================================================


class TestReadingDebriefSection2c:
    """CURR-FOLLOWUP-04: input-orchestration.md Section 2 (Comprehension Debrief) must
    include a Section 2c that documents the reading-debrief flow using content_summary
    and chapter_range, parallel to the listening flow already in Section 2."""

    def _read(self):
        return INPUT_ORCHESTRATION.read_text(encoding="utf-8")

    def test_reading_debrief_subsection_present(self):
        """A heading or sub-heading containing 'reading' and 'debrief' (case-insensitive)
        must exist between Section 2 and Section 3 of input-orchestration.md."""
        import re
        content = self._read()
        # Find Section 2 and Section 3 boundaries
        sec2_match = re.search(r"^##\s+Section\s+2\b", content, re.MULTILINE | re.IGNORECASE)
        sec3_match = re.search(r"^##\s+Section\s+3\b", content, re.MULTILINE | re.IGNORECASE)
        assert sec2_match, "CURR-FOLLOWUP-04: Section 2 heading not found in input-orchestration.md"
        assert sec3_match, "CURR-FOLLOWUP-04: Section 3 heading not found in input-orchestration.md"
        section2_block = content[sec2_match.start():sec3_match.start()]
        # Look for a heading containing both 'reading' and 'debrief' (case-insensitive)
        heading_pattern = re.compile(r"^#{2,4}.*reading.*debrief", re.MULTILINE | re.IGNORECASE)
        alt_pattern = re.compile(r"^#{2,4}.*debrief.*reading", re.MULTILINE | re.IGNORECASE)
        assert heading_pattern.search(section2_block) or alt_pattern.search(section2_block), (
            "CURR-FOLLOWUP-04: input-orchestration.md Section 2 must contain a heading "
            "with 'reading' and 'debrief' (Section 2c — Reading Debrief). "
            "See .planning/phases/08-followup-v1.1-improvements/08-05-PLAN.md."
        )

    def test_reading_debrief_references_content_summary(self):
        """The reading-debrief section must explicitly cite content_summary and
        chapter_range from media-bank.yaml prescriptive_episodes.reading."""
        import re
        content = self._read()
        sec2_match = re.search(r"^##\s+Section\s+2\b", content, re.MULTILINE | re.IGNORECASE)
        sec3_match = re.search(r"^##\s+Section\s+3\b", content, re.MULTILINE | re.IGNORECASE)
        assert sec2_match and sec3_match, "CURR-FOLLOWUP-04: Section 2/3 boundaries not found"
        section2_block = content[sec2_match.start():sec3_match.start()]
        assert "content_summary" in section2_block, (
            "CURR-FOLLOWUP-04: the reading-debrief section must cite `content_summary` "
            "(the field on prescriptive_episodes.reading entries that drives comprehension probes)."
        )
        assert "chapter_range" in section2_block, (
            "CURR-FOLLOWUP-04: the reading-debrief section must cite `chapter_range` "
            "(the field that scopes the debrief to the assigned chapters)."
        )


class TestInputOrchestrationSchemaFieldDrift:
    """Audit H-2 + M-5 regression guards.

    Wave B found two drift sites between input-orchestration.md and the
    schema/validator. Tests here assert the doc uses the canonical field
    names so a tutor agent following the prose verbatim writes session-log
    fields the schema accepts and the validator counts.

    Same anti-pattern (CC-1) as the 08-02 dead-code finding: a contract
    documented in prose but never asserted in code is silently drift-prone.
    """

    def _read(self):
        return INPUT_ORCHESTRATION.read_text(encoding="utf-8")

    def test_uses_estimated_minutes_not_input_minutes(self):
        """Audit H-2: the per-assignment time field is `estimated_minutes`
        (schemas/session-log.schema.yaml > assignments.item_schema). Earlier
        revisions of this doc said `input_minutes:` — a name the budget
        enforcer at scripts/check-session-log.py never reads. A tutor
        following the doc verbatim shipped a 0-minute assignment and the
        homework-budget WARN never fired.
        """
        content = self._read()
        # The bare prose phrase "input_minutes" must NOT appear as a field-name
        # token. Allow it inside a "previously named X, now Y" deprecation note
        # if one is ever added — match the colon-suffixed YAML-key form only.
        assert "input_minutes:" not in content, (
            "audit H-2: input-orchestration.md must not document `input_minutes:` "
            "as the per-assignment time field; the canonical name is "
            "`estimated_minutes:` (per schemas/session-log.schema.yaml)."
        )
        assert "estimated_minutes:" in content, (
            "audit H-2: input-orchestration.md must document `estimated_minutes:` "
            "explicitly so the tutor uses the schema-recognized field name."
        )

    def test_dialect_advisory_uses_canonical_voseo_plus_vosotros(self):
        """Audit M-5: the schema enum for dialect_advisory is
        ['voseo', 'vosotros', 'voseo+vosotros'] — note the literal `+`.
        Earlier prose suggested 'comma-separated' which a tutor would
        write as `voseo,vosotros`, breaking the enum.
        """
        content = self._read()
        # Reject the comma-separated form as a documented value
        assert "voseo,vosotros" not in content, (
            "audit M-5: input-orchestration.md must not suggest `voseo,vosotros` "
            "as a value for dialect_advisory; the schema enum requires the "
            "`voseo+vosotros` form (literal `+`)."
        )
        assert "voseo+vosotros" in content, (
            "audit M-5: input-orchestration.md must document the `voseo+vosotros` "
            "literal so the prose matches the session-log schema enum."
        )
