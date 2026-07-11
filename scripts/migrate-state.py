#!/usr/bin/env python3
"""Add missing fields to state files when schema evolves.
Run after pulling updates: python3 scripts/migrate-state.py [--dry-run]
"""
import argparse
import copy
import sys
from collections.abc import Callable

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

import shared
from shared import ROOT, green, yellow, red
CURRENT_VERSION = 1

# ---------------------------------------------------------------------------
# Migration operations
# ---------------------------------------------------------------------------
#
# MIGRATIONS maps a target schema_version N to the list of operations that
# upgrade a file from version N-1 to N. main() applies them as a *chain*: a
# file at version F is walked forward one version at a time (F+1, F+2, ... up
# to CURRENT_VERSION), applying every op whose "file" matches. This generalizes
# the original additive-only (file, dotpath, default) tuples; the v1 entries
# below are those same additive fields re-expressed as {"op": "add", ...}
# dicts, so current/older state files migrate byte-for-byte as before.
#
# Each operation is a dict keyed by "op":
#   add       {"op": "add",       "file", "path", "default"}
#             add `path` set to `default` if the field is missing (idempotent).
#   remove    {"op": "remove",    "file", "path"}
#             delete `path` if present.
#   rename    {"op": "rename",    "file", "from", "to"}
#             move the value at `from` to `to` (no-op if `from` is absent).
#   transform {"op": "transform", "file", "fn"}
#             call TRANSFORMS[fn](data) -> data for reshaping the four
#             structural ops can't express (e.g. splitting a field, recomputing
#             a value). The function receives and returns the whole file dict.
#
# `path`/`from`/`to` are dot-separated (e.g. "input_hours.listening_total").

MIGRATIONS: dict[int, list[dict]] = {
    1: [
        # schema_version itself (added to all state files)
        {"op": "add", "file": "state/learner-profile.yaml", "path": "schema_version", "default": 1},
        {"op": "add", "file": "state/skill-map.yaml", "path": "schema_version", "default": 1},
        {"op": "add", "file": "state/schedule.yaml", "path": "schema_version", "default": 1},
        {"op": "add", "file": "state/system-health.yaml", "path": "schema_version", "default": 1},
        {"op": "add", "file": "state/resource-tracker.yaml", "path": "schema_version", "default": 1},
        # input_hours section in learner-profile
        {"op": "add", "file": "state/learner-profile.yaml", "path": "input_hours", "default": {
            "listening_total": 0.0,
            "reading_total": 0.0,
            "last_updated": None,
        }},
        # fluency tracking in schedule
        {"op": "add", "file": "state/schedule.yaml", "path": "fluency_days_this_week", "default": 0},
        {"op": "add", "file": "state/schedule.yaml", "path": "last_fluency_day", "default": None},
    ],
}

# TRANSFORMS: named data-reshaping functions referenced by
# {"op": "transform", "fn": <name>}. Each takes the file's data dict and
# returns the transformed dict (it may mutate in place and return the same
# object). Empty until a future schema version needs a reshape the structural
# ops can't express — register the function here and reference it by name.
TRANSFORMS: dict[str, Callable[[dict], dict]] = {}


def get_nested(data: dict, field_path: str) -> tuple[bool, object]:
    """Check if a nested field exists. Returns (exists, value)."""
    keys = field_path.split(".")
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return False, None
        current = current[key]
    return True, current


def set_nested(data: dict, field_path: str, value: object) -> None:
    """Set a nested field, creating intermediate dicts as needed."""
    keys = field_path.split(".")
    current = data
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def remove_nested(data: dict, field_path: str) -> bool:
    """Delete a nested field if present. Returns True if a value was removed."""
    keys = field_path.split(".")
    current = data
    for key in keys[:-1]:
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]
    if isinstance(current, dict) and keys[-1] in current:
        del current[keys[-1]]
        return True
    return False


