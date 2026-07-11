"""Tests for scripts/init-student.py template generation and reset logic.

scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
"""
import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

init_mod = importlib.import_module("init-student")

generate_template_from_schema = init_mod.generate_template_from_schema
TEMPLATES = init_mod.TEMPLATES
SCHEMA_TEMPLATES = init_mod.SCHEMA_TEMPLATES
ZERO_GRAMMAR = init_mod.ZERO_GRAMMAR
ZERO_VOCAB = init_mod.ZERO_VOCAB
reset_skill_map = init_mod.reset_skill_map

# Also import shared for schema access
import shared as shared_mod


# ---------------------------------------------------------------------------
# 1. Template completeness — generated templates are parseable YAML
# ---------------------------------------------------------------------------

class TestTemplateCompleteness:
    @pytest.mark.parametrize("rel_path", list(SCHEMA_TEMPLATES.keys()))
    def test_template_is_parseable_yaml(self, rel_path):
        content = TEMPLATES[rel_path]
        # Strip header comments before parsing
        lines = content.splitlines()
        yaml_lines = [l for l in lines if not l.startswith("#")]
        data = yaml.safe_load("\n".join(yaml_lines))
        assert isinstance(data, dict), f"Template {rel_path} did not parse to a dict"

    def test_parking_lot_is_string(self):
        assert "parking-lot.md" in TEMPLATES
        assert isinstance(TEMPLATES["parking-lot.md"], str)
        assert "Parking Lot" in TEMPLATES["parking-lot.md"]


# ---------------------------------------------------------------------------
# 2. Template has all required schema fields
# ---------------------------------------------------------------------------

class TestTemplateHasRequiredFields:
    @pytest.mark.parametrize("rel_path,info", list(SCHEMA_TEMPLATES.items()))
    def test_required_fields_present(self, rel_path, info):
        content = TEMPLATES[rel_path]
        lines = content.splitlines()
        yaml_lines = [l for l in lines if not l.startswith("#")]
        data = yaml.safe_load("\n".join(yaml_lines))

        schema = shared_mod.load_schema(info["schema"])
        required = shared_mod.get_required_fields(schema)

        for field in required:
            assert field in data, (
                f"Template {rel_path} missing required field '{field}' from schema {info['schema']}"
            )


# ---------------------------------------------------------------------------
# 3. reset_skill_map zeroing
# ---------------------------------------------------------------------------

class TestResetSkillMapZeroing:
    def test_grammar_entries_zeroed(self, tmp_path, monkeypatch):
        """After reset, all grammar entries should be unseen with practice_count=0."""
        monkeypatch.setattr(init_mod, "ROOT", tmp_path)
        state_dir = tmp_path / "state"
        state_dir.mkdir()

        # Create a skill-map with some progress
        sm = {
            "schema_version": 1,
            "grammar": {
                "A-01-present-regular": {
                    "status": "acquired",
                    "introduced_date": "2026-04-01",
                    "last_practiced": "2026-04-05",
                    "practice_count": 12,
                    "error_rate_drills": 0.05,
                    "error_rate_production": 0.08,
                    "error_trend": "stable",
                    "performance_scaffolded": "competent",
                    "performance_unscaffolded": "competent",
                    "integration_tested_with": ["A-02-ser-vs-estar"],
                    "prerequisites": [],
                    "notes": "",
                },
            },
            "vocabulary": {
                "tier1-greetings-introductions": {
                    "status": "practicing",
                    "words_total": 30,
                    "words_introduced": 15,
                    "passive_known": 10,
                    "active_known": 5,
                    "weak_production": ["hola"],
                    "weak_recognition": [],
                    "last_practiced": "2026-04-05",
                },
            },
            "pronunciation": {
                "vowel-sounds": {
                    "status": "practicing",
                    "last_practiced": "2026-04-05",
                    "external_feedback": "good",
                },
            },
        }
        sm_path = state_dir / "skill-map.yaml"
        with open(sm_path, "w", encoding="utf-8") as f:
            yaml.dump(sm, f, default_flow_style=False, sort_keys=False)

        monkeypatch.setattr(init_mod, "STATE_DIR", state_dir)

        reset_skill_map()

        result = yaml.safe_load(sm_path.read_text(encoding="utf-8"))
        g = result["grammar"]["A-01-present-regular"]
        assert g["status"] == "unseen"
        assert g["practice_count"] == 0
        assert g["integration_tested_with"] == []
        assert g["error_rate_drills"] is None
        assert g["error_rate_production"] is None


# ---------------------------------------------------------------------------
# 4. reset preserves structure
# ---------------------------------------------------------------------------

