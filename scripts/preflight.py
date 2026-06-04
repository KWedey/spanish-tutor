#!/usr/bin/env python3
"""Pre-flight check: verify the tutoring system is ready for a new user.

Runs a sequence of checks and reports go/no-go:
  1. State validation  — all state files parse and pass cross-checks
  2. Key files exist   — critical curriculum/state/schema files present
  3. Test suite        — all pytest tests pass
  4. Vault generation  — Obsidian vault builds without errors
  5. Obsidian ready    — vault is browsable (Home, Getting Started, .obsidianignore)
  6. Fresh init        — (opt-in, DESTRUCTIVE) init + validate run end-to-end; RESETS
                         real state, so it is OFF unless --include-fresh-init

Usage:
    python3 scripts/preflight.py                      # safe, non-destructive
    python3 scripts/preflight.py --quick              # also skip the slow test suite
    python3 scripts/preflight.py --include-fresh-init # fresh clones only — RESETS state
"""
import argparse
import subprocess
import sys

from shared import ROOT, VAULT_DIR, green, red, yellow, bold, dim



def run(cmd: list[str], label: str, *, capture: bool = True) -> tuple[bool, str]:
    """Run a subprocess and return (success, output)."""
    try:
        r = subprocess.run(
            cmd, cwd=str(ROOT), capture_output=capture, text=True, timeout=120,
        )
        output = (r.stdout + r.stderr).strip()
        return r.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"{label} timed out after 120s"
    except FileNotFoundError as e:
        return False, f"Command not found: {e}"


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_state_validation() -> tuple[bool, str]:
    """Check 1: validate-state.py passes with 0 warnings, 0 failures."""
    ok, out = run([sys.executable, "scripts/validate-state.py"], "state validation")
    if not ok:
        return False, out
    # Parse summary line
    for line in out.splitlines():
        if "failures" in line.lower():
            if "0 warnings, 0 failures" in line:
                return True, line.strip()
            return False, line.strip()
    return ok, out


def check_test_suite() -> tuple[bool, str]:
    """Check 2: pytest passes."""
    ok, out = run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line"],
        "test suite",
    )
    if not ok:
        # Show last few lines for context
        lines = out.strip().splitlines()
        return False, "\n".join(lines[-10:])
    for line in out.splitlines():
        if "passed" in line:
            return True, line.strip()
    return ok, out.splitlines()[-1] if out else "(no output)"


def check_vault_generation() -> tuple[bool, str]:
    """Check 3: generate-vault.py --full succeeds."""
    ok, out = run(
        [sys.executable, "scripts/generate-vault.py", "--full"],
        "vault generation",
    )
    if not ok:
        return False, out
    for line in out.splitlines():
        if "files written" in line.lower() or "complete" in line.lower():
            return True, line.strip()
    return ok, out.splitlines()[-1] if out else "(no output)"


def check_fresh_init() -> tuple[bool, str]:
    """Opt-in, DESTRUCTIVE: verify init-student.py + validate-state.py run cleanly
    end-to-end.

    WARNING: this runs `init-student.py --force` against the REAL repo — it resets
    every state/ file to a blank template and clears journal/ and progress-reports/.
    A recovery snapshot of state/ is taken first, but journal/ and progress-reports/
    are NOT snapshotted. Run ONLY on a fresh clone, before the first session. It is
    OFF by default and runs only with --include-fresh-init (the earlier version
    silently wiped real learner state despite a docstring claiming otherwise — audit
    P1-7)."""
    ok, out = run(
        [sys.executable, "scripts/init-student.py", "--force"],
        "fresh init",
    )
    if not ok:
        return False, out
    ok2, out2 = run(
        [sys.executable, "scripts/validate-state.py"],
        "post-init validation",
    )
    if not ok2:
        return False, f"Init succeeded but validation failed:\n{out2}"
    return True, "init + validation passed"


