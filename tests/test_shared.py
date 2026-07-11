"""Tests for scripts/shared.py utility functions and constants.

scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
"""
from pathlib import Path

import pytest
import yaml

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
# 1b. load_yaml_strict — non-lossy loader for write-back paths (A3)
# ---------------------------------------------------------------------------


class TestLoadYamlStrict:
    """A3: load_yaml_strict must distinguish corrupt from empty/missing so a
    write-back caller never silently re-serializes a corrupt file as {}.
    """

    def test_valid_yaml_returns_dict(self, tmp_path):
        f = tmp_path / "ok.yaml"
        f.write_text("a: 1\nb: two\n", encoding="utf-8")
        result = shared.load_yaml_strict(f)
        assert result == {"a": 1, "b": "two"}

    def test_empty_file_returns_empty_dict(self, tmp_path):
        """An empty file is valid (not corrupt) — return {}, like load_yaml."""
        f = tmp_path / "empty.yaml"
        f.write_text("", encoding="utf-8")
        assert shared.load_yaml_strict(f) == {}

    def test_null_only_returns_empty_dict(self, tmp_path):
        f = tmp_path / "null.yaml"
        f.write_text("null\n", encoding="utf-8")
        assert shared.load_yaml_strict(f) == {}

    def test_corrupt_yaml_raises(self, tmp_path):
        """The whole point: corrupt YAML must RAISE, not collapse to None/{}.

        Contrast with load_yaml, which returns None here and lets a
        `load_yaml(p) or {}` caller overwrite p with {}.
        """
        f = tmp_path / "bad.yaml"
        f.write_text("key: [unterminated\n  : : :\n", encoding="utf-8")
        with pytest.raises(yaml.YAMLError):
            shared.load_yaml_strict(f)

    def test_corrupt_yaml_error_names_path(self, tmp_path):
        """The raised error must mention the offending path for a clean message."""
        f = tmp_path / "bad.yaml"
        f.write_text("key: [unterminated\n  : : :\n", encoding="utf-8")
        with pytest.raises(yaml.YAMLError) as excinfo:
            shared.load_yaml_strict(f)
        assert "bad.yaml" in str(excinfo.value)

    def test_missing_file_raises(self, tmp_path):
        """A missing file on a strict (write-back) path is a real error."""
        f = tmp_path / "nope.yaml"
        with pytest.raises(FileNotFoundError):
            shared.load_yaml_strict(f)


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


# ---------------------------------------------------------------------------
# 8. StateStore — the portable storage seam (docs/engine-api.md)
# ---------------------------------------------------------------------------

class TestStateStoreDocs:
    """load/save round-trip and missing-doc semantics for top-level documents."""

    def test_load_missing_doc_returns_none(self, tmp_path):
        store = shared.StateStore(tmp_path / "state")
        assert store.load("schedule") is None

    def test_save_then_load_round_trip(self, tmp_path):
        store = shared.StateStore(tmp_path / "state")
        data = {"schema_version": 1, "current_phase": "A-foundation", "week": 3}

        store.save("schedule", data)
        loaded = store.load("schedule")

        assert loaded == data

    def test_save_writes_expected_path(self, tmp_path):
        state_dir = tmp_path / "state"
        store = shared.StateStore(state_dir)

        store.save("skill-map", {"grammar": {}})

        assert (state_dir / "skill-map.yaml").exists()

    def test_save_creates_state_dir(self, tmp_path):
        # Constructor must not require the directory to pre-exist.
        store = shared.StateStore(tmp_path / "does-not-exist-yet")
        store.save("system-health", {"schema_version": 1})
        assert store.load("system-health") == {"schema_version": 1}

    def test_save_overwrites_existing(self, tmp_path):
        store = shared.StateStore(tmp_path / "state")
        store.save("schedule", {"week": 1})
        store.save("schedule", {"week": 2})
        assert store.load("schedule") == {"week": 2}

    def test_save_is_atomic_no_temp_left(self, tmp_path):
        state_dir = tmp_path / "state"
        store = shared.StateStore(state_dir)

        store.save("schedule", {"week": 1})

        # Only the target file remains; the atomic-write temp file is gone.
        remaining = sorted(p.name for p in state_dir.iterdir())
        assert remaining == ["schedule.yaml"]

    def test_string_state_dir_accepted(self, tmp_path):
        store = shared.StateStore(str(tmp_path / "state"))
        store.save("schedule", {"week": 1})
        assert store.load("schedule") == {"week": 1}

    def test_default_state_dir_is_repo_state(self):
        store = shared.StateStore()
        assert store.state_dir == shared.STATE_DIR
        assert store.sessions_dir == shared.STATE_DIR / "sessions"


class TestStateStoreSessions:
    """list/load/save for per-day session logs."""

    def test_list_sessions_empty_when_no_dir(self, tmp_path):
        store = shared.StateStore(tmp_path / "state")
        assert store.list_sessions() == []

    def test_save_then_load_session_round_trip(self, tmp_path):
        store = shared.StateStore(tmp_path / "state")
        log = {"date": "2026-04-10", "session_number": 5, "session_type": "standard"}

        store.save_session("2026-04-10", log)
        loaded = store.load_session("2026-04-10")

        assert loaded == log

    def test_load_missing_session_returns_none(self, tmp_path):
        store = shared.StateStore(tmp_path / "state")
        store.save_session("2026-04-10", {"date": "2026-04-10"})
        assert store.load_session("2026-04-11") is None

    def test_list_sessions_sorted_ascending(self, tmp_path):
        store = shared.StateStore(tmp_path / "state")
        for d in ("2026-04-12", "2026-04-01", "2026-04-07"):
            store.save_session(d, {"date": d})

        assert store.list_sessions() == ["2026-04-01", "2026-04-07", "2026-04-12"]

    def test_list_sessions_ignores_archive_and_stray_files(self, tmp_path):
        state_dir = tmp_path / "state"
        store = shared.StateStore(state_dir)
        store.save_session("2026-04-10", {"date": "2026-04-10"})

        # An archive subtree and a non-date stray file must not be reported.
        archive = state_dir / "sessions" / "archive"
        archive.mkdir(parents=True, exist_ok=True)
        (archive / "2026-01-01.yaml").write_text("date: 2026-01-01\n", encoding="utf-8")
        (state_dir / "sessions" / "index.yaml").write_text("note: not a log\n",
                                                           encoding="utf-8")

        assert store.list_sessions() == ["2026-04-10"]

    def test_save_session_is_atomic_no_temp_left(self, tmp_path):
        state_dir = tmp_path / "state"
        store = shared.StateStore(state_dir)

        store.save_session("2026-04-10", {"date": "2026-04-10"})

        remaining = sorted(p.name for p in (state_dir / "sessions").iterdir())
        assert remaining == ["2026-04-10.yaml"]
