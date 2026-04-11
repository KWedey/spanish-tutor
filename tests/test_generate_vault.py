"""Tests for scripts/generate-vault.py vault generation functions."""
import copy
import importlib
import sys
from pathlib import Path

import pytest
import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

gv = importlib.import_module("generate-vault")

write_vault_file = gv.write_vault_file
file_has_generated_marker = gv.file_has_generated_marker
update_frontmatter_in_file = gv.update_frontmatter_in_file
yaml_frontmatter = gv.yaml_frontmatter
_yaml_value = gv._yaml_value
concept_id_to_title = gv.concept_id_to_title
run_full = gv.run_full
run_session = gv.run_session
VAULT_DIR = gv.VAULT_DIR

# Import conftest data
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
from conftest import MINIMAL_SKILL_MAP, MINIMAL_SCHEDULE


# ---------------------------------------------------------------------------
# 1. write_vault_file protection
# ---------------------------------------------------------------------------

class TestWriteVaultFileProtection:
    def test_no_overwrite_without_generated_marker(self, tmp_path):
        target = tmp_path / "test.md"
        target.write_text("---\ntitle: my note\n---\nHand-written content\n", encoding="utf-8")
        original = target.read_text(encoding="utf-8")

        write_vault_file(target, "---\ngenerated: true\n---\nNew content\n", force=False)

        assert target.read_text(encoding="utf-8") == original

    def test_overwrite_with_force(self, tmp_path):
        target = tmp_path / "test.md"
        target.write_text("---\ntitle: my note\n---\nHand-written content\n", encoding="utf-8")
        new_content = "---\ngenerated: true\n---\nForced content\n"

        write_vault_file(target, new_content, force=True)

        assert target.read_text(encoding="utf-8") == new_content


# ---------------------------------------------------------------------------
# 2. write_vault_file creates new files
# ---------------------------------------------------------------------------

class TestWriteVaultFileCreates:
    def test_creates_new_file_and_parents(self, tmp_path):
        target = tmp_path / "sub" / "dir" / "note.md"
        content = "---\ngenerated: true\n---\nContent\n"

        write_vault_file(target, content)

        assert target.exists()
        assert target.read_text(encoding="utf-8") == content


# ---------------------------------------------------------------------------
# 3. update_frontmatter_in_file
# ---------------------------------------------------------------------------

class TestUpdateFrontmatter:
    def test_updates_fields(self, tmp_path):
        target = tmp_path / "note.md"
        target.write_text(
            "---\ngenerated: true\nstatus: unseen\ntags: [grammar]\n---\nBody text\n",
            encoding="utf-8",
        )

        result = update_frontmatter_in_file(target, {"status": "practicing"})

        assert result is True
        content = target.read_text(encoding="utf-8")
        assert "status: practicing" in content
        # Body should be preserved
        assert "Body text" in content

    def test_skips_without_generated_marker(self, tmp_path):
        target = tmp_path / "note.md"
        target.write_text("---\ntitle: hand-edited\n---\nBody\n", encoding="utf-8")

        result = update_frontmatter_in_file(target, {"status": "practicing"})

        assert result is False

    def test_skips_nonexistent(self, tmp_path):
        result = update_frontmatter_in_file(tmp_path / "nope.md", {"status": "x"})
        assert result is False


# ---------------------------------------------------------------------------
# 4. yaml_frontmatter serialization
# ---------------------------------------------------------------------------

class TestYamlFrontmatter:
    def test_none_becomes_null(self):
        assert _yaml_value(None) == "null"

    def test_bool_true(self):
        assert _yaml_value(True) == "true"

    def test_bool_false(self):
        assert _yaml_value(False) == "false"

    def test_empty_list(self):
        assert _yaml_value([]) == "[]"

    def test_list_with_strings(self):
        result = _yaml_value(["a", "b"])
        assert result == '["a", "b"]'

    def test_string_with_colon_gets_quoted(self):
        result = _yaml_value("key: value")
        assert result == '"key: value"'

    def test_plain_string_unquoted(self):
        assert _yaml_value("hello") == "hello"

    def test_full_frontmatter_structure(self):
        fm = yaml_frontmatter({"generated": True, "title": "Test", "tags": ["a", "b"]})
        assert fm.startswith("---")
        assert fm.endswith("---")
        assert "generated: true" in fm
        assert "title: Test" in fm


