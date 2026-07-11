#!/usr/bin/env python3
"""Reset all student data to clean templates for sharing or starting over."""
import argparse
import subprocess
import sys

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from shared import (ROOT, STATE_DIR, load_schema, get_field_default, load_yaml,
                    yaml_value as _yaml_value, green, yellow, red)

# ---------------------------------------------------------------------------
# Schema-driven template generation
# ---------------------------------------------------------------------------

# Schema-to-file mapping and header comments for state files generated from schemas.
SCHEMA_TEMPLATES = {
    "state/learner-profile.yaml": {
        "schema": "learner-profile",
        "header": (
            "# Learner Profile — slow-changing facts about the learner\n"
            "# Updated rarely, typically during first session and at phase transitions.\n"
            "# Schema: schemas/learner-profile.schema.yaml\n"
        ),
    },
    "state/schedule.yaml": {
        "schema": "schedule",
        "header": (
            "# Schedule — the tutor's current plan\n"
            "# Updated at the end of each session.\n"
            "# Schema: schemas/schedule.schema.yaml\n"
        ),
    },
    "state/system-health.yaml": {
        "schema": "system-health",
        "header": (
            "# System Health — meta-metrics on tutoring system effectiveness\n"
            "# Updated at end of each session. Reviewed in detail during weekly reviews.\n"
            "# Schema: schemas/system-health.schema.yaml\n"
        ),
    },
    "state/resource-tracker.yaml": {
        "schema": "resource-tracker",
        "header": (
            "# Resource Tracker — which external resources are in active rotation\n"
            "# Updated when resources are added, swapped, or engagement changes.\n"
            "# Schema: schemas/resource-tracker.schema.yaml\n"
        ),
    },
}




def _render_map_children(children: dict, indent: int) -> str:
    """Render nested map children as YAML lines."""
    lines = []
    prefix = "  " * indent
    for name, spec in children.items():
        if not isinstance(spec, dict):
            continue
        default = get_field_default(spec)
        if spec.get("type") == "map" and "children" in spec:
            lines.append(f"{prefix}{name}:")
            lines.append(_render_map_children(spec["children"], indent + 1))
        else:
            lines.append(f"{prefix}{name}: {_yaml_value(default)}")
    return "\n".join(lines)


def generate_template_from_schema(schema_name: str, header: str = "") -> str:
    """Generate a default YAML template from a schema file.

    Reads schemas/<schema_name>.schema.yaml and builds a YAML string
    using default values from the schema's 'fields' section.
    """
    schema = load_schema(schema_name)
    fields = schema.get("fields", {})

    lines = []
    if header:
        lines.append(header)

    for name, spec in fields.items():
        if not isinstance(spec, dict):
            continue
        default = get_field_default(spec)
        if spec.get("type") == "map" and "children" in spec:
            lines.append(f"{name}:")
            lines.append(_render_map_children(spec["children"], 1))
        else:
            lines.append(f"{name}: {_yaml_value(default)}")

    return "\n".join(lines) + "\n"


# Template files keyed by path relative to ROOT. skill-map.yaml is reset
# in-place (too large for inline template) — see reset_skill_map().
# Schema-driven templates are generated at runtime; parking-lot is static.
TEMPLATES: dict[str, str] = {}

# Generate schema-driven templates
for _rel_path, _info in SCHEMA_TEMPLATES.items():
    TEMPLATES[_rel_path] = generate_template_from_schema(_info["schema"], _info["header"])

TEMPLATES["parking-lot.md"] = (
    "# Parking Lot — Things I Want to Learn\n\n"
    "Add anything here between sessions. Your tutor will review this at the\n"
    "start of each session and work items into lessons.\n\n"
    "## Urgent (need before an upcoming real-world situation)\n\n\n"
    "## Questions\n\n\n## Words & Phrases I Encountered\n\n\n## Completed\n\n"
)

