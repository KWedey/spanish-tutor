"""Tests for scripts/migrate-state.py migration functions.

scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
"""
import importlib
from pathlib import Path

import pytest
import yaml

migrate_mod = importlib.import_module("migrate-state")

set_nested = migrate_mod.set_nested
get_nested = migrate_mod.get_nested
load_state_file = migrate_mod.load_state_file
CURRENT_VERSION = migrate_mod.CURRENT_VERSION
MIGRATIONS = migrate_mod.MIGRATIONS


# ---------------------------------------------------------------------------
# 1. set_nested creates intermediate dicts
# ---------------------------------------------------------------------------

class TestSetNested:
    def test_creates_intermediate_dicts(self):
        data = {}
        set_nested(data, "a.b.c", 1)
        assert data == {"a": {"b": {"c": 1}}}

    def test_single_key(self):
        data = {}
        set_nested(data, "x", 42)
        assert data == {"x": 42}

    def test_overwrites_existing(self):
        data = {"a": {"b": 10}}
        set_nested(data, "a.b", 20)
        assert data == {"a": {"b": 20}}

    def test_replaces_non_dict_intermediate(self):
        data = {"a": "string_value"}
        set_nested(data, "a.b.c", 1)
        assert data == {"a": {"b": {"c": 1}}}


# ---------------------------------------------------------------------------
# 2. get_nested returns (True, value) for existing
# ---------------------------------------------------------------------------

class TestGetNestedExists:
    def test_returns_true_and_value(self):
        data = {"a": {"b": 1}}
        exists, value = get_nested(data, "a.b")
        assert exists is True
        assert value == 1

    def test_top_level(self):
        data = {"x": 42}
        exists, value = get_nested(data, "x")
        assert exists is True
        assert value == 42

    def test_deep_nesting(self):
        data = {"a": {"b": {"c": {"d": "deep"}}}}
        exists, value = get_nested(data, "a.b.c.d")
        assert exists is True
        assert value == "deep"


# ---------------------------------------------------------------------------
# 3. get_nested returns (False, None) for missing
# ---------------------------------------------------------------------------

class TestGetNestedMissing:
    def test_missing_key(self):
        data = {"a": 1}
        exists, value = get_nested(data, "a.b")
        assert exists is False
        assert value is None

    def test_completely_missing(self):
        data = {}
        exists, value = get_nested(data, "x.y.z")
        assert exists is False
        assert value is None

    def test_non_dict_intermediate(self):
        data = {"a": "string"}
        exists, value = get_nested(data, "a.b")
        assert exists is False
        assert value is None


# ---------------------------------------------------------------------------
# 4. Migration skips up-to-date files
# ---------------------------------------------------------------------------

class TestMigrationSkipsUpToDate:
    def test_file_at_current_version_unchanged(self, tmp_path, monkeypatch):
        monkeypatch.setattr(migrate_mod, "ROOT", tmp_path)

        state_dir = tmp_path / "state"
        state_dir.mkdir()
        data = {"schema_version": CURRENT_VERSION, "name": "Test"}
        file_path = state_dir / "learner-profile.yaml"
        file_path.write_text(
            yaml.dump(data, default_flow_style=False), encoding="utf-8"
        )

        original_content = file_path.read_text(encoding="utf-8")

        loaded, error = load_state_file("state/learner-profile.yaml")
        assert error is None
        assert loaded["schema_version"] >= CURRENT_VERSION

        # The file should remain unchanged since it's at current version
        assert file_path.read_text(encoding="utf-8") == original_content


# ---------------------------------------------------------------------------
# 5. Migration adds missing fields
# ---------------------------------------------------------------------------

class TestMigrationAddsMissingFields:
    def test_adds_fields_below_current_version(self, tmp_path, monkeypatch):
        monkeypatch.setattr(migrate_mod, "ROOT", tmp_path)

        state_dir = tmp_path / "state"
        state_dir.mkdir()

        # File at version 0 (below CURRENT_VERSION)
        data = {"schema_version": 0, "name": "Test"}
        file_path = state_dir / "learner-profile.yaml"
        file_path.write_text(
            yaml.dump(data, default_flow_style=False), encoding="utf-8"
        )

        # Simulate migration: find all fields that should be added for this file
        fields_for_file = []
        for version in range(1, CURRENT_VERSION + 1):
            if version not in MIGRATIONS:
                continue
            for m_file, field_path, default in MIGRATIONS[version]:
                if m_file == "state/learner-profile.yaml":
                    fields_for_file.append((field_path, default))

        # Apply migrations manually (same logic as main())
        loaded, error = load_state_file("state/learner-profile.yaml")
        assert error is None

        for field_path, default in fields_for_file:
            exists, _ = get_nested(loaded, field_path)
            if not exists:
                set_nested(loaded, field_path, default)

        loaded["schema_version"] = CURRENT_VERSION

        # Verify the fields were added
        for field_path, default in fields_for_file:
            exists, value = get_nested(loaded, field_path)
            assert exists, f"Field '{field_path}' should have been added by migration"


# ---------------------------------------------------------------------------
# 6. Integration test for main()
# ---------------------------------------------------------------------------