# ---------------------------------------------------------------------------
# 5. concept_id_to_title
# ---------------------------------------------------------------------------

class TestConceptIdToTitle:
    def test_standard_concept(self):
        assert concept_id_to_title("A-01-present-regular") == "Present Regular"

    def test_communication_repair(self):
        assert concept_id_to_title("A-00-communication-repair") == "Communication Repair"

    def test_multi_word(self):
        assert concept_id_to_title("B-05-preterite-vs-imperfect") == "Preterite Vs Imperfect"


# ---------------------------------------------------------------------------
# 6. run_full file count
# ---------------------------------------------------------------------------

class TestRunFullFileCount:
    """Verify run_full generates the expected number of vault files.

    Uses a synthetic skill-map fixture so the test is self-contained and
    does not break when the real state/skill-map.yaml changes.
    """

    SYNTHETIC_SKILL_MAP = {
        "schema_version": 1,
        "grammar": {
            "A-01-present-regular": {
                "status": "unseen", "introduced_date": None,
                "last_practiced": None, "practice_count": 0,
                "error_rate_drills": None, "error_rate_production": None,
                "error_trend": None, "performance_scaffolded": None,
                "performance_unscaffolded": None,
                "integration_tested_with": [], "prerequisites": [], "notes": "",
            },
            "A-02-ser-vs-estar": {
                "status": "practicing", "introduced_date": "2026-04-01",
                "last_practiced": "2026-04-09", "practice_count": 3,
                "error_rate_drills": 0.15, "error_rate_production": 0.20,
                "error_trend": "improving", "performance_scaffolded": "competent",
                "performance_unscaffolded": "struggling",
                "integration_tested_with": [], "prerequisites": ["A-01-present-regular"], "notes": "",
            },
            "B-01-preterite-regular": {
                "status": "unseen", "introduced_date": None,
                "last_practiced": None, "practice_count": 0,
                "error_rate_drills": None, "error_rate_production": None,
                "error_trend": None, "performance_scaffolded": None,
                "performance_unscaffolded": None,
                "integration_tested_with": [], "prerequisites": ["A-01-present-regular"], "notes": "",
            },
        },
        "vocabulary": {
            "tier1-greetings-introductions": {
                "status": "unseen", "words_total": 30, "words_introduced": 0,
                "passive_known": 0, "active_known": 0,
                "weak_production": [], "weak_recognition": [],
                "last_practiced": None,
                "error_tracking": {"error_rate_production": 0.0, "common_errors": []},
            },
            "tier2-food-drink": {
                "status": "unseen", "words_total": 25, "words_introduced": 0,
                "passive_known": 0, "active_known": 0,
                "weak_production": [], "weak_recognition": [],
                "last_practiced": None,
                "error_tracking": {"error_rate_production": 0.0, "common_errors": []},
            },
        },
        "pronunciation": {
            "vowel-sounds": {
                "status": "unseen", "last_practiced": None, "external_feedback": "",
            },
        },
        "cultural_awareness": {
            "politeness_formulas": {
                "status": "unseen", "introduced_at_phase": "B",
                "assessed_through": "", "signs_of_acquisition": "",
            },
            "regional_awareness": {
                "status": "unseen", "introduced_at_phase": "B",
                "assessed_through": "", "signs_of_acquisition": "",
            },
        },
        "receptive_skills": {
            "listening": {
                "current_level": "L1", "hours_at_level": 0,
                "hours_total": 0, "comprehension_quality": None,
            },
            "reading": {
                "current_level": "R1", "hours_at_level": 0,
                "hours_total": 0, "comprehension_quality": None, "lookup_frequency": None,
            },
        },
    }

    # 3 grammar + 2 vocab + 1 pronunciation + 2 cultural = 8 dynamic
    # 9 static: Home, Roadmap, Grammar Progress, Vocab Progress,
    #           Weekly Reports, Milestones, Daily Note template,
    #           Journal template, Getting Started
    EXPECTED_GRAMMAR = 3
    EXPECTED_VOCAB = 2
    EXPECTED_PRONUNCIATION = 1
    EXPECTED_CULTURAL = 2
    EXPECTED_STATIC = 9
    EXPECTED_TOTAL = (EXPECTED_GRAMMAR + EXPECTED_VOCAB
                      + EXPECTED_PRONUNCIATION + EXPECTED_CULTURAL
                      + EXPECTED_STATIC)  # 17

    def test_generates_expected_file_count(self, tmp_path, monkeypatch):
        """run_full with synthetic skill-map generates the correct number of files."""
        skill_map = copy.deepcopy(self.SYNTHETIC_SKILL_MAP)
        schedule = copy.deepcopy(MINIMAL_SCHEDULE)

        monkeypatch.setattr(gv, "VAULT_DIR", tmp_path / "vault")

        run_full(skill_map, schedule)

        all_files = list((tmp_path / "vault").rglob("*.md"))

        assert len(all_files) == self.EXPECTED_TOTAL, (
            f"Expected {self.EXPECTED_TOTAL} files "
            f"({self.EXPECTED_GRAMMAR}g + {self.EXPECTED_VOCAB}v "
            f"+ {self.EXPECTED_PRONUNCIATION}p + {self.EXPECTED_CULTURAL}c "
            f"+ {self.EXPECTED_STATIC}s), got {len(all_files)}"
        )

    def test_file_categories_match(self, tmp_path, monkeypatch):
        """Verify each category produces the right number of files."""
        skill_map = copy.deepcopy(self.SYNTHETIC_SKILL_MAP)
        schedule = copy.deepcopy(MINIMAL_SCHEDULE)
        vault = tmp_path / "vault"
        monkeypatch.setattr(gv, "VAULT_DIR", vault)

        run_full(skill_map, schedule)

        grammar_files = list((vault / "Grammar").rglob("*.md")) if (vault / "Grammar").exists() else []
        vocab_files = list((vault / "Vocabulary").rglob("*.md")) if (vault / "Vocabulary").exists() else []
        pronunciation_files = list((vault / "Pronunciation").rglob("*.md")) if (vault / "Pronunciation").exists() else []
        cultural_files = list((vault / "Cultural").rglob("*.md")) if (vault / "Cultural").exists() else []

        assert len(grammar_files) == self.EXPECTED_GRAMMAR
        assert len(vocab_files) == self.EXPECTED_VOCAB
        assert len(pronunciation_files) == self.EXPECTED_PRONUNCIATION
        assert len(cultural_files) == self.EXPECTED_CULTURAL


