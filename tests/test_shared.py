"""Tests for scripts/shared.py utility functions and constants."""
import sys
from pathlib import Path

import pytest
import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import shared


# ---------------------------------------------------------------------------
# 1. load_yaml returns dict
# ---------------------------------------------------------------------------

class TestLoadYaml:
    def test_valid_yaml_returns_dict(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("key: value\nnumber: 42\n", encoding="utf-8")

        result = shared.load_yaml(f)

        assert isinstance(result, dict)
        assert result["key"] == "value"
        assert result["number"] == 42


# ---------------------------------------------------------------------------
# 2. load_yaml returns empty dict for empty file
# ---------------------------------------------------------------------------

class TestLoadYamlEmpty:
    def test_empty_file_returns_empty_dict(self, tmp_path):
        f = tmp_path / "empty.yaml"
        f.write_text("", encoding="utf-8")

        result = shared.load_yaml(f)

        assert result == {}

    def test_null_only_returns_empty_dict(self, tmp_path):
        f = tmp_path / "null.yaml"
        f.write_text("null\n", encoding="utf-8")

        # yaml.safe_load("null") returns None, so load_yaml should return {}
        result = shared.load_yaml(f)
        assert result == {}


# ---------------------------------------------------------------------------
# 3. load_schema loads schema files
# ---------------------------------------------------------------------------

class TestLoadSchema:
    def test_loads_schema_with_fields_key(self):
        # Test with a real schema file from the project
        result = shared.load_schema("learner-profile")

        assert isinstance(result, dict)
        assert "fields" in result

    def test_missing_schema_raises(self):
        with pytest.raises(FileNotFoundError):
            shared.load_schema("nonexistent-schema")


# ---------------------------------------------------------------------------
# 4. get_required_fields filters correctly
# ---------------------------------------------------------------------------

class TestGetRequiredFields:
    def test_filters_required_true(self):
        schema = {
            "fields": {
                "name": {"type": "string", "required": True},
                "nickname": {"type": "string", "required": False},
                "age": {"type": "int", "required": True},
                "notes": {"type": "string"},
            }
        }

        result = shared.get_required_fields(schema)

        assert "name" in result
        assert "age" in result
        assert "nickname" not in result
        assert "notes" not in result

    def test_empty_schema_returns_empty(self):
        assert shared.get_required_fields({}) == []
        assert shared.get_required_fields({"fields": {}}) == []


# ---------------------------------------------------------------------------
# 5. Path constants exist and are valid Path objects
# ---------------------------------------------------------------------------

class TestPathConstants:
    def test_root_is_path(self):
        assert isinstance(shared.ROOT, Path)

    def test_state_dir_is_path(self):
        assert isinstance(shared.STATE_DIR, Path)

    def test_curriculum_dir_is_path(self):
        assert isinstance(shared.CURRICULUM_DIR, Path)

    def test_vault_dir_is_path(self):
        assert isinstance(shared.VAULT_DIR, Path)

    def test_schemas_dir_is_path(self):
        assert isinstance(shared.SCHEMAS_DIR, Path)

    def test_root_contains_state(self):
        assert shared.STATE_DIR == shared.ROOT / "state"

    def test_root_contains_schemas(self):
        assert shared.SCHEMAS_DIR == shared.ROOT / "schemas"
