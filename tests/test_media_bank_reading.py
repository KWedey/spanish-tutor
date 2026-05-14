"""RED tests for media-bank.yaml prescriptive_episodes.reading (Phase 7 CURR-01).

These tests fail against the current media-bank.yaml (which only has
`prescriptive_episodes.listening`). They pass once 07-01 adds the
`reading:` sub-key with ≥5 entries covering R2-R4 and ≥2 dialects.

Requirements covered: CURR-01.
"""
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MEDIA_BANK = REPO_ROOT / "curriculum" / "media-bank.yaml"

REQUIRED_FIELDS = {"source", "title", "level", "cefr", "dialect", "chapter_range", "content_summary"}


class TestMediaBankReadingPrescriptive:
    """CURR-01: media-bank.yaml prescriptive_episodes must include a `reading` sub-key
    with at least 5 entries covering the R2 → R4 arc, each carrying the full field set."""

    def _load(self):
        return yaml.safe_load(MEDIA_BANK.read_text(encoding="utf-8"))

    def test_reading_subkey_present(self):
        data = self._load()
        prescriptive = data.get("prescriptive_episodes") or {}
        assert "reading" in prescriptive, (
            "CURR-01: media-bank.yaml prescriptive_episodes must have a `reading` sub-key "
            "(parallel to the existing `listening` sub-key). "
            "See .planning/phases/07-curr-curriculum-content/07-01-PLAN.md."
        )

    def test_reading_has_at_least_5_entries(self):
        data = self._load()
        entries = (data.get("prescriptive_episodes") or {}).get("reading") or []
        assert len(entries) >= 5, (
            f"CURR-01: prescriptive_episodes.reading must contain at least 5 entries "
            f"(found {len(entries)}). See REQUIREMENTS.md CURR-01."
        )

    def test_every_entry_has_required_fields(self):
        data = self._load()
        entries = (data.get("prescriptive_episodes") or {}).get("reading") or []
        offenders = []
        for i, entry in enumerate(entries):
            missing = REQUIRED_FIELDS - set((entry or {}).keys())
            if missing:
                offenders.append((i, sorted(missing), (entry or {}).get("title", "<no title>")))
        assert not offenders, (
            "CURR-01: every reading entry must have all required fields "
            f"({sorted(REQUIRED_FIELDS)}). Offenders:\n"
            + "\n".join(f"  [{i}] '{title}' missing {missing}" for i, missing, title in offenders)
        )

    def test_levels_span_r2_to_r4(self):
        """At least one entry per level R2, R3, R4 to cover the graded → authentic arc."""
        data = self._load()
        entries = (data.get("prescriptive_episodes") or {}).get("reading") or []
        levels_present = {e.get("level") for e in entries if isinstance(e, dict)}
        for required_level in ("R2", "R3", "R4"):
            assert required_level in levels_present, (
                f"CURR-01: at least one reading entry must be at level {required_level} "
                f"(found levels: {sorted(l for l in levels_present if l)}). The graded-reader → "
                "authentic-literature arc must be covered."
            )

    def test_dialect_coverage(self):
        """At least 2 distinct dialects across entries — broader than a single regional bias."""
        data = self._load()
        entries = (data.get("prescriptive_episodes") or {}).get("reading") or []
        dialects = {e.get("dialect") for e in entries if isinstance(e, dict) and e.get("dialect")}
        assert len(dialects) >= 2, (
            f"CURR-01: reading entries must cover at least 2 distinct dialects "
            f"(found: {sorted(dialects)}). A single-dialect reading bank cannot serve "
            "learners with varying target_dialect."
        )
