"""Tests for scripts/build-manifest.py and the generated curriculum/manifest.yaml.

The manifest is the single machine-readable index of every teachable concept — the curriculum
package index a port bundles as versioned content (docs/engine-api.md). These tests pin down:

  (a) the committed manifest parses and every ``path`` points at a real file;
  (b) manifest entries and on-disk curriculum files are in exact 1:1 correspondence (drift);
  (c) every ``prerequisites`` id resolves to another concept and every ``l1_interference`` id
      resolves to a pattern in curriculum/l1-interference.yaml;
  (d) regeneration is idempotent — a fresh build is byte-identical to the committed file
      (also proving the committed file is not stale);
  (e) grammar and cultural ids match state/skill-map.template.yaml concept keys exactly.

scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
"""
import importlib
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

build_manifest = importlib.import_module("build-manifest")

REPO_ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = REPO_ROOT / "curriculum"
MANIFEST_PATH = CURRICULUM / "manifest.yaml"
SCRIPT = REPO_ROOT / "scripts" / "build-manifest.py"
TEMPLATE_PATH = REPO_ROOT / "state" / "skill-map.template.yaml"

PHASE_DIRS = {"A": "A-foundation", "B": "B-conversational",
              "C": "C-intermediate", "D": "D-advanced"}
TIER_DIRS = {"1": "tier1-survival", "2": "tier2-daily-life",
             "3": "tier3-social", "4": "tier4-abstract"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))


def _concepts() -> list[dict]:
    return _load_manifest()["concepts"]


def _by_category(category: str) -> list[dict]:
    return [c for c in _concepts() if c["category"] == category]


def _ids() -> set[str]:
    return {c["id"] for c in _concepts()}


def _expected_grammar_ids() -> set[str]:
    ids = set()
    for phase, dirname in PHASE_DIRS.items():
        for md in (CURRICULUM / "grammar" / dirname).glob("*.md"):
            ids.add(f"{phase}-{md.stem}")
    return ids


def _expected_vocab_ids() -> set[str]:
    ids = set()
    for tier, dirname in TIER_DIRS.items():
        for md in (CURRICULUM / "vocabulary" / dirname).glob("*.md"):
            ids.add(f"vocab-t{tier}-{md.stem}")
    return ids


def _expected_pron_ids() -> set[str]:
    return {md.stem for md in (CURRICULUM / "pronunciation").glob("*.md")}


def _expected_cultural_ids() -> set[str]:
    return {md.stem.replace("-", "_") for md in (CURRICULUM / "cultural").glob("*.md")}


# ---------------------------------------------------------------------------
# (a) Manifest parses; every path exists
# ---------------------------------------------------------------------------

class TestManifestStructure:
    def test_manifest_parses(self):
        data = _load_manifest()
        assert data["schema_version"] == 1
        assert isinstance(data["concepts"], list) and data["concepts"]

    def test_required_fields_present(self):
        for c in _concepts():
            for field in ("id", "category", "title", "path",
                          "prerequisites", "l1_interference"):
                assert field in c, f"{c.get('id')} missing '{field}'"
            assert ("phase" in c) or ("tier" in c), \
                f"{c['id']} has neither phase nor tier"

    def test_every_path_exists(self):
        for c in _concepts():
            p = REPO_ROOT / c["path"]
            assert p.is_file(), f"{c['id']} -> missing file {c['path']}"

    def test_ids_unique(self):
        ids = [c["id"] for c in _concepts()]
        assert len(ids) == len(set(ids)), "duplicate concept ids in manifest"

    def test_categories_are_known(self):
        assert {c["category"] for c in _concepts()} == {
            "grammar", "vocabulary", "pronunciation", "cultural"}


# ---------------------------------------------------------------------------
# (b) Drift: manifest entries <-> on-disk files are 1:1
# ---------------------------------------------------------------------------

class TestDrift:
    def test_grammar_files_and_entries_match(self):
        manifest_ids = {c["id"] for c in _by_category("grammar")}
        disk_ids = _expected_grammar_ids()
        assert manifest_ids == disk_ids, (
            f"grammar drift — only in manifest: {manifest_ids - disk_ids}; "
            f"only on disk: {disk_ids - manifest_ids}")

    def test_vocabulary_files_and_entries_match(self):
        manifest_ids = {c["id"] for c in _by_category("vocabulary")}
        assert manifest_ids == _expected_vocab_ids()

    def test_pronunciation_files_and_entries_match(self):
        manifest_ids = {c["id"] for c in _by_category("pronunciation")}
        assert manifest_ids == _expected_pron_ids()

    def test_cultural_files_and_entries_match(self):
        manifest_ids = {c["id"] for c in _by_category("cultural")}
        assert manifest_ids == _expected_cultural_ids()

    def test_paths_map_back_to_declared_category_dir(self):
        expected_dir = {
            "grammar": "curriculum/grammar/",
            "vocabulary": "curriculum/vocabulary/",
            "pronunciation": "curriculum/pronunciation/",
            "cultural": "curriculum/cultural/",
        }
        for c in _concepts():
            assert c["path"].startswith(expected_dir[c["category"]]), \
                f"{c['id']} path {c['path']} not under {c['category']} dir"


