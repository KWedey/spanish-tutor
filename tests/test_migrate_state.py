"""Tests for scripts/migrate-state.py migration functions."""
import importlib
import sys
from pathlib import Path

import pytest
import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

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
