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
remove_nested = migrate_mod.remove_nested
apply_operation = migrate_mod.apply_operation
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

        # Simulate migration: gather the add-ops targeting this file.
        ops_for_file = []
        for version in range(1, CURRENT_VERSION + 1):
            if version not in MIGRATIONS:
                continue
            for op in MIGRATIONS[version]:
                if op["file"] == "state/learner-profile.yaml":
                    ops_for_file.append(op)

        # Apply migrations via apply_operation (same path as main())
        loaded, error = load_state_file("state/learner-profile.yaml")
        assert error is None

        for op in ops_for_file:
            loaded, _ = apply_operation(loaded, op, dry_run=False)

        loaded["schema_version"] = CURRENT_VERSION

        # Verify the add-op fields were added
        for op in ops_for_file:
            assert op["op"] == "add"
            exists, _ = get_nested(loaded, op["path"])
            assert exists, f"Field '{op['path']}' should have been added by migration"


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


# ---------------------------------------------------------------------------
# 7. remove_nested deletes a nested field
# ---------------------------------------------------------------------------

class TestRemoveNested:
    def test_removes_top_level(self):
        data = {"a": 1, "b": 2}
        assert remove_nested(data, "a") is True
        assert data == {"b": 2}

    def test_removes_nested(self):
        data = {"a": {"b": {"c": 1, "d": 2}}}
        assert remove_nested(data, "a.b.c") is True
        assert data == {"a": {"b": {"d": 2}}}

    def test_missing_leaf_returns_false(self):
        data = {"a": {"b": 1}}
        assert remove_nested(data, "a.z") is False
        assert data == {"a": {"b": 1}}

    def test_missing_intermediate_returns_false(self):
        data = {"a": 1}
        assert remove_nested(data, "x.y.z") is False
        assert data == {"a": 1}

    def test_non_dict_intermediate_returns_false(self):
        data = {"a": "string"}
        assert remove_nested(data, "a.b") is False
        assert data == {"a": "string"}


# ---------------------------------------------------------------------------
# 8. apply_operation — one test per op type (add / remove / rename / transform)
# ---------------------------------------------------------------------------

class TestApplyOperationAdd:
    def test_adds_missing_field(self):
        data = {"x": 1}
        op = {"op": "add", "file": "state/schedule.yaml", "path": "y", "default": 5}
        result, changes = apply_operation(data, op, dry_run=False)
        assert result is data
        assert data["y"] == 5
        assert changes == ["+ y"]

    def test_existing_field_is_noop(self):
        data = {"y": 99}
        op = {"op": "add", "file": "f", "path": "y", "default": 5}
        result, changes = apply_operation(data, op, dry_run=False)
        assert data["y"] == 99
        assert changes == []

    def test_dry_run_shows_value_but_does_not_write(self):
        data = {}
        op = {"op": "add", "file": "f", "path": "y", "default": 5}
        result, changes = apply_operation(data, op, dry_run=True)
        assert "y" not in data
        assert changes == ["+ y = 5"]

    def test_nested_default(self):
        data = {}
        op = {"op": "add", "file": "f", "path": "a.b.c", "default": 7}
        apply_operation(data, op, dry_run=False)
        assert data == {"a": {"b": {"c": 7}}}


class TestApplyOperationRemove:
    def test_removes_present_field(self):
        data = {"legacy": 1, "keep": 2}
        op = {"op": "remove", "file": "f", "path": "legacy"}
        _, changes = apply_operation(data, op, dry_run=False)
        assert data == {"keep": 2}
        assert changes == ["- legacy"]

    def test_absent_field_is_noop(self):
        data = {"keep": 2}
        op = {"op": "remove", "file": "f", "path": "legacy"}
        _, changes = apply_operation(data, op, dry_run=False)
        assert data == {"keep": 2}
        assert changes == []

    def test_dry_run_does_not_remove(self):
        data = {"legacy": 1}
        op = {"op": "remove", "file": "f", "path": "legacy"}
        _, changes = apply_operation(data, op, dry_run=True)
        assert data == {"legacy": 1}
        assert changes == ["- legacy"]


class TestApplyOperationRename:
    def test_moves_value(self):
        data = {"old_name": "v", "other": 1}
        op = {"op": "rename", "file": "f", "from": "old_name", "to": "new_name"}
        _, changes = apply_operation(data, op, dry_run=False)
        assert data == {"new_name": "v", "other": 1}
        assert changes == ["~ old_name -> new_name"]

    def test_rename_into_nested_path(self):
        data = {"flat": 42}
        op = {"op": "rename", "file": "f", "from": "flat", "to": "group.flat"}
        apply_operation(data, op, dry_run=False)
        assert data == {"group": {"flat": 42}}

    def test_absent_source_is_noop(self):
        data = {"other": 1}
        op = {"op": "rename", "file": "f", "from": "missing", "to": "dest"}
        _, changes = apply_operation(data, op, dry_run=False)
        assert data == {"other": 1}
        assert changes == []

    def test_dry_run_does_not_move(self):
        data = {"old_name": "v"}
        op = {"op": "rename", "file": "f", "from": "old_name", "to": "new_name"}
        _, changes = apply_operation(data, op, dry_run=True)
        assert data == {"old_name": "v"}
        assert changes == ["~ old_name -> new_name"]