# ---------------------------------------------------------------------------
# 7. run_session frontmatter updates
# ---------------------------------------------------------------------------

class TestRunSessionFrontmatter:
    def test_session_updates_frontmatter(self, tmp_path, monkeypatch):
        """After run_full then run_session with changed data, frontmatter should update."""
        sm = copy.deepcopy(MINIMAL_SKILL_MAP)
        schedule = copy.deepcopy(MINIMAL_SCHEDULE)
        vault = tmp_path / "vault"
        monkeypatch.setattr(gv, "VAULT_DIR", vault)

        # First do a full generation
        run_full(sm, schedule)

        # Now update the skill map
        sm["grammar"]["A-01-present-regular"]["status"] = "practicing"
        sm["grammar"]["A-01-present-regular"]["practice_count"] = 3

        # Monkeypatch SCHEDULE_PATH so run_session can load schedule
        schedule_path = tmp_path / "schedule.yaml"
        with open(schedule_path, "w", encoding="utf-8") as f:
            yaml.dump(schedule, f)
        monkeypatch.setattr(gv, "SCHEDULE_PATH", schedule_path)

        run_session(sm, "2026-04-10")

        # Check the grammar note was updated
        note_path = vault / "Grammar" / "Phase A - Foundation" / "Present Regular.md"
        assert note_path.exists()
        content = note_path.read_text(encoding="utf-8")
        assert "status: practicing" in content
        assert "practice_count: 3" in content