# ---------------------------------------------------------------------------
# (c) Every prerequisite id and l1_interference id resolves
# ---------------------------------------------------------------------------

class TestReferentialIntegrity:
    def test_prerequisites_resolve(self):
        ids = _ids()
        for c in _concepts():
            for pre in c["prerequisites"]:
                assert pre in ids, f"{c['id']} prereq '{pre}' resolves to no concept"

    def test_only_grammar_carries_prerequisites(self):
        # Prerequisites are a grammar-only field by spec; others must be empty.
        for c in _concepts():
            if c["category"] != "grammar":
                assert c["prerequisites"] == [], \
                    f"{c['id']} ({c['category']}) unexpectedly has prerequisites"
            # every declared grammar prereq points at a grammar concept
            for pre in c["prerequisites"]:
                assert pre.startswith(("A-", "B-", "C-", "D-"))

    def test_l1_interference_ids_resolve(self):
        l1 = yaml.safe_load((CURRICULUM / "l1-interference.yaml").read_text(encoding="utf-8"))
        pattern_ids = {p["id"] for p in l1["interference_patterns"]}
        for c in _concepts():
            for pid in c["l1_interference"]:
                assert pid in pattern_ids, \
                    f"{c['id']} l1_interference '{pid}' resolves to no pattern"

    def test_grammar_preempts_are_all_captured(self):
        """Every l1 pattern whose preempt_at is a grammar concept id must appear on that
        concept — the manifest is the join table the tutor/port reads instead of re-parsing
        l1-interference.yaml's preempt_at strings."""
        l1 = yaml.safe_load((CURRICULUM / "l1-interference.yaml").read_text(encoding="utf-8"))
        grammar_ids = {c["id"] for c in _by_category("grammar")}
        by_id = {c["id"]: c for c in _concepts()}
        for p in l1["interference_patterns"]:
            target = p.get("preempt_at")
            if target in grammar_ids:
                assert p["id"] in by_id[target]["l1_interference"], (
                    f"pattern {p['id']} preempts {target} but is absent from its "
                    "l1_interference list")

    def test_l1_interference_lists_sorted(self):
        for c in _concepts():
            assert c["l1_interference"] == sorted(c["l1_interference"]), \
                f"{c['id']} l1_interference not sorted (non-deterministic)"


# ---------------------------------------------------------------------------
# (d) Regeneration is idempotent / committed file is fresh
# ---------------------------------------------------------------------------

class TestIdempotency:
    def test_rebuild_is_byte_identical(self, tmp_path):
        out = tmp_path / "manifest.regen.yaml"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "-o", str(out)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        regenerated = out.read_bytes()
        committed = MANIFEST_PATH.read_bytes()
        assert regenerated == committed, (
            "regenerated manifest differs from committed curriculum/manifest.yaml — "
            "either build-manifest.py is non-deterministic or the committed file is stale "
            "(run: .venv/bin/python scripts/build-manifest.py)")

    def test_check_mode_passes_on_committed_file(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, (
            "build-manifest.py --check reports the committed manifest is stale:\n"
            + result.stdout + result.stderr)

    def test_render_matches_committed(self):
        # In-process determinism: render() over a fresh build equals the committed bytes.
        assert build_manifest.render(build_manifest.build_manifest()) == \
            MANIFEST_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# (e) Grammar + cultural ids match the skill-map template concept keys
# ---------------------------------------------------------------------------

class TestSkillMapTemplateAlignment:
    def test_grammar_ids_match_template(self):
        tmpl = yaml.safe_load(TEMPLATE_PATH.read_text(encoding="utf-8"))
        template_ids = set(tmpl["grammar"].keys())
        manifest_ids = {c["id"] for c in _by_category("grammar")}
        assert manifest_ids == template_ids, (
            f"grammar id mismatch vs skill-map.template.yaml — "
            f"only in manifest: {manifest_ids - template_ids}; "
            f"only in template: {template_ids - manifest_ids}")

    def test_cultural_ids_match_template(self):
        tmpl = yaml.safe_load(TEMPLATE_PATH.read_text(encoding="utf-8"))
        template_ids = set(tmpl["cultural_awareness"].keys())
        manifest_ids = {c["id"] for c in _by_category("cultural")}
        assert manifest_ids == template_ids, (
            f"cultural id mismatch vs skill-map.template.yaml — "
            f"only in manifest: {manifest_ids - template_ids}; "
            f"only in template: {template_ids - manifest_ids}")

    def test_cultural_phase_matches_template_introduced_at_phase(self):
        tmpl = yaml.safe_load(TEMPLATE_PATH.read_text(encoding="utf-8"))
        ca = tmpl["cultural_awareness"]
        for c in _by_category("cultural"):
            assert c["phase"] == ca[c["id"]]["introduced_at_phase"], (
                f"{c['id']} phase {c['phase']} != template "
                f"introduced_at_phase {ca[c['id']]['introduced_at_phase']}")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
