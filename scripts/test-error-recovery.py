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
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
VALIDATOR = Path(__file__).resolve().parent / "validate-state.py"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def dump(data: dict, path: Path) -> None:
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))


def copy_state_to_temp(dest: Path, source: Path) -> Path:
    """Copy the *source* state/ tree to *dest* and return *dest*."""
    shutil.copytree(source, dest)
    return dest


def run_validator(state_dir: Path) -> tuple[int, str]:
    """Run validate-state.py against *state_dir*, returning (exit_code, output).

    STATE redirection goes through the TUTOR_STATE_DIR env var (see shared.py),
    so the validator runs as an ordinary subprocess — no import-time patching of
    shared.py, and no fragile inline wrapper to keep working.
    """
    env = {**os.environ, "TUTOR_STATE_DIR": str(state_dir)}
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--verbose"],
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout + result.stderr


def validator_markers(state_dir: Path) -> set[str]:
    """Run the validator against *state_dir* and return its FAIL/WARN markers.

    Volatile temp paths in marker text are normalized to ``<state>`` so the same
    finding compares equal across two different temp copies. A traceback means
    the validator crashed rather than reporting a result — surface it as an error
    instead of silently counting a crash as a caught corruption (the exact blind
    spot a non-zero-exit==caught check used to hide).
    """
    _, output = run_validator(state_dir)
    if "Traceback (most recent call last)" in output:
        raise RuntimeError(f"validate-state.py crashed against {state_dir}:\n{output}")
    sd = str(state_dir)
    return {
        line.replace(sd, "<state>")
        for line in output.splitlines()
        if line.startswith("[FAIL]") or line.startswith("[WARN]")
    }


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

def run_scenario(scenario_id: str, description: str, corrupt_fn,
                 base_state: Path | None = None) -> bool:
    """
    Execute one scenario. Returns True if the corruption introduced a NEW
    validator FAIL/WARN that the clean baseline did not already emit.

    Diffing against a clean copy — rather than asserting "any FAIL/WARN
    appeared" — keeps the test honest even when the baseline itself carries
    pre-existing markers: only a marker the corruption *adds* counts as caught.

    *base_state* selects the baseline to corrupt. Tests pass a committed minimal
    state because CI has no live learner state (state/*.yaml is gitignored); the
    standalone CLI defaults to the live state/ tree. Each scenario works on its
    own temp copies — live state is never touched — and the temp directory is
    cleaned up automatically when the context manager exits.
    """
    source = base_state if base_state is not None else STATE
    with tempfile.TemporaryDirectory(prefix="lang-state-test-") as tmp_str:
        tmp = Path(tmp_str)
        try:
            baseline = validator_markers(copy_state_to_temp(tmp / "clean", source))
            dirty = copy_state_to_temp(tmp / "dirty", source)
            corrupt_fn(dirty)
            caught = bool(validator_markers(dirty) - baseline)
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
