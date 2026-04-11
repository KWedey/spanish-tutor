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
    if v < (3, 6):
        print(red(f"Python 3.6+ required (found {v.major}.{v.minor})"))
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


def main():
    print(bold("\n=== Spanish Fluency Tutor — Setup ===\n"))

    print("Checking prerequisites...")
    check_python()
    check_pyyaml()

    print("\nInitializing learner state...")
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