class TestApplyOperationTransform:
    def test_transform_reshapes_data(self, monkeypatch):
        def double_count(d: dict) -> dict:
            d["count"] = d.get("count", 0) * 2
            return d

        monkeypatch.setattr(migrate_mod, "TRANSFORMS", {"double_count": double_count})
        data = {"count": 3}
        op = {"op": "transform", "file": "f", "fn": "double_count"}
        result, changes = apply_operation(data, op, dry_run=False)
        assert result["count"] == 6
        assert changes == ["* transform double_count"]

    def test_transform_dry_run_does_not_mutate(self, monkeypatch):
        def double_count(d: dict) -> dict:
            d["count"] = d.get("count", 0) * 2
            return d

        monkeypatch.setattr(migrate_mod, "TRANSFORMS", {"double_count": double_count})
        data = {"count": 3}
        op = {"op": "transform", "file": "f", "fn": "double_count"}
        _, changes = apply_operation(data, op, dry_run=True)
        assert data == {"count": 3}  # untouched
        assert changes == ["* transform double_count"]

    def test_noop_transform_reports_no_change(self, monkeypatch):
        monkeypatch.setattr(migrate_mod, "TRANSFORMS", {"identity": lambda d: d})
        data = {"count": 3}
        op = {"op": "transform", "file": "f", "fn": "identity"}
        _, changes = apply_operation(data, op, dry_run=False)
        assert changes == []

    def test_unknown_transform_raises(self):
        with pytest.raises(KeyError):
            apply_operation({}, {"op": "transform", "file": "f", "fn": "nope"}, dry_run=False)


class TestApplyOperationUnknown:
    def test_unknown_op_raises(self):
        with pytest.raises(ValueError):
            apply_operation({}, {"op": "frobnicate", "file": "f"}, dry_run=False)


# ---------------------------------------------------------------------------
# 9. Chained migration across two synthetic schema versions
# ---------------------------------------------------------------------------

class TestMigrationChain:
    """main() walks a v0 file forward through v1 then v2, applying each version's
    ops in order. Exercised against a temporarily-patched CURRENT_VERSION /
    MIGRATIONS / TRANSFORMS so the real v1-only config is untouched.
    """

    def _write(self, state_dir: Path, filename: str, data: dict) -> Path:
        path = state_dir / filename
        path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        return path

    def test_v0_to_v2_applies_both_versions_in_order(self, tmp_path, monkeypatch):
        state_dir = tmp_path / "state"
        state_dir.mkdir()

        # A version-0 file carrying a legacy field we will rename, then reshape.
        self._write(state_dir, "schedule.yaml", {"legacy_days": 4, "keep": "yes"})

        def stamp_migrated(d: dict) -> dict:
            d["migrated"] = True
            return d

        synthetic = {
            1: [
                # v0 -> v1: rename legacy_days -> fluency_days_this_week
                {"op": "rename", "file": "state/schedule.yaml",
                 "from": "legacy_days", "to": "fluency_days_this_week"},
                {"op": "add", "file": "state/schedule.yaml",
                 "path": "last_fluency_day", "default": None},
            ],
            2: [
                # v1 -> v2: drop a field and run a transform
                {"op": "remove", "file": "state/schedule.yaml", "path": "keep"},
                {"op": "transform", "file": "state/schedule.yaml", "fn": "stamp_migrated"},
            ],
        }

        monkeypatch.setattr(migrate_mod, "ROOT", tmp_path)
        monkeypatch.setattr(migrate_mod, "CURRENT_VERSION", 2)
        monkeypatch.setattr(migrate_mod, "MIGRATIONS", synthetic)
        monkeypatch.setattr(migrate_mod, "TRANSFORMS", {"stamp_migrated": stamp_migrated})
        monkeypatch.setattr("sys.argv", ["migrate-state.py"])

        migrate_mod.main()

        result = yaml.safe_load((state_dir / "schedule.yaml").read_text(encoding="utf-8"))
        assert result["schema_version"] == 2
        # v1 ops
        assert "legacy_days" not in result
        assert result["fluency_days_this_week"] == 4
        assert result["last_fluency_day"] is None
        # v2 ops
        assert "keep" not in result
        assert result["migrated"] is True

    def test_chain_dry_run_writes_nothing(self, tmp_path, monkeypatch):
        state_dir = tmp_path / "state"
        state_dir.mkdir()
        original = {"legacy_days": 4, "keep": "yes"}
        self._write(state_dir, "schedule.yaml", original)
        before = (state_dir / "schedule.yaml").read_text(encoding="utf-8")

        synthetic = {
            1: [{"op": "rename", "file": "state/schedule.yaml",
                 "from": "legacy_days", "to": "fluency_days_this_week"}],
            2: [{"op": "remove", "file": "state/schedule.yaml", "path": "keep"}],
        }
        monkeypatch.setattr(migrate_mod, "ROOT", tmp_path)
        monkeypatch.setattr(migrate_mod, "CURRENT_VERSION", 2)
        monkeypatch.setattr(migrate_mod, "MIGRATIONS", synthetic)
        monkeypatch.setattr("sys.argv", ["migrate-state.py", "--dry-run"])

        migrate_mod.main()

        assert (state_dir / "schedule.yaml").read_text(encoding="utf-8") == before


# ---------------------------------------------------------------------------
# 10. v1 additive behavior is unchanged (regression guard for the new format)
# ---------------------------------------------------------------------------

class TestV1AdditiveUnchanged:
    """The real (unpatched) MIGRATIONS[1] must still be additive-only add ops so
    current/older state files migrate byte-for-byte as before the refactor.
    """

    def test_all_v1_ops_are_add(self):
        for op in MIGRATIONS[1]:
            assert op["op"] == "add", f"v1 must stay additive-only, found: {op}"
            assert "path" in op and "default" in op and "file" in op

    def test_v1_covers_expected_fields(self):
        paths = {(op["file"], op["path"]) for op in MIGRATIONS[1]}
        assert ("state/schedule.yaml", "fluency_days_this_week") in paths
        assert ("state/schedule.yaml", "last_fluency_day") in paths
        assert ("state/learner-profile.yaml", "input_hours") in paths
