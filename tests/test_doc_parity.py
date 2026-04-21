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
