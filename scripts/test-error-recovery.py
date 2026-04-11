#!/usr/bin/env python3
"""
Stress-test validate-state.py against known corruption scenarios.

For each scenario:
  1. Copy the entire state/ directory to a temp location (never touch live state).
  2. Apply a targeted corruption to the temp copy.
  3. Run validate-state.py against the temp copy and capture stdout/exit code.
  4. Assert the validator emitted at least one [FAIL] or [WARN] line.
  5. Temp directory is cleaned up automatically.

Exit 0 — all scenarios were caught by the validator.
Exit 1 — at least one scenario was NOT caught (validator blind spot).
"""
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
VALIDATOR = Path(__file__).resolve().parent / "validate-state.py"
SCRIPTS_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def dump(data: dict, path: Path) -> None:
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))


def copy_state_to_temp(tmp: Path) -> Path:
    """Copy the entire state/ tree to tmp/state/ and return the new state path."""
    dest = tmp / "state"
    shutil.copytree(STATE, dest)
    return dest


def run_validator(state_dir: Path) -> tuple[int, str]:
    """Run validate-state.py against *state_dir* via TUTOR_STATE_DIR env override.

    The validator imports STATE_DIR from shared.py which is hardcoded.
    To redirect it to the temp copy without modifying shared.py, we run a
    thin wrapper script that patches shared.STATE_DIR before importing the
    validator module.
    """
    # Build a small wrapper that patches the state path before running the
    # validator's main(). This avoids modifying shared.py (owned by another agent).
    wrapper = textwrap.dedent(f"""\
        import sys, importlib
        from pathlib import Path

        # Patch shared.STATE_DIR before validate-state.py imports it
        sys.path.insert(0, {str(SCRIPTS_DIR)!r})
        import shared
        shared.STATE_DIR = Path({str(state_dir)!r})

        # Now import and run the validator
        spec = importlib.util.spec_from_file_location("validate_state", {str(VALIDATOR)!r})
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()
    """)
    result = subprocess.run(
        [sys.executable, "-c", wrapper, "--verbose"],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout + result.stderr


def validator_caught(output: str, exit_code: int) -> bool:
    """Return True if the validator signalled at least one FAIL or WARN."""
    return exit_code != 0 or "[FAIL]" in output or "[WARN]" in output


# ---------------------------------------------------------------------------
# Corruption functions
# Each accepts a state_dir Path pointing to the TEMP copy of state/.
# Mutations are applied only to temp files — live state is never touched.
# ---------------------------------------------------------------------------

def corrupt_bad_yaml(state_dir: Path) -> None:
    """Inject a raw unmatched bracket that breaks YAML parsing."""
    path = state_dir / "skill-map.yaml"
    original = path.read_text()
    path.write_text(original + "\nunmatched: [\n")


def corrupt_missing_field(state_dir: Path) -> None:
    """Remove the required 'current_phase' key from schedule.yaml."""
    path = state_dir / "schedule.yaml"
    data = load(path)
    data.pop("current_phase", None)
    dump(data, path)


def corrupt_bad_enum(state_dir: Path) -> None:
    """Set fluency_accuracy_balance to a value outside the allowed enum."""
    path = state_dir / "schedule.yaml"
    data = load(path)
    data["fluency_accuracy_balance"] = "invalid-value"
    dump(data, path)


def corrupt_orphan_carryover(state_dir: Path) -> None:
    """Add a concept ID that does not exist in skill-map to carryover_concepts."""
    path = state_dir / "schedule.yaml"
    data = load(path)
    carryover = list(data.get("carryover_concepts") or [])
    carryover.append("A-99-nonexistent-concept")
    data["carryover_concepts"] = carryover
    dump(data, path)


def corrupt_bad_integration_ref(state_dir: Path) -> None:
    """Add an invalid concept ID to integration_tested_with on the first grammar entry."""
    path = state_dir / "skill-map.yaml"
    data = load(path)
    grammar = data.get("grammar", {})
    if not grammar:
        raise RuntimeError("skill-map grammar section is empty — cannot apply corruption")
    first_key = next(iter(grammar))
    entry = grammar[first_key]
    if not isinstance(entry, dict):
        raise RuntimeError(f"Grammar entry '{first_key}' is not a dict")
    refs = list(entry.get("integration_tested_with") or [])
    refs.append("Z-99-phantom-concept")
    entry["integration_tested_with"] = refs
    dump(data, path)


def corrupt_vocab_passive_lt_active(state_dir: Path) -> None:
    """Set active_known > passive_known in the first vocabulary cluster."""
    path = state_dir / "skill-map.yaml"
    data = load(path)
    vocab = data.get("vocabulary", {})
    if not vocab:
        raise RuntimeError("skill-map vocabulary section is empty — cannot apply corruption")
    first_key = next(iter(vocab))
    entry = vocab[first_key]
    if not isinstance(entry, dict):
        raise RuntimeError(f"Vocabulary entry '{first_key}' is not a dict")
    entry["passive_known"] = 2
    entry["active_known"] = 10  # active > passive — violation
    dump(data, path)


def corrupt_bad_performance_enum(state_dir: Path) -> None:
    """Set performance_scaffolded to 'excellent' — not in the allowed set."""
    path = state_dir / "skill-map.yaml"
    data = load(path)
    grammar = data.get("grammar", {})
    if not grammar:
        raise RuntimeError("skill-map grammar section is empty — cannot apply corruption")
    first_key = next(iter(grammar))
    entry = grammar[first_key]
    if not isinstance(entry, dict):
        raise RuntimeError(f"Grammar entry '{first_key}' is not a dict")
    entry["performance_scaffolded"] = "excellent"
    dump(data, path)


def corrupt_validation_no_onboarding(state_dir: Path) -> None:
    """Set placement_validation.active=true while onboarding_complete=false."""
    path = state_dir / "schedule.yaml"
    data = load(path)
    data["onboarding_complete"] = False
    pv = data.get("placement_validation") or {}
    pv["active"] = True
    data["placement_validation"] = pv
    dump(data, path)


# ---------------------------------------------------------------------------
# Scenario registry
# Each entry: (scenario_id, human_description, corrupt_fn)
# ---------------------------------------------------------------------------

SCENARIOS: list[tuple[str, str, object]] = [
    ("bad_yaml",                 "Inject invalid YAML into skill-map.yaml",                   corrupt_bad_yaml),
    ("missing_field",            "Remove 'current_phase' from schedule.yaml",                 corrupt_missing_field),
    ("bad_enum",                 "Set fluency_accuracy_balance to 'invalid-value'",           corrupt_bad_enum),
    ("orphan_carryover",         "Add nonexistent concept to carryover_concepts",             corrupt_orphan_carryover),
    ("bad_integration_ref",      "Add invalid concept ID to integration_tested_with",         corrupt_bad_integration_ref),
    ("vocab_passive_lt_active",  "Set active_known > passive_known in a vocab cluster",       corrupt_vocab_passive_lt_active),
    ("bad_performance_enum",     "Set performance_scaffolded to 'excellent'",                 corrupt_bad_performance_enum),
    ("validation_no_onboarding", "Set placement_validation.active=true, onboarding_complete=false",
                                                                                               corrupt_validation_no_onboarding),
]

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_scenario(scenario_id: str, description: str, corrupt_fn) -> bool:
    """
    Execute one scenario. Returns True if the validator caught the corruption.

    Each scenario gets its own temp copy of state/ — live state is never touched.
    The temp directory is cleaned up automatically when the context manager exits.
    """
    with tempfile.TemporaryDirectory(prefix="lang-state-test-") as tmp_str:
        tmp = Path(tmp_str)
        try:
            temp_state = copy_state_to_temp(tmp)
            corrupt_fn(temp_state)
            exit_code, output = run_validator(temp_state)
            caught = validator_caught(output, exit_code)
        except Exception as exc:
            print(f"[ERROR] {scenario_id}: raised an exception: {exc}")
            return False

    if caught:
        print(f"[PASS] {scenario_id}: Validator correctly detected — {description}")
    else:
        print(f"[FAIL] {scenario_id}: Validator did NOT catch — {description}")

    return caught


def main() -> None:
    if not VALIDATOR.exists():
        print(f"ERROR: validate-state.py not found at {VALIDATOR}", file=sys.stderr)
        sys.exit(2)

    if not STATE.is_dir():
        print(f"ERROR: state/ directory not found at {STATE}", file=sys.stderr)
        sys.exit(2)

    print(f"Running {len(SCENARIOS)} corruption scenarios against validate-state.py\n")

    results = []
    for scenario_id, description, corrupt_fn in SCENARIOS:
        caught = run_scenario(scenario_id, description, corrupt_fn)
        results.append((scenario_id, caught))

    total = len(results)
    caught_count = sum(1 for _, ok in results if ok)
    missed = [sid for sid, ok in results if not ok]

    print(f"\n--- Summary: {caught_count}/{total} scenarios caught ---")

    if missed:
        print(f"\nValidator blind spots ({len(missed)}):")
        for sid in missed:
            print(f"  - {sid}")
        sys.exit(1)
    else:
        print("All scenarios correctly detected by the validator.")
        sys.exit(0)


if __name__ == "__main__":
    main()