def apply_operation(data: dict, op: dict, dry_run: bool) -> tuple[dict, list[str]]:
    """Apply one migration operation to a single file's `data`.

    Returns ``(data, changes)``. `data` is the resulting document — the same
    object for the structural ops (add/remove/rename), possibly a new object
    for a transform. `changes` is a list of human-readable change descriptions,
    empty when the op is a no-op (e.g. an additive field that already exists, a
    rename whose source is absent, a transform that touched nothing). When
    `dry_run` is set, `data` is left unmodified but `changes` still reflects
    what would change.
    """
    kind = op["op"]

    if kind == "add":
        path, default = op["path"], op.get("default")
        exists, _ = get_nested(data, path)
        if exists:
            return data, []
        if not dry_run:
            set_nested(data, path, default)
        # Match the original CLI: dry-run shows the value, applied does not.
        return data, [f"+ {path} = {default}" if dry_run else f"+ {path}"]

    if kind == "remove":
        path = op["path"]
        exists, _ = get_nested(data, path)
        if not exists:
            return data, []
        if not dry_run:
            remove_nested(data, path)
        return data, [f"- {path}"]

    if kind == "rename":
        src, dst = op["from"], op["to"]
        exists, value = get_nested(data, src)
        if not exists:
            return data, []
        if not dry_run:
            remove_nested(data, src)
            set_nested(data, dst, value)
        return data, [f"~ {src} -> {dst}"]

    if kind == "transform":
        fn_name = op["fn"]
        if fn_name not in TRANSFORMS:
            raise KeyError(f"unknown transform {fn_name!r} (not in TRANSFORMS registry)")
        fn = TRANSFORMS[fn_name]
        before = copy.deepcopy(data)
        result = fn(copy.deepcopy(data)) if dry_run else fn(data)
        changed = result != before
        # Thread the transformed document through even in dry-run (it is a
        # deep copy, never written to disk) so later ops in the same file's
        # chain preview against the post-transform shape — otherwise dry-run
        # under-reports ops that depend on a transform's output.
        return result, ([f"* transform {fn_name}"] if changed else [])

    raise ValueError(f"unknown migration op: {kind!r}")


def load_state_file(rel_path: str) -> tuple[dict | None, str | None]:
    """Load a state YAML file. Returns (data, error_msg)."""
    path = ROOT / rel_path
    if not path.exists(): return None, f"file not found: {rel_path}"
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}, None
    except yaml.YAMLError as e:
        return None, f"YAML parse error in {rel_path}: {e}"


def save_state_file(rel_path: str, data: dict, original_text: str) -> None:
    """Save a state file, preserving comment header from the original.

    Handles blank lines between comment blocks and between comments and the
    first YAML key, as well as files that start with blank lines before comments.
    """
    hdr: list[str] = []
    for line in original_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            hdr.append(line)
        elif stripped == "":
            # Blank line — keep collecting; it may be between comment blocks
            hdr.append(line)
        else:
            # First non-comment, non-blank line: YAML body starts here
            break
    if hdr:
        # Strip trailing blank lines from header so we control the separator
        while hdr and hdr[-1].strip() == "":
            hdr.pop()
    header = "\n".join(hdr) + "\n\n" if hdr else ""
    body = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    shared.atomic_write(ROOT / rel_path, header + body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate state files to current schema version.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    all_files = sorted({op["file"] for migs in MIGRATIONS.values() for op in migs})
    total_added = total_errors = 0
    if args.dry_run:
        print(yellow("DRY RUN — no files will be modified\n"))

    for rel_path in all_files:
        data, error = load_state_file(rel_path)
        if error:
            print(red(f"  ERROR: {error}")); total_errors += 1; continue
        original_text = (ROOT / rel_path).read_text(encoding="utf-8")
        file_version = data.get("schema_version", 0)
        if file_version >= CURRENT_VERSION:
            print(f"  {rel_path}: already at version {file_version}"); continue
        print(f"  {rel_path}: version {file_version} -> {CURRENT_VERSION}")
        file_changes = 0
        for version in range(file_version + 1, CURRENT_VERSION + 1):
            if version not in MIGRATIONS: continue
            for op in MIGRATIONS[version]:
                if op["file"] != rel_path:
                    continue
                data, changes = apply_operation(data, op, args.dry_run)
                for desc in changes:
                    print(green(f"    {desc}"))
                file_changes += len(changes)
        data["schema_version"] = CURRENT_VERSION
        if not args.dry_run:
            save_state_file(rel_path, data, original_text)
        total_added += file_changes

    print(f"\n=== Summary ===\n  Fields added: {total_added}\n  Errors: {total_errors}"
          f"\n  Target version: {CURRENT_VERSION}")
    if args.dry_run: print(yellow("  (dry run — no changes written)"))
    elif total_added > 0: print(green("  Migration complete."))
    else: print("  All files already up to date.")


if __name__ == "__main__":
    main()