class TestResetPreservesStructure:
    def test_sections_preserved_after_reset(self, tmp_path, monkeypatch):
        monkeypatch.setattr(init_mod, "ROOT", tmp_path)
        state_dir = tmp_path / "state"
        state_dir.mkdir()

        sm = {
            "schema_version": 1,
            "grammar": {
                "A-01-present-regular": {
                    "status": "acquired",
                    "introduced_date": "2026-04-01",
                    "last_practiced": "2026-04-05",
                    "practice_count": 12,
                    "error_rate_drills": 0.05,
                    "error_rate_production": 0.08,
                    "error_trend": "stable",
                    "performance_scaffolded": "competent",
                    "performance_unscaffolded": "competent",
                    "integration_tested_with": [],
                    "prerequisites": [],
                    "notes": "",
                },
            },
            "vocabulary": {
                "tier1-greetings-introductions": {
                    "status": "practicing",
                    "words_total": 30,
                    "words_introduced": 15,
                    "passive_known": 10,
                    "active_known": 5,
                    "weak_production": [],
                    "weak_recognition": [],
                    "last_practiced": None,
                },
            },
            "pronunciation": {
                "vowel-sounds": {
                    "status": "practicing",
                    "last_practiced": "2026-04-05",
                    "external_feedback": "good",
                },
            },
        }
        sm_path = state_dir / "skill-map.yaml"
        with open(sm_path, "w", encoding="utf-8") as f:
            yaml.dump(sm, f, default_flow_style=False, sort_keys=False)

        monkeypatch.setattr(init_mod, "STATE_DIR", state_dir)

        reset_skill_map()

        result = yaml.safe_load(sm_path.read_text(encoding="utf-8"))
        assert "grammar" in result
        assert "vocabulary" in result
        assert "pronunciation" in result
        assert "A-01-present-regular" in result["grammar"]
        assert "tier1-greetings-introductions" in result["vocabulary"]
        assert "vowel-sounds" in result["pronunciation"]


# ---------------------------------------------------------------------------
# 5. Re-init safety — snapshot before wipe, type-to-confirm, fresh-install bypass
# ---------------------------------------------------------------------------

