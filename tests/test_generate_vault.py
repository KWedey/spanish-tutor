"""Tests for scripts/generate-vault.py vault generation functions."""
import copy
import importlib
import re
import sys
from pathlib import Path

import pytest
import yaml

# scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
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

    def test_full_preserves_appended_weekly_reports_and_milestones(self, tmp_path, monkeypatch):
        """H4: a second run_full must NOT clobber history appended to the
        Weekly Reports / Milestones append-targets (they carry generated: false
        and are written force=False)."""
        skill_map = copy.deepcopy(self.SYNTHETIC_SKILL_MAP)
        schedule = copy.deepcopy(MINIMAL_SCHEDULE)
        monkeypatch.setattr(gv, "VAULT_DIR", tmp_path / "vault")

        run_full(skill_map, schedule)  # first run creates placeholders
        wr = tmp_path / "vault" / "Progress" / "Weekly Reports.md"
        ms = tmp_path / "vault" / "Progress" / "Milestones.md"
        assert wr.exists() and ms.exists()
        # neither should advertise itself as auto-generated
        assert not file_has_generated_marker(wr)
        assert not file_has_generated_marker(ms)

        # tutor appends real history
        wr.write_text(wr.read_text() + "\n## Week 2026-W23\nReal weekly entry.\n", encoding="utf-8")
        ms.write_text(ms.read_text() + "\n## 2026-06-03 — first 100 words\nMilestone.\n", encoding="utf-8")

        run_full(skill_map, schedule)  # second run must preserve

        assert "Real weekly entry." in wr.read_text(), "H4: weekly history wiped by --full"
        assert "first 100 words" in ms.read_text(), "H4: milestone history wiped by --full"

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
# 6b. run_full with all-None receptive data — H2 regression guard
# ---------------------------------------------------------------------------

class TestRunFullNoneFormatting:
    """The H2 bug shipped because the SYNTHETIC_SKILL_MAP fixture used
    populated receptive levels (L1/R1), so the None path was never exercised.
    This test builds a skill map with every receptive field set to None and
    asserts no literal 'None' string appears in Home.md or Roadmap.md — the
    two files that interpolate receptive values into their body text.
    """

    @staticmethod
    def _none_receptive_skill_map():
        sm = copy.deepcopy(TestRunFullFileCount.SYNTHETIC_SKILL_MAP)
        sm["receptive_skills"] = {
            "listening": {
                "current_level": None,
                "hours_at_level": None,
                "hours_total": None,
                "comprehension_quality": None,
            },
            "reading": {
                "current_level": None,
                "hours_at_level": None,
                "hours_total": None,
                "comprehension_quality": None,
                "lookup_frequency": None,
            },
        }
        return sm

    def test_no_literal_none_in_home(self, tmp_path, monkeypatch):
        skill_map = self._none_receptive_skill_map()
        schedule = copy.deepcopy(MINIMAL_SCHEDULE)
        vault = tmp_path / "vault"
        monkeypatch.setattr(gv, "VAULT_DIR", vault)

        run_full(skill_map, schedule)

        home_content = (vault / "Home.md").read_text(encoding="utf-8")
        matches = re.findall(r"\bNone\b", home_content)
        assert matches == [], (
            f"Home.md contains literal 'None' {len(matches)} time(s) — "
            f"the H2 formatting bug has regressed.\n--- Home.md ---\n{home_content}"
        )

    def test_no_literal_none_in_roadmap(self, tmp_path, monkeypatch):
        skill_map = self._none_receptive_skill_map()
        schedule = copy.deepcopy(MINIMAL_SCHEDULE)
        vault = tmp_path / "vault"
        monkeypatch.setattr(gv, "VAULT_DIR", vault)

        run_full(skill_map, schedule)

        roadmap_content = (vault / "Roadmap.md").read_text(encoding="utf-8")
        matches = re.findall(r"\bNone\b", roadmap_content)
        assert matches == [], (
            f"Roadmap.md contains literal 'None' {len(matches)} time(s) — "
            f"the H2 formatting bug has regressed.\n--- Roadmap.md ---\n{roadmap_content}"
        )


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


# ---------------------------------------------------------------------------
# 7. Marker protection under run_full (P2-a) + frontmatter robustness (P2-n/o)
# ---------------------------------------------------------------------------

class TestRunFullMarkerProtection:
    def test_full_protects_marker_stripped_concept_note(self, tmp_path, monkeypatch):
        """P2-a: run_full must NOT clobber a generated concept note whose marker the
        learner removed to keep a hand-edit (concept notes are now written force=False)."""
        skill_map = copy.deepcopy(TestRunFullFileCount.SYNTHETIC_SKILL_MAP)
        schedule = copy.deepcopy(MINIMAL_SCHEDULE)
        monkeypatch.setattr(gv, "VAULT_DIR", tmp_path / "vault")

        run_full(skill_map, schedule)
        note, _ = gv.generate_grammar_note(
            "A-01-present-regular", skill_map["grammar"]["A-01-present-regular"])
        assert note.exists() and file_has_generated_marker(note)

        note.write_text("---\ntitle: mine\n---\nMy mnemonic — keep this!\n", encoding="utf-8")
        run_full(skill_map, schedule)
        assert "My mnemonic — keep this!" in note.read_text(encoding="utf-8"), (
            "P2-a: run_full clobbered a marker-stripped hand-edited concept note"
        )

    def test_full_still_regenerates_marked_concept_note(self, tmp_path, monkeypatch):
        """P2-a control: a note still carrying generated:true IS rewritten on the next
        run_full, so dashboards/notes stay current."""
        skill_map = copy.deepcopy(TestRunFullFileCount.SYNTHETIC_SKILL_MAP)
        schedule = copy.deepcopy(MINIMAL_SCHEDULE)
        monkeypatch.setattr(gv, "VAULT_DIR", tmp_path / "vault")

        run_full(skill_map, schedule)
        note, _ = gv.generate_grammar_note(
            "A-01-present-regular", skill_map["grammar"]["A-01-present-regular"])
        note.write_text("---\ngenerated: true\n---\nSTALE BODY\n", encoding="utf-8")
        run_full(skill_map, schedule)
        assert "STALE BODY" not in note.read_text(encoding="utf-8"), (
            "P2-a control: a marker-bearing note must be regenerated, not preserved"
        )


