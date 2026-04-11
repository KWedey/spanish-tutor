#!/usr/bin/env python3
"""Add missing fields to state files when schema evolves.
Run after pulling updates: python3 scripts/migrate-state.py [--dry-run]
"""
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from shared import ROOT, STATE_DIR
CURRENT_VERSION = 1
_C = sys.stdout.isatty()
green = lambda t: f"\033[32m{t}\033[0m" if _C else t
yellow = lambda t: f"\033[33m{t}\033[0m" if _C else t
red = lambda t: f"\033[31m{t}\033[0m" if _C else t

# Migrations: version -> [(file, dot.field.path, default_value), ...]
# Applied cumulatively from file's current schema_version to CURRENT_VERSION.

MIGRATIONS: dict[int, list[tuple[str, str, object]]] = {
    1: [
        # schema_version itself (added to all state files)
        ("state/learner-profile.yaml", "schema_version", 1),
        ("state/skill-map.yaml", "schema_version", 1),
        ("state/schedule.yaml", "schema_version", 1),
        ("state/system-health.yaml", "schema_version", 1),
        ("state/resource-tracker.yaml", "schema_version", 1),
        # input_hours section in learner-profile
        ("state/learner-profile.yaml", "input_hours", {
            "listening_total": 0.0,
            "reading_total": 0.0,
            "last_updated": None,
        }),
        # fluency tracking in schedule
        ("state/schedule.yaml", "fluency_days_this_week", 0),
        ("state/schedule.yaml", "last_fluency_day", None),
    ],
}


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


def load_state_file(rel_path: str) -> tuple[dict | None, str | None]:
    """Load a state YAML file. Returns (data, error_msg)."""
    path = ROOT / rel_path
    if not path.exists(): return None, f"file not found: {rel_path}"
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}, None
    except yaml.YAMLError as e:
        return None, f"YAML parse error in {rel_path}: {e}"


def save_state_file(rel_path: str, data: dict, original_text: str) -> None:
    """Save a state file, preserving comment header from the original."""
    hdr = []
    for line in original_text.splitlines():
        if line.startswith("#"): hdr.append(line)
        else: break
    header = "\n".join(hdr) + "\n\n" if hdr else ""
    body = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    (ROOT / rel_path).write_text(header + body, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate state files to current schema version.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    all_files = sorted({f for migs in MIGRATIONS.values() for f, _, _ in migs})
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
            for m_file, field_path, default in MIGRATIONS[version]:
                if m_file != rel_path: continue
                exists, _ = get_nested(data, field_path)
                if not exists:
                    if args.dry_run:
                        print(green(f"    + {field_path} = {default}"))
                    else:
                        set_nested(data, field_path, default)
                        print(green(f"    + {field_path}"))
                    file_changes += 1
        data["schema_version"] = CURRENT_VERSION
        if not args.dry_run and file_changes > 0:
            save_state_file(rel_path, data, original_text)
        total_added += file_changes

    print(f"\n=== Summary ===\n  Fields added: {total_added}\n  Errors: {total_errors}"
          f"\n  Target version: {CURRENT_VERSION}")
    if args.dry_run: print(yellow("  (dry run — no changes written)"))
    elif total_added > 0: print(green("  Migration complete."))
    else: print("  All files already up to date.")


if __name__ == "__main__":
    main()