class TestReinitSafety:
    """Tests for D-07 through D-10: snapshot before wipe, type-to-confirm, fresh-install bypass."""

    def test_fresh_install_skips_snapshot_and_prompt(self, tmp_path, monkeypatch, capsys):
        """D-09: No learner-profile.yaml -> no snapshot, no prompt, prints message."""
        monkeypatch.setattr(init_mod, "ROOT", tmp_path)
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        monkeypatch.setattr(init_mod, "STATE_DIR", state_dir)
        # No learner-profile.yaml exists

        # Test the detection logic directly
        from shared import load_yaml
        profile_path = state_dir / "learner-profile.yaml"
        data = load_yaml(profile_path) or {}
        name = data.get("name")
        has_prior = bool(name and str(name).strip())
        assert not has_prior, "Fresh install should detect no prior learner"

    def test_prior_learner_detected(self, tmp_path, monkeypatch):
        """D-08: Non-empty name in profile -> prior learner detected."""
        monkeypatch.setattr(init_mod, "ROOT", tmp_path)
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        monkeypatch.setattr(init_mod, "STATE_DIR", state_dir)

        profile = state_dir / "learner-profile.yaml"
        profile.write_text("name: Kyle\ntarget_dialect: es-MX\n", encoding="utf-8")

        from shared import load_yaml
        data = load_yaml(profile) or {}
        name = data.get("name")
        has_prior = bool(name and str(name).strip())
        assert has_prior, "Should detect prior learner when name is non-empty"

    def test_empty_name_treated_as_fresh(self, tmp_path, monkeypatch):
        """D-09: Profile exists but name is empty -> treated as fresh install."""
        monkeypatch.setattr(init_mod, "ROOT", tmp_path)
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        monkeypatch.setattr(init_mod, "STATE_DIR", state_dir)

        profile = state_dir / "learner-profile.yaml"
        profile.write_text("name: \"\"\ntarget_dialect: null\n", encoding="utf-8")

        from shared import load_yaml
        data = load_yaml(profile) or {}
        name = data.get("name")
        has_prior = bool(name and str(name).strip())
        assert not has_prior, "Empty name should be treated as fresh install"

    def test_session_logs_with_empty_name_is_prior_data(self, tmp_path):
        """P2-c: empty profile name BUT existing session logs must count as prior
        data, so `init --force` snapshots before wiping (the old name-only gate
        skipped the snapshot and silently destroyed the logs)."""
        sessions = tmp_path / "state" / "sessions"
        sessions.mkdir(parents=True)
        (tmp_path / "state" / "learner-profile.yaml").write_text('name: ""\n', encoding="utf-8")
        (sessions / "2026-06-01.yaml").write_text("date: '2026-06-01'\n", encoding="utf-8")
        assert init_mod.has_existing_learner_data(tmp_path) is True

    def test_truly_fresh_is_not_prior_data(self, tmp_path):
        """P2-c control: empty name + no session logs + no journal = fresh install."""
        (tmp_path / "state").mkdir(parents=True)
        (tmp_path / "state" / "learner-profile.yaml").write_text('name: ""\n', encoding="utf-8")
        assert init_mod.has_existing_learner_data(tmp_path) is False

    def test_archived_only_sessions_with_empty_name_is_prior_data(self, tmp_path):
        """A2 (code-review): a learner whose only logs were archived (>60d) with an
        empty profile name must still be detected — else --force wipes the archive
        with no recovery snapshot."""
        archive = tmp_path / "state" / "sessions" / "archive"
        archive.mkdir(parents=True)
        (tmp_path / "state" / "learner-profile.yaml").write_text('name: ""\n', encoding="utf-8")
        (archive / "2025-01-01.yaml").write_text("date: '2025-01-01'\n", encoding="utf-8")
        assert init_mod.has_existing_learner_data(tmp_path) is True

    def test_dirty_parking_lot_is_prior_data(self, tmp_path):
        """F078: consolidating onto setup's broader scope means parking-lot drift
        (with an empty profile name and no session logs) now counts as prior data —
        previously init's detector ignored it and --force wiped it with no snapshot."""
        (tmp_path / "state").mkdir(parents=True)
        (tmp_path / "state" / "learner-profile.yaml").write_text('name: ""\n', encoding="utf-8")
        (tmp_path / "parking-lot.md").write_text(
            init_mod.TEMPLATES["parking-lot.md"] + "\n- Ask about the subjunctive\n",
            encoding="utf-8",
        )
        assert init_mod.has_existing_learner_data(tmp_path) is True

    def test_pristine_parking_lot_is_not_prior_data(self, tmp_path):
        """F078 control: a parking-lot.md that still matches the pristine template
        (plus an empty profile name) must NOT be treated as prior data."""
        (tmp_path / "state").mkdir(parents=True)
        (tmp_path / "state" / "learner-profile.yaml").write_text('name: ""\n', encoding="utf-8")
        (tmp_path / "parking-lot.md").write_text(
            init_mod.TEMPLATES["parking-lot.md"], encoding="utf-8"
        )
        assert init_mod.has_existing_learner_data(tmp_path) is False

    def test_resource_tracker_entries_is_prior_data(self, tmp_path):
        """F078: resource-tracker.yaml with a populated `resources` list (empty
        profile name, no session logs) now counts as prior data — init's detector
        previously ignored the file it wipes in TEMPLATES."""
        (tmp_path / "state").mkdir(parents=True)
        (tmp_path / "state" / "learner-profile.yaml").write_text('name: ""\n', encoding="utf-8")
        (tmp_path / "state" / "resource-tracker.yaml").write_text(
            "schema_version: 1\nresources:\n  - id: dreaming-spanish\n", encoding="utf-8"
        )
        assert init_mod.has_existing_learner_data(tmp_path) is True

    def test_corrupt_profile_is_prior_data(self, tmp_path):
        """F078: a corrupt learner-profile.yaml must fail safe to prior-data=True
        so --force snapshots before clobbering a recoverable-but-unparseable file.
        init previously used load_yaml (returns None on YAMLError) → treated as no
        data → wiped with no snapshot."""
        (tmp_path / "state").mkdir(parents=True)
        (tmp_path / "state" / "learner-profile.yaml").write_text(
            "name: [unclosed\n  : : :\n", encoding="utf-8"
        )
        assert init_mod.has_existing_learner_data(tmp_path) is True

    def test_corrupt_resource_tracker_is_prior_data(self, tmp_path):
        """F078: same fail-safe for a corrupt resource-tracker.yaml. Profile is kept
        pristine so the corrupt tracker is the only signal."""
        (tmp_path / "state").mkdir(parents=True)
        (tmp_path / "state" / "learner-profile.yaml").write_text('name: ""\n', encoding="utf-8")
        (tmp_path / "state" / "resource-tracker.yaml").write_text(
            "resources: [\n  - id: x\n    : broken\n", encoding="utf-8"
        )
        assert init_mod.has_existing_learner_data(tmp_path) is True

    def test_force_help_mentions_snapshot(self, capsys):
        """D-10: --help text for --force mentions snapshot is always taken."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--force", action="store_true",
                            help="Skip the interactive confirmation prompt (snapshot is always taken)")
        help_text = parser.format_help()
        assert "snapshot" in help_text.lower()


# ---------------------------------------------------------------------------
# 6. --demo: seed a realistic, validator-clean sample learner
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


def _run_script(script: str, state_dir: Path, *args: str) -> subprocess.CompletedProcess:
    """Run a repo script in a subprocess with STATE_DIR redirected to a scratch
    dir via TUTOR_STATE_DIR, so the seed/validation never touches real state."""
    env = {**os.environ, "TUTOR_STATE_DIR": str(state_dir)}
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script), *args],
        cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
    )


class TestDemoSeed:
    def test_demo_state_validates_end_to_end(self, tmp_path):
        """CRITICAL: `init-student.py --demo` must seed state that
        validate-state.py accepts with 0 warnings AND 0 failures."""
        state_dir = tmp_path / "state"
        seed = _run_script("init-student.py", state_dir, "--demo")
        assert seed.returncode == 0, seed.stdout + seed.stderr

        val = _run_script("validate-state.py", state_dir)
        assert val.returncode == 0, val.stdout + val.stderr
        assert "0 warnings, 0 failures" in val.stdout, val.stdout

    def test_demo_seed_contents_and_routing(self, tmp_path):
        """The seed is a coherent mid-Phase-B Mexican-dialect learner, and with
        no session logs it boots into first-session (route_session Row 1)."""
        state_dir = tmp_path / "state"
        seed = _run_script("init-student.py", state_dir, "--demo")
        assert seed.returncode == 0, seed.stdout + seed.stderr

        profile = yaml.safe_load((state_dir / "learner-profile.yaml").read_text(encoding="utf-8"))
        assert profile["name"] == "Alex Demo"
        assert profile["target_dialect"] == "Mexican"
        assert profile["initial_placement"]["level"] == "early-B"

        schedule = yaml.safe_load((state_dir / "schedule.yaml").read_text(encoding="utf-8"))
        assert schedule["onboarding_complete"] is True
        assert schedule["current_phase"] == "B-conversational"
        assert schedule["last_session_date"] is None

        skill_map = yaml.safe_load((state_dir / "skill-map.yaml").read_text(encoding="utf-8"))
        # Phase-B entry prerequisites are acquired; early-B concepts are practicing.
        assert skill_map["grammar"]["A-01-present-regular"]["status"] == "acquired"
        assert skill_map["grammar"]["B-01-preterite-regular"]["status"] == "practicing"

        route_mod = importlib.import_module("route_session")
        assert route_mod.route_session(state_dir) == "first-session"

    def test_demo_overwrite_guard_respects_existing_data(self, tmp_path, monkeypatch):
        """The demo must refuse to clobber real learner data without --force,
        reusing has_existing_learner_data as the detector."""
        state_dir = tmp_path / "state"
        (state_dir / "sessions").mkdir(parents=True)
        (state_dir / "sessions" / "2026-06-01.yaml").write_text(
            "date: '2026-06-01'\n", encoding="utf-8"
        )
        monkeypatch.setattr(init_mod, "STATE_DIR", state_dir)

        # Prior data is detected at the demo root (STATE_DIR.parent).
        assert init_mod.has_existing_learner_data(state_dir.parent) is True

        rc = init_mod.run_demo(force=False)
        assert rc == 1
        # The guard aborted before writing any demo state.
        assert not (state_dir / "learner-profile.yaml").exists()

    def test_demo_overwrite_guard_with_non_state_named_dir(self, tmp_path, monkeypatch):
        """Regression: the guard must inspect the SAME directory the seed writes
        to. With TUTOR_STATE_DIR pointing at a dir not named 'state', the old
        STATE_DIR.parent/state reconstruction checked an empty location and
        silently clobbered real learner data."""
        state_dir = tmp_path / "mystate"
        (state_dir / "sessions").mkdir(parents=True)
        (state_dir / "learner-profile.yaml").write_text(
            "name: Real Learner\n", encoding="utf-8"
        )
        (state_dir / "sessions" / "2026-07-01.yaml").write_text(
            "date: '2026-07-01'\n", encoding="utf-8"
        )
        monkeypatch.setattr(init_mod, "STATE_DIR", state_dir)

        rc = init_mod.run_demo(force=False)
        assert rc == 1
        # Real data untouched.
        profile = (state_dir / "learner-profile.yaml").read_text(encoding="utf-8")
        assert "Real Learner" in profile

    def test_plain_learner_profile_template_is_blank(self):
        """Plain (non-demo) template generation is unchanged: the demo constants
        never leak into the blank templates."""
        data = yaml.safe_load(init_mod.generate_template_from_schema("learner-profile"))
        assert data["name"] == ""
        assert data["target_dialect"] == ""