class TestFrontmatterRobustness:
    def test_malformed_source_frontmatter_falls_back_to_raw(self):
        """P2-n: split_frontmatter must not raise on malformed YAML; a source file with
        a bad frontmatter block falls back to raw content instead of aborting run_full."""
        bad = "---\nkey: [unclosed\n---\nReal body content\n"
        fm, _ = gv.split_frontmatter(bad)   # must not raise
        assert fm is None
        assert "Real body content" in gv.strip_source_frontmatter(bad)

    def test_marker_recognized_past_1024_bytes(self, tmp_path):
        """P2-o: a generated note whose frontmatter closing '---' sits beyond 1024
        bytes must still be recognized as generated (not misread as hand-edited)."""
        filler = "\n".join(f"alias{i}: value{i}" for i in range(120))  # push close past 1024B
        note = tmp_path / "big.md"
        note.write_text(f"---\ngenerated: true\n{filler}\n---\nbody\n", encoding="utf-8")
        assert gv.file_has_generated_marker(note) is True


class TestNullReceptiveGuard:
    def test_null_receptive_entries_do_not_crash(self, tmp_path, monkeypatch):
        """A1 (code-review): receptive_skills present with null listening/reading
        entries (plausible pre-session-5 state) must not crash generate_home /
        generate_roadmap during run_full."""
        skill_map = copy.deepcopy(TestRunFullFileCount.SYNTHETIC_SKILL_MAP)
        skill_map["receptive_skills"] = {"listening": None, "reading": None}
        schedule = copy.deepcopy(MINIMAL_SCHEDULE)
        monkeypatch.setattr(gv, "VAULT_DIR", tmp_path / "vault")
        run_full(skill_map, schedule)  # must not raise AttributeError
        assert (tmp_path / "vault" / "Home.md").exists()
        assert (tmp_path / "vault" / "Roadmap.md").exists()


# ---------------------------------------------------------------------------
# 8. Corrupt-but-present state fails loud (F037)
# ---------------------------------------------------------------------------

class TestCorruptStateFailsLoud:
    """F037: main() and run_session must fail loud (clean stderr + nonzero exit)
    when a present-but-corrupt skill-map/schedule makes the loader raise, instead
    of letting a later None.get(...) surface as an AttributeError traceback.
    Covers all three load sites: main() skill-map, main() schedule, run_session
    schedule (the path post-session.sh --session actually executes)."""

    CORRUPT_YAML = "grammar: [unclosed\n  bad: :\n"

    def test_main_exits_on_corrupt_skill_map(self, tmp_path, monkeypatch, capsys):
        skill_map = tmp_path / "skill-map.yaml"
        skill_map.write_text(self.CORRUPT_YAML, encoding="utf-8")
        monkeypatch.setattr(gv, "SKILL_MAP_PATH", skill_map)
        monkeypatch.setattr(gv, "SCHEDULE_PATH", tmp_path / "schedule.yaml")
        monkeypatch.setattr(gv, "VAULT_DIR", tmp_path / "vault")
        monkeypatch.setattr(sys, "argv", ["generate-vault.py", "--full"])

        with pytest.raises(SystemExit) as exc:
            gv.main()

        assert exc.value.code == 1
        err = capsys.readouterr().err
        assert err.startswith("Error:")
        assert str(skill_map) in err  # message points at the offending file

    def test_main_exits_on_corrupt_schedule(self, tmp_path, monkeypatch, capsys):
        skill_map = tmp_path / "skill-map.yaml"
        with open(skill_map, "w", encoding="utf-8") as f:
            yaml.dump(copy.deepcopy(MINIMAL_SKILL_MAP), f)
        schedule = tmp_path / "schedule.yaml"
        schedule.write_text(self.CORRUPT_YAML, encoding="utf-8")
        monkeypatch.setattr(gv, "SKILL_MAP_PATH", skill_map)
        monkeypatch.setattr(gv, "SCHEDULE_PATH", schedule)
        monkeypatch.setattr(gv, "VAULT_DIR", tmp_path / "vault")
        monkeypatch.setattr(sys, "argv", ["generate-vault.py", "--full"])

        with pytest.raises(SystemExit) as exc:
            gv.main()

        assert exc.value.code == 1
        err = capsys.readouterr().err
        assert err.startswith("Error:")
        assert str(schedule) in err

    def test_run_session_exits_on_corrupt_schedule(self, tmp_path, monkeypatch, capsys):
        """The --session route (post-session.sh) reloads schedule inside
        run_session; a corrupt schedule there must also fail loud."""
        schedule = tmp_path / "schedule.yaml"
        schedule.write_text(self.CORRUPT_YAML, encoding="utf-8")
        monkeypatch.setattr(gv, "SCHEDULE_PATH", schedule)
        monkeypatch.setattr(gv, "VAULT_DIR", tmp_path / "vault")

        with pytest.raises(SystemExit) as exc:
            gv.run_session(copy.deepcopy(MINIMAL_SKILL_MAP), "2026-04-10")

        assert exc.value.code == 1
        assert str(schedule) in capsys.readouterr().err
