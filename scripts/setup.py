#!/usr/bin/env python3
"""One-command setup for new users. Initializes learner state and vault."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

_C = sys.stdout.isatty()
green = lambda t: f"\033[32m{t}\033[0m" if _C else t
yellow = lambda t: f"\033[33m{t}\033[0m" if _C else t
red = lambda t: f"\033[31m{t}\033[0m" if _C else t
bold = lambda t: f"\033[1m{t}\033[0m" if _C else t


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
        print(yellow("  PyYAML not found — installing..."))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
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


def _dir_has_file(rel_path: str, suffix: str) -> bool:
    """True if ROOT/rel_path contains any non-.gitkeep file with the given suffix."""
    d = ROOT / rel_path
    if not d.exists():
        return False
    for f in d.iterdir():
        if not f.is_file() or f.name == ".gitkeep":
            continue
        if f.suffix == suffix:
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
      - parking-lot.md modified from its pristine template
      - state/learner-profile.yaml with a populated name

    init-student.py wipes all of these directories on reset, so any one of
    them counts as user data that must be preserved. Cheap directory
    iteration runs first; the YAML parse is the most expensive check and
    runs last.
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

    # Parking lot: compare against pristine template. rstrip so a trailing
    # newline drift between platforms doesn't trigger a false positive.
    parking_lot = ROOT / "parking-lot.md"
    if parking_lot.exists():
        try:
            if parking_lot.read_text(encoding="utf-8").rstrip() != PARKING_LOT_TEMPLATE.rstrip():
                return True
        except OSError:
            pass

    # Profile: most expensive check (YAML parse) — runs last.
    profile_path = ROOT / "state" / "learner-profile.yaml"
    if profile_path.exists():
        try:
            import yaml
            data = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
            name = data.get("name")
            if name and str(name).strip():
                return True
        except Exception:
            pass

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
    result = run_script("validate-state.py")

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