SKILL_MAP_HEADER = (
    "# Skill Map — learner's current mastery state across all skill dimensions\n"
    "# Updated every session. The single source of truth for what has been taught "
    "and how well it's retained.\n# Schema defined in docs/system-design.md\n#\n"
    "# Status values:\n"
    "#   unseen — not yet introduced | introduced — seen once, not yet practiced\n"
    "#   practicing — error rate > 15% | acquired — error rate < 10%\n"
    "#   automatic — spot-checked only | regressed — errors resurfaced\n#\n"
    "# Context performance: null | struggling | competent\n"
    "# Acquisition requires performance_unscaffolded = competent\n\n"
)

ZERO_GRAMMAR = dict(status="unseen", introduced_date=None, last_practiced=None,
    practice_count=0, error_rate_drills=None, error_rate_production=None,
    error_trend=None, performance_scaffolded=None, performance_unscaffolded=None,
    integration_tested_with=[])

ZERO_VOCAB = dict(status="unseen", words_introduced=0, passive_known=0, active_known=0,
    weak_production=[], weak_recognition=[], last_practiced=None)

ZERO_PRONUN = dict(status="unseen", last_practiced=None, external_feedback="")


def reset_skill_map() -> None:
    """Load skill-map.yaml, zero all progress values, and rewrite.

    On a fresh clone the working file is gitignored and therefore absent —
    in that case we bootstrap from state/skill-map.template.yaml (which is
    tracked). The template is pristine already, but we still run the zero
    pass so that a stale or hand-edited template can't leak progress values.
    """
    path = STATE_DIR / "skill-map.yaml"
    template = STATE_DIR / "skill-map.template.yaml"
    if not path.exists():
        if template.exists():
            path.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
            print(yellow(f"  BOOTSTRAPPED from {template.relative_to(ROOT)}"))
        else:
            print(red(
                f"  MISSING: {path.relative_to(ROOT)} (and no template at "
                f"{template.relative_to(ROOT)})"
            ))
            return
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for entry in (data.get("grammar") or {}).values():
        if isinstance(entry, dict):
            entry.update(ZERO_GRAMMAR)
    for entry in (data.get("vocabulary") or {}).values():
        if isinstance(entry, dict):
            entry.update({k: (list(v) if isinstance(v, list) else v) for k, v in ZERO_VOCAB.items()})
    for entry in (data.get("pronunciation") or {}).values():
        if isinstance(entry, dict):
            entry.update(ZERO_PRONUN)
    for entry in (data.get("writing") or {}).values():
        if isinstance(entry, dict):
            entry["status"], entry["last_practiced"] = "unseen", None
    for key in ("listening", "reading"):
        if key in (data.get("receptive_skills") or {}):
            data["receptive_skills"][key] = {f: (None if f != "notes" else "") for f in data["receptive_skills"][key]}
    for entry in (data.get("cultural_awareness") or {}).values():
        if isinstance(entry, dict):
            entry["status"] = "unseen"
    for key in (data.get("fluency_metrics") or {}):
        data["fluency_metrics"][key] = ""
    oe = data.get("overall_estimates") or {}
    oe.update(cefr_estimate="A0", estimated_active_vocabulary=0, estimated_passive_vocabulary=0,
              production_gap=0, strongest_skill=None, weakest_skill=None, last_formal_assessment=None)
    data = {"schema_version": 1, **{k: v for k, v in data.items() if k != "schema_version"}}
    content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    path.write_text(SKILL_MAP_HEADER + content, encoding="utf-8")
    print(green(f"  RESET: {path.relative_to(ROOT)}"))


def clear_directory(rel_path: str) -> int:
    """Remove all files in a directory except .gitkeep. Returns count removed."""
    dirpath = ROOT / rel_path
    if not dirpath.exists():
        print(yellow(f"  SKIP: {rel_path}/ (does not exist)")); return 0
    files = [f for f in dirpath.iterdir() if f.name != ".gitkeep" and not f.is_dir()]
    for f in files:
        f.unlink()
    count = len(files)
    print(green(f"  CLEARED: {rel_path}/ ({count} files)") if count else f"  CLEAN: {rel_path}/")
    return count


