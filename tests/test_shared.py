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

    def test_missing_file_returns_none(self, tmp_path):
        """E-01: missing files return None instead of raising."""
        f = tmp_path / "does-not-exist.yaml"

        result = shared.load_yaml(f)

        assert result is None

    def test_malformed_yaml_returns_none(self, tmp_path):
        """E-02: YAML parse errors return None instead of propagating."""
        f = tmp_path / "bad.yaml"
        f.write_text("key: [unterminated", encoding="utf-8")

        result = shared.load_yaml(f)

        assert result is None


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


# ---------------------------------------------------------------------------
# 6. get_field_default handles types and defaults
# ---------------------------------------------------------------------------

class TestGetFieldDefault:
    def test_type_list_default_none_returns_none(self):
        # default=None triggers early return before type coercion
        result = shared.get_field_default({"type": "list", "default": None})
        assert result is None

    def test_type_map_default_none_returns_none(self):
        result = shared.get_field_default({"type": "map", "default": None})
        assert result is None

    def test_explicit_default_returned(self):
        result = shared.get_field_default({"type": "string", "default": "hello"})
        assert result == "hello"

    def test_no_default_key_returns_none(self):
        result = shared.get_field_default({"type": "string"})
        assert result is None


# ---------------------------------------------------------------------------
# 7. atomic_write writes atomically
# ---------------------------------------------------------------------------

class TestAtomicWrite:
    def test_writes_content_to_file(self, tmp_path):
        target = tmp_path / "out.yaml"

        shared.atomic_write(target, "key: value\n")

        assert target.exists()
        assert target.read_text(encoding="utf-8") == "key: value\n"

    def test_creates_parent_dirs(self, tmp_path):
        target = tmp_path / "sub" / "dir" / "file.yaml"

        shared.atomic_write(target, "hello\n")

        assert target.exists()
        assert target.read_text(encoding="utf-8") == "hello\n"

    def test_overwrites_existing_file(self, tmp_path):
        target = tmp_path / "existing.yaml"
        target.write_text("old content\n", encoding="utf-8")

        shared.atomic_write(target, "new content\n")

        assert target.read_text(encoding="utf-8") == "new content\n"

    def test_no_temp_file_left_on_success(self, tmp_path):
        target = tmp_path / "clean.yaml"

        shared.atomic_write(target, "data\n")

        remaining = list(tmp_path.iterdir())
        assert len(remaining) == 1
        assert remaining[0].name == "clean.yaml"
