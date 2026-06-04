#!/usr/bin/env python3
"""One-command setup for new users. Initializes learner state and vault."""
import subprocess
import sys
from shared import ROOT, green, yellow, red, bold

SCRIPTS = ROOT / "scripts"



def check_python():
    v = sys.version_info
    if v < (3, 10):
        print(red(f"Python 3.10+ required (found {v.major}.{v.minor}). Install from https://python.org"))
        sys.exit(1)
    print(green(f"  Python {v.major}.{v.minor}.{v.micro}"))


def check_pyyaml():
    try:
        import yaml  # noqa: F401
        print(green("  PyYAML installed"))
    except ImportError:
        print(yellow("  PyYAML not found — installing from requirements.txt..."))
        # Install from requirements.txt so the pin (pyyaml>=6.0,<7) is the single
        # source of truth. Bare `pip install pyyaml` was unpinned and would happily
        # pull in a future incompatible major.
        requirements = ROOT / "requirements.txt"
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements), "-q"]
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(red(f"  Could not auto-install PyYAML ({e})."))
            print(red(f"  Install it manually:  {sys.executable} -m pip install -r {requirements}"))
            sys.exit(1)
        print(green("  PyYAML installed"))


def run_script(name, args=None):
    cmd = [sys.executable, str(SCRIPTS / name)] + (args or [])
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if result.returncode != 0:
        print(red(f"  {name} failed:"))
        print(result.stderr.strip())
        sys.exit(1)
    if result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            print(f"  {line}")
    return result


def configure_git_hooks():
    """Point git's hook path to .githooks/ (idempotent)."""
    try:
        subprocess.run(
            ["git", "config", "core.hooksPath", ".githooks"],
            cwd=str(ROOT), check=True, capture_output=True, text=True,
        )
        print(green("  Git hooks configured (.githooks/)"))
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(yellow("  Could not configure git hooks (is git installed?)"))


# Pristine parking-lot.md contents. Must match TEMPLATES["parking-lot.md"] in
# scripts/init-student.py — the sync is guarded by
# tests/test_setup.py::test_parking_lot_template_matches_init_student.
PARKING_LOT_TEMPLATE = (
    "# Parking Lot — Things I Want to Learn\n\n"
    "Add anything here between sessions. Your tutor will review this at the\n"
    "start of each session and work items into lessons.\n\n"
    "## Urgent (need before an upcoming real-world situation)\n\n\n"
    "## Questions\n\n\n## Words & Phrases I Encountered\n\n\n## Completed\n\n"
)


def _dir_has_file(rel_path: str, suffix: str | None = None) -> bool:
    """True if ROOT/rel_path contains any non-.gitkeep file.

    If `suffix` is given, only files with that extension count.
    """
    d = ROOT / rel_path
    if not d.exists():
        return False
    for f in d.iterdir():
        if not f.is_file() or f.name == ".gitkeep":
            continue
        if suffix is None or f.suffix == suffix:
            return True
    return False


def has_existing_state():
    """Detect whether the repo already holds real learner data.

    Returns True on any of:
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

    init-student.py wipes all of these on reset, so any one of them
    counts as user data that must be preserved. Cheap directory iteration
    runs first; YAML parses are the most expensive checks and run last.
    """
    # Directory-level checks — no file content read.
    if _dir_has_file("state/sessions", ".yaml"):
        return True
    if _dir_has_file("journal", ".md"):
        return True
    if _dir_has_file("state/sessions/archive", ".yaml"):
        return True
    if _dir_has_file("state/summaries", ".yaml"):
        return True
    if _dir_has_file("state/milestones", ".yaml"):
        return True
    if _dir_has_file("progress-reports", ".md"):
        return True
    if _dir_has_file("state/offline-guides"):
        return True

    # Parking lot: compare against pristine template. rstrip so a trailing
    # newline drift between platforms doesn't trigger a false positive.
    parking_lot = ROOT / "parking-lot.md"
    if parking_lot.exists():
        try:
            if parking_lot.read_text(encoding="utf-8").rstrip() != PARKING_LOT_TEMPLATE.rstrip():
                return True
        except OSError:
            pass

    # YAML parses — most expensive checks go last.
    # A1 fail-safe: a parse failure (corrupt-but-present state) must read as
    # "state present" (return True), NOT swallowed into the fall-through
    # `return False`. Otherwise setup proceeds to `init-student --force` and
    # WIPES a recoverable file. Narrow the except to the parse/IO errors we
    # expect and fail safe on them.
    import yaml
    profile_path = ROOT / "state" / "learner-profile.yaml"
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
    # The pristine template has `resources: []`; init-student would wipe
    # anything the learner added.
    rt_path = ROOT / "state" / "resource-tracker.yaml"
    if rt_path.exists():
        try:
            data = yaml.safe_load(rt_path.read_text(encoding="utf-8")) or {}
            if data.get("resources"):
                return True
        except (OSError, yaml.YAMLError):
            # Corrupt or unreadable — refuse to clobber it.
            return True

    return False


def main():
    print(bold("\n=== Spanish Fluency Tutor — Setup ===\n"))

    print("Checking prerequisites...")
    check_python()
    check_pyyaml()

    print("\nInitializing learner state...")
    if has_existing_state():
        print(yellow("  Existing learner state detected — skipping init."))
        print("  Re-running vault generation and validation only.")
        print("  Use `python3 scripts/init-student.py` directly to reset.")
    else:
        run_script("init-student.py", ["--force"])

    print("\nGenerating Obsidian vault...")
    run_script("generate-vault.py", ["--full"])

    print("\nValidating state...")
    run_script("validate-state.py")

    print("\nConfiguring safety hooks...")
    configure_git_hooks()

    print(bold(green("\n=== Setup complete! ===\n")))
    print("Next steps:\n")
    print("  1. Open a terminal in this directory and run:")
    print(bold("     claude\n"))
    print("  2. The tutor will guide you through your first session —")
    print("     it'll ask about your goals, experience, and schedule.\n")
    print("  3. (Optional) Install Obsidian (https://obsidian.md) and open")
    print("     this folder as a vault for a visual progress dashboard.\n")
    print("  4. See STUDENT-GUIDE.md for full details on how the system works.\n")


if __name__ == "__main__":
    main()
