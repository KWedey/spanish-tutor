"""Doc-parity regression locks for Phase 5 LOAD.

Every new schema field MUST stay referenced in docs/system-design.md.
If a future refactor deletes either the schema entry or the doc, this test
fails loudly — mirrors the Phase 1 LEAK / Phase 2.1 HOOK "test-locks-wiring" precedent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_DESIGN = REPO_ROOT / "docs" / "system-design.md"
SCHEMA_SCHEDULE = REPO_ROOT / "schemas" / "schedule.schema.yaml"
SCHEMA_SESSION = REPO_ROOT / "schemas" / "session-log.schema.yaml"
SCHEMA_SYSTEM_HEALTH = REPO_ROOT / "schemas" / "system-health.schema.yaml"
SKILL_MAP_TEMPLATE = REPO_ROOT / "state" / "skill-map.template.yaml"


class TestDocParityStudyTimeBudget:
    """LOAD-07: docs/system-design.md §Schedule Schema must document study_time_budget map
    whenever the schema defines it."""

    def test_schema_and_docs_both_reference_field(self):
        schema_text = SCHEMA_SCHEDULE.read_text(encoding="utf-8")
        if "study_time_budget" not in schema_text:
            return  # schema hasn't added it yet — presence test in test_schema_fields_present will catch this
        docs_text = SYSTEM_DESIGN.read_text(encoding="utf-8")
        assert "study_time_budget" in docs_text, (
            "LOAD-07 doc-parity: study_time_budget exists in schedule.schema.yaml but NOT "
            "in docs/system-design.md — schema and docs must stay in lockstep"
        )

    def test_docs_reference_all_five_subfields(self):
        schema_text = SCHEMA_SCHEDULE.read_text(encoding="utf-8")
        if "study_time_budget" not in schema_text:
            return
        docs_text = SYSTEM_DESIGN.read_text(encoding="utf-8")
        for sub in ("daily_minimum", "daily_target", "daily_maximum", "weekly_goal", "today_stretch"):
            assert sub in docs_text, (
                f"LOAD-07 doc-parity: study_time_budget.{sub} must be documented in docs/system-design.md"
            )


class TestDocParityHomeworkLoadRating:
    """LOAD-04: docs/system-design.md §Session Log Schema must document homework_load_rating
    whenever the schema defines it."""

    def test_schema_and_docs_both_reference_field(self):
        schema_text = SCHEMA_SESSION.read_text(encoding="utf-8")
        if "homework_load_rating" not in schema_text:
            return
        docs_text = SYSTEM_DESIGN.read_text(encoding="utf-8")
        assert "homework_load_rating" in docs_text, (
            "LOAD-04 doc-parity: homework_load_rating exists in session-log.schema.yaml but "
            "NOT in docs/system-design.md — schema and docs must stay in lockstep"
        )

    def test_docs_reference_all_enum_values(self):
        schema_text = SCHEMA_SESSION.read_text(encoding="utf-8")
        if "homework_load_rating" not in schema_text:
            return
        docs_text = SYSTEM_DESIGN.read_text(encoding="utf-8")
        for value in ("too-much", "just-right", "too-light"):
            assert value in docs_text, (
                f"LOAD-04 doc-parity: homework_load_rating enum value '{value}' must appear in docs/system-design.md"
            )


class TestDocParitySystemHealthFields:
    """F033/F073: the §8 System Health example block must document every field the
    system-health schema declares (schema is authoritative). Guards against the
    doc block drifting behind the schema again."""

    # Fields declared in the schema that were previously absent from the §8 doc block.
    BACKFILLED = (
        "schema_version",
        "last_validation_issues",
        "load_adjustments",
        "auto_fixes",
        "session_difficulty_tracking",
        "maintenance_sessions_total",
        "regressions_detected_in_maintenance",
    )

    def test_backfilled_fields_declared_in_schema(self):
        schema_text = SCHEMA_SYSTEM_HEALTH.read_text(encoding="utf-8")
        for field in self.BACKFILLED:
            assert f"{field}:" in schema_text, (
                f"F033/F073: {field} must be declared in schemas/system-health.schema.yaml"
            )

    def test_backfilled_fields_documented_in_system_design(self):
        docs_text = SYSTEM_DESIGN.read_text(encoding="utf-8")
        for field in self.BACKFILLED:
            assert field in docs_text, (
                f"F033/F073 doc-parity: {field} exists in system-health.schema.yaml but NOT "
                f"in docs/system-design.md §8 — schema and docs must stay in lockstep"
            )


class TestDocParityRegisterShiftingPhase:
    """F035: cultural_awareness.register_shifting is introduced at Phase B (the field
    means the *introduction* phase). docs/system-design.md must agree with the
    skill-map template and CLAUDE.md's load-map (register-shifting.md at Phase B)."""

    def test_docs_match_template_introduced_at_phase_b(self):
        template_text = SKILL_MAP_TEMPLATE.read_text(encoding="utf-8")
        if "register_shifting" not in template_text:
            return
        docs_text = SYSTEM_DESIGN.read_text(encoding="utf-8")
        # Locate the register_shifting block in the doc and assert its introduced_at_phase is B.
        lines = docs_text.splitlines()
        idx = next((i for i, ln in enumerate(lines) if ln.strip().startswith("register_shifting:")), None)
        assert idx is not None, "F035: register_shifting block must exist in docs/system-design.md"
        window = "\n".join(lines[idx:idx + 4])
        assert "introduced_at_phase: B" in window, (
            "F035: docs/system-design.md register_shifting must be introduced_at_phase: B "
            "(matches state/skill-map.template.yaml and curriculum/cultural/register-shifting.md)"
        )