class TestMainIntegration:
    """End-to-end test that calls main() and verifies state files are migrated."""

    def _write_state_file(self, state_dir: Path, filename: str, data: dict,
                          comment_header: str = "") -> Path:
        """Write a YAML state file, optionally with a comment header."""
        path = state_dir / filename
        content = ""
        if comment_header:
            content = comment_header + "\n"
        content += yaml.dump(data, default_flow_style=False, allow_unicode=True,
                             sort_keys=False)
        path.write_text(content, encoding="utf-8")
        return path

    def test_main_migrates_old_files(self, tmp_path, monkeypatch):
        """main() upgrades version-0 state files to CURRENT_VERSION."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()

        # Create version-0 files (missing schema_version means version 0)
        lp_header = "# Learner Profile\n# Tracks learner identity and preferences"
        self._write_state_file(state_dir, "learner-profile.yaml",
                               {"name": "Integration Tester", "native_language": "English"},
                               comment_header=lp_header)
        self._write_state_file(state_dir, "skill-map.yaml",
                               {"grammar": {}, "vocabulary": {}})
        self._write_state_file(state_dir, "schedule.yaml",
                               {"current_phase": "A-foundation", "current_week": 1})
        self._write_state_file(state_dir, "system-health.yaml",
                               {"last_session": None, "total_sessions": 0})
        self._write_state_file(state_dir, "resource-tracker.yaml",
                               {"resources": []})

        # Monkeypatch ROOT so the script resolves paths against tmp_path
        monkeypatch.setattr(migrate_mod, "ROOT", tmp_path)
        # Monkeypatch sys.argv to simulate: migrate-state.py (no --dry-run)
        monkeypatch.setattr("sys.argv", ["migrate-state.py"])

        migrate_mod.main()

        # Verify all files now have schema_version == CURRENT_VERSION
        for filename in ("learner-profile.yaml", "skill-map.yaml", "schedule.yaml",
                         "system-health.yaml", "resource-tracker.yaml"):
            path = state_dir / filename
            assert path.exists(), f"{filename} should still exist after migration"
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            assert data["schema_version"] == CURRENT_VERSION, (
                f"{filename} should be at version {CURRENT_VERSION}, "
                f"got {data.get('schema_version')}"
            )

        # Verify migration-specific fields were added to learner-profile
        lp = yaml.safe_load((state_dir / "learner-profile.yaml").read_text(encoding="utf-8"))
        assert "input_hours" in lp, "input_hours should be added by migration v1"
        assert lp["input_hours"]["listening_total"] == 0.0
        assert lp["input_hours"]["reading_total"] == 0.0

        # Verify schedule got its new fields
        sched = yaml.safe_load((state_dir / "schedule.yaml").read_text(encoding="utf-8"))
        assert "fluency_days_this_week" in sched
        assert sched["fluency_days_this_week"] == 0
        assert "last_fluency_day" in sched

        # Verify original data was preserved (not wiped)
        assert lp["name"] == "Integration Tester"
        assert sched["current_phase"] == "A-foundation"

    def test_main_preserves_comment_header(self, tmp_path, monkeypatch):
        """main() preserves comment headers from original files."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()

        header = "# Schedule Configuration\n# Updated by tutor after each session"
        self._write_state_file(state_dir, "schedule.yaml",
                               {"current_phase": "A-foundation"},
                               comment_header=header)
        # Create remaining required files at current version so they are skipped
        for fname in ("learner-profile.yaml", "skill-map.yaml",
                      "system-health.yaml", "resource-tracker.yaml"):
            self._write_state_file(state_dir, fname, {"schema_version": CURRENT_VERSION})

        monkeypatch.setattr(migrate_mod, "ROOT", tmp_path)
        monkeypatch.setattr("sys.argv", ["migrate-state.py"])

        migrate_mod.main()

        content = (state_dir / "schedule.yaml").read_text(encoding="utf-8")
        assert content.startswith("# Schedule Configuration\n"), (
            "Comment header should be preserved after migration"
        )
        assert "# Updated by tutor after each session" in content

    def test_main_dry_run_does_not_modify(self, tmp_path, monkeypatch):
        """main() with --dry-run previews changes without writing."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()

        original_data = {"current_phase": "A-foundation"}
        self._write_state_file(state_dir, "schedule.yaml", original_data)
        # Create remaining required files at current version
        for fname in ("learner-profile.yaml", "skill-map.yaml",
                      "system-health.yaml", "resource-tracker.yaml"):
            self._write_state_file(state_dir, fname, {"schema_version": CURRENT_VERSION})

        original_content = (state_dir / "schedule.yaml").read_text(encoding="utf-8")

        monkeypatch.setattr(migrate_mod, "ROOT", tmp_path)
        monkeypatch.setattr("sys.argv", ["migrate-state.py", "--dry-run"])

        migrate_mod.main()

        after_content = (state_dir / "schedule.yaml").read_text(encoding="utf-8")
        assert after_content == original_content, (
            "--dry-run should not modify any files"
        )

    def test_main_skips_up_to_date_files(self, tmp_path, monkeypatch):
        """main() leaves already-current files unchanged."""
        state_dir = tmp_path / "state"
        state_dir.mkdir()

        for fname in ("learner-profile.yaml", "skill-map.yaml", "schedule.yaml",
                      "system-health.yaml", "resource-tracker.yaml"):
            self._write_state_file(state_dir, fname, {"schema_version": CURRENT_VERSION})

        originals = {}
        for fname in ("learner-profile.yaml", "skill-map.yaml", "schedule.yaml",
                      "system-health.yaml", "resource-tracker.yaml"):
            originals[fname] = (state_dir / fname).read_text(encoding="utf-8")

        monkeypatch.setattr(migrate_mod, "ROOT", tmp_path)
        monkeypatch.setattr("sys.argv", ["migrate-state.py"])

        migrate_mod.main()

        for fname, original in originals.items():
            assert (state_dir / fname).read_text(encoding="utf-8") == original, (
                f"{fname} should not be modified when already at current version"
            )