def check_key_files_exist() -> tuple[bool, str]:
    """Check 5: critical files exist and are non-empty."""
    critical = [
        "CLAUDE.md",
        "STUDENT-GUIDE.md",
        "SETUP.md",
        "curriculum/tutor-guides/first-session.md",
        "curriculum/tutor-guides/decision-engine.md",
        "curriculum/tutor-guides/onboarding-guide.md",
        "curriculum/l1-interference.yaml",
        "state/skill-map.yaml",
        "state/schedule.yaml",
        "state/learner-profile.yaml",
        "state/system-health.yaml",
        "state/resource-tracker.yaml",
        "schemas/session-log.schema.yaml",
    ]
    missing = []
    empty = []
    for rel in critical:
        p = ROOT / rel
        if not p.exists():
            missing.append(rel)
        elif p.stat().st_size == 0:
            empty.append(rel)

    issues = []
    if missing:
        issues.append(f"Missing: {', '.join(missing)}")
    if empty:
        issues.append(f"Empty: {', '.join(empty)}")
    if issues:
        return False, "; ".join(issues)
    return True, f"{len(critical)} critical files present"


def check_obsidian_ready() -> tuple[bool, str]:
    """Check 6: Obsidian vault is browsable."""
    issues = []
    if not VAULT_DIR.exists():
        return False, "vault/ directory does not exist"

    # Check .obsidianignore exists
    ignore = ROOT / ".obsidianignore"
    if not ignore.exists():
        issues.append(".obsidianignore missing — system dirs visible to learner")

    # Check Home.md exists
    home = VAULT_DIR / "Home.md"
    if not home.exists():
        issues.append("vault/Home.md missing")

    # Check Getting Started exists
    gs = VAULT_DIR / "Getting Started.md"
    if not gs.exists():
        issues.append("vault/Getting Started.md missing")

    # Count vault files
    vault_files = list(VAULT_DIR.rglob("*.md"))
    if len(vault_files) < 10:
        issues.append(f"Only {len(vault_files)} vault files (expected 70+)")

    if issues:
        return False, "; ".join(issues)
    return True, f"{len(vault_files)} vault files, Home + Getting Started present"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

CHECKS = [
    ("State validation", check_state_validation),
    ("Key files exist", check_key_files_exist),
    ("Test suite", check_test_suite),
    ("Vault generation", check_vault_generation),
    ("Obsidian ready", check_obsidian_ready),
    ("Fresh init cycle", check_fresh_init),
]

QUICK_SKIP = {"Test suite", "Fresh init cycle"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-flight check for tutoring system.")
    parser.add_argument("--quick", action="store_true", help="Skip test suite and init cycle")
    parser.add_argument("--include-fresh-init", action="store_true",
                        help="Run the DESTRUCTIVE fresh-init check (RESETS real state; fresh clones only)")
    args = parser.parse_args()

    print(bold("\n=== Pre-flight Check ===\n"))

    passed = 0
    failed = 0
    skipped = 0

    for name, fn in CHECKS:
        if args.quick and name in QUICK_SKIP:
            print(f"  {yellow('SKIP')}  {name}")
            skipped += 1
            continue
        if name == "Fresh init cycle" and not args.include_fresh_init:
            print(f"  {yellow('SKIP')}  {name}  {dim('— destructive; use --include-fresh-init on a fresh clone')}")
            skipped += 1
            continue
        if name == "Fresh init cycle":
            print(f"  {red('WARNING')}  {name} RESETS real state (--include-fresh-init)")

        ok, detail = fn()
        status = green("PASS") if ok else red("FAIL")
        print(f"  {status}  {name}  {dim('— ' + detail)}")

        if ok:
            passed += 1
        else:
            failed += 1

    # Verdict
    print()
    if failed == 0:
        print(green(bold(f"  GO  — {passed} passed, {skipped} skipped\n")))
        sys.exit(0)
    else:
        print(red(bold(f"  NO-GO  — {failed} failed, {passed} passed, {skipped} skipped\n")))
        sys.exit(1)


if __name__ == "__main__":
    main()
