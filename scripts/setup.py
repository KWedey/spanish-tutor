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
# tests/test_setup.py::test_parking_lot_template_matches_init_student. Kept as a
# test-facing mirror (the pristine layout the tests seed against); the live
# drift check runs inside init-student.has_existing_learner_data.
PARKING_LOT_TEMPLATE = (
    "# Parking Lot — Things I Want to Learn\n\n"
    "Add anything here between sessions. Your tutor will review this at the\n"
    "start of each session and work items into lessons.\n\n"
    "## Urgent (need before an upcoming real-world situation)\n\n\n"
    "## Questions\n\n\n## Words & Phrases I Encountered\n\n\n## Completed\n\n"
)


def _load_init_student():
    """Load scripts/init-student.py (dashed filename) as a module.

    scripts/ is on sys.path — that's how `from shared import ...` above
    resolves — so import_module resolves the dashed name directly. Cached in
    sys.modules after the first call.
    """
    import importlib
    return importlib.import_module("init-student")


def has_existing_state():
    """Detect whether the repo already holds real learner data.

    Thin wrapper over the canonical detector,
    init-student.has_existing_learner_data(), so setup and init-student can
    never disagree about what counts as real data — init-student is the script
    that actually wipes it on reset. See that function for the full list of
    signals (session logs, journal, archives, summaries, milestones, progress
    reports, offline guides, parking-lot drift, a populated profile name, and
    resource-tracker entries), plus the corrupt-YAML fail-safe.
    """
    return _load_init_student().has_existing_learner_data(ROOT)


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