def _dir_has_file(root, rel_path: str, suffix: str | None = None) -> bool:
    """True if root/rel_path contains any non-.gitkeep file.

    If `suffix` is given, only files with that extension count.
    """
    d = root / rel_path
    if not d.exists():
        return False
    for f in d.iterdir():
        if not f.is_file() or f.name == ".gitkeep":
            continue
        if suffix is None or f.suffix == suffix:
            return True
    return False


def has_existing_learner_data(root) -> bool:
    """Detect whether the repo already holds real learner data.

    Canonical detector for the whole toolchain: setup.py's has_existing_state()
    delegates here so the two scripts can never disagree about what counts as
    real data (init-student is the one that actually wipes it on reset). Returns
    True on any of:
      - A session log in state/sessions/
      - A journal entry in journal/
      - An archived session in state/sessions/archive/
      - A weekly summary in state/summaries/
      - A milestone in state/milestones/
      - A progress report in progress-reports/
      - Any file in state/offline-guides/
      - parking-lot.md modified from its pristine template
      - state/learner-profile.yaml with a populated name
      - state/resource-tracker.yaml with any entries in `resources`

    main() wipes all of these on --force, so any one of them must trigger a
    recovery snapshot first (P2-c: a crash or hand-edit can leave session logs
    behind an empty profile name; A2: archived-only history was the gap). Cheap
    directory iteration runs first; YAML parses are the most expensive and run
    last, failing safe (return True) on a corrupt-but-present file so --force
    never clobbers a recoverable one.
    """
    # Directory-level checks — no file content read.
    if _dir_has_file(root, "state/sessions", ".yaml"):
        return True
    if _dir_has_file(root, "journal", ".md"):
        return True
    if _dir_has_file(root, "state/sessions/archive", ".yaml"):
        return True
    if _dir_has_file(root, "state/summaries", ".yaml"):
        return True
    if _dir_has_file(root, "state/milestones", ".yaml"):
        return True
    if _dir_has_file(root, "progress-reports", ".md"):
        return True
    if _dir_has_file(root, "state/offline-guides"):
        return True

    # Parking lot: compare against pristine template. rstrip so a trailing
    # newline drift between platforms doesn't trigger a false positive.
    parking_lot = root / "parking-lot.md"
    if parking_lot.exists():
        try:
            if parking_lot.read_text(encoding="utf-8").rstrip() != TEMPLATES["parking-lot.md"].rstrip():
                return True
        except OSError:
            pass

    # YAML parses — most expensive checks go last. A parse failure (corrupt-but-
    # present state) must read as "state present" (return True), NOT swallowed
    # into the fall-through `return False`; otherwise --force WIPES a recoverable
    # file. Narrow the except to the parse/IO errors we expect and fail safe.
    profile_path = root / "state" / "learner-profile.yaml"
    if profile_path.exists():
        try:
            data = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
            name = data.get("name")
            if name and str(name).strip():
                return True
        except (OSError, yaml.YAMLError):
            # Corrupt or unreadable — refuse to clobber it.
            return True

    # Resource tracker: any populated `resources` list counts as user data.
    # The pristine template has `resources: []`; --force would wipe anything
    # the learner added.
    rt_path = root / "state" / "resource-tracker.yaml"
    if rt_path.exists():
        try:
            data = yaml.safe_load(rt_path.read_text(encoding="utf-8")) or {}
            if data.get("resources"):
                return True
        except (OSError, yaml.YAMLError):
            # Corrupt or unreadable — refuse to clobber it.
            return True

    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset all student data to clean templates.")
    parser.add_argument("--force", action="store_true",
                        help="Skip the interactive confirmation prompt (a recovery snapshot is taken whenever prior learner data is detected)")
    args = parser.parse_args()

    # --- Step 0: Detect prior learner state (D-09 gate) ---
    profile_path = ROOT / "state" / "learner-profile.yaml"
    profile_data = load_yaml(profile_path) or {}
    name = profile_data.get("name")
    has_prior_learner = has_existing_learner_data(ROOT)

    if has_prior_learner:
        # --- Step 1: Snapshot BEFORE any writes (D-07, unconditional even under --force) ---
        print(yellow("\n=== Taking recovery snapshot ==="))
        snapshot_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "snapshot-state.py"), "snapshot"],
            cwd=str(ROOT),
        )
        if snapshot_result.returncode != 0:
            print(red("Snapshot failed — cannot safely reset. Aborting."))
            sys.exit(1)

        # --- Step 2: Gather pre-wipe state for display ---
        schedule_data = load_yaml(ROOT / "state" / "schedule.yaml") or {}
        last_session = schedule_data.get("last_session_date", None)
        if not last_session:
            # Fall back to most recent session log filename
            session_dir = ROOT / "state" / "sessions"
            if session_dir.exists():
                logs = sorted(f.stem for f in session_dir.glob("*.yaml") if f.name != ".gitkeep")
                last_session = logs[-1] if logs else "unknown"
            else:
                last_session = "unknown"

        session_count = 0
        session_dir = ROOT / "state" / "sessions"
        if session_dir.exists():
            session_count = len([f for f in session_dir.glob("*.yaml") if f.name != ".gitkeep"])

        journal_count = 0
        journal_dir = ROOT / "journal"
        if journal_dir.exists():
            journal_count = len([f for f in journal_dir.glob("*.md") if f.name != ".gitkeep"])

        snapshot_path = str((ROOT / "state" / ".snapshot").relative_to(ROOT)) + "/"

        # --- Step 3: Confirmation (D-08 type-to-confirm, D-10 --force skips prompt) ---
        if not args.force:
            print(f"\nAbout to erase all progress for: {name or '(unnamed learner — session/journal data present)'}")
            print(f"  Last session: {last_session}")
            print(f"  {session_count} session log(s) will be cleared")
            print(f"  {journal_count} journal entry/entries will be cleared")
            print(f"  Recovery snapshot saved to: {snapshot_path}")
            has_name = bool(name and str(name).strip())
            if has_name:
                print(f'\nType the learner name "{name}" or "RESET" to confirm:')
            else:
                print('\nType "RESET" to confirm:')
            answer = input("> ").strip()
            if not (answer == "RESET" or (has_name and answer == str(name))):
                print("Aborted.")
                sys.exit(0)
        else:
            print(yellow(f"  --force: skipping confirmation for learner '{name}'"))
    else:
        # --- Fresh install path (D-09): no snapshot, no prompt ---
        print(green("No prior learner detected — initializing clean state."))

    # --- Proceed with writes (unchanged from original) ---
    print("\n=== Resetting state files ===")
    for rel_path, content in TEMPLATES.items():
        (ROOT / rel_path).write_text(content, encoding="utf-8")
        print(green(f"  RESET: {rel_path}"))
    reset_skill_map()

    print("\n=== Clearing session data ===")
    total_removed = sum(clear_directory(d) for d in [
        "state/sessions", "state/sessions/archive", "state/summaries",
        "state/milestones", "state/offline-guides", "journal", "progress-reports"])

    print("\n=== Regenerating vault ===")
    vault_script = ROOT / "scripts" / "generate-vault.py"
    vault_failed = False
    if vault_script.exists():
        r = subprocess.run([sys.executable, str(vault_script), "--full"],
                           cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode == 0:
            print(green(f"  {r.stdout.strip()}"))
        else:
            print(red(f"  Vault generation failed: {r.stderr.strip()}"))
            vault_failed = True
    else:
        print(yellow("  SKIP: generate-vault.py not found"))

    print("\n=== Summary ===")
    print(f"  State files reset: {len(TEMPLATES) + 1}")  # +1 for skill-map
    print(f"  Data files removed: {total_removed}")
    if vault_failed:
        print(red("\nState was reset, but vault generation FAILED — run "
                  "`python3 scripts/generate-vault.py --full` and fix the error "
                  "before the first session."))
        sys.exit(1)
    print(green("\nStudent data has been reset to a clean state."))


if __name__ == "__main__":
    main()
