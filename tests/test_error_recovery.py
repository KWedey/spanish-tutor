"""Wire scripts/test-error-recovery.py into pytest collection (H2).

The corruption-stress harness was previously invoked by nothing: its hyphenated
name under scripts/ (not tests/) meant pytest never collected it, so a validator
blind-spot regression would never surface in CI. This thin wrapper parametrizes
over the harness's own SCENARIOS registry — each known corruption scenario must
be caught by validate-state.py. No logic is duplicated here; the corruption
functions and the runner live in the harness.
"""
import importlib

import pytest

# scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
ter = importlib.import_module("test-error-recovery")


@pytest.mark.parametrize(
    "scenario_id,description,corrupt_fn",
    ter.SCENARIOS,
    ids=[s[0] for s in ter.SCENARIOS],
)
def test_validator_catches_corruption(scenario_id, description, corrupt_fn, state_dir):
    """validate-state.py must emit a FAIL/WARN for each known corruption.

    A scenario the validator silently passes is a blind spot — exactly what the
    harness exists to catch, now run on every `pytest` invocation rather than
    never.

    The baseline is conftest's minimal valid ``state_dir`` fixture, not the live
    state/ tree: live learner state is gitignored, so a CI checkout has none of
    it and the harness would otherwise fail to even find a file to corrupt.
    """
    assert ter.run_scenario(scenario_id, description, corrupt_fn, base_state=state_dir), (
        f"Validator blind spot: {scenario_id} — {description}"
    )
