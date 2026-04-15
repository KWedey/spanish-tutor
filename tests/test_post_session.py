"""Structural tests for scripts/post-session.sh.

These tests read the shell script and assert that required patterns are
present, that ordering invariants hold (Step 0 before Step 1), and that
dry-run and failure branches exist.  They do NOT execute the script at
runtime — this mirrors the TestSetupBatExitCode / test_pre_commit_hook
structural-assertion pattern from Phases 1 and 2.

Requirements covered: ENFORCE-01 (Step 0 snapshot), ENFORCE-09 (transcript FAIL).
"""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "post-session.sh"


def _read_script() -> str:
    assert SCRIPT_PATH.exists(), (
        f"post-session.sh missing at {SCRIPT_PATH} — "
        "it must exist per the project's post-session automation."
    )
    return SCRIPT_PATH.read_text(encoding="utf-8")


def _script_lines() -> list[str]:
    return _read_script().splitlines()


def _line_number_of(token: str) -> int:
    """Return 1-based line number of the first line containing token, or -1."""
    for i, line in enumerate(_script_lines(), start=1):
        if token in line:
            return i
    return -1


# ---------------------------------------------------------------------------
# ENFORCE-01: Step 0 invokes snapshot-state.py
# ---------------------------------------------------------------------------

class TestStep0Snapshot:
    """ENFORCE-01: post-session.sh must call snapshot-state.py as Step 0."""

    def test_step_0_header_present(self):
        """Step 0/6 header line exists in the script."""
        content = _read_script()
        assert "Step 0/6: Snapshotting state before writes" in content, (
            "ENFORCE-01: 'Step 0/6: Snapshotting state before writes' missing"
        )

    def test_step_0_invokes_snapshot_state(self):
        """Step 0 block invokes snapshot-state.py."""
        content = _read_script()
        assert "snapshot-state.py" in content, (
            "ENFORCE-01: 'snapshot-state.py' not referenced in post-session.sh"
        )
        # Verify it's an invocation, not just a comment
        lines = _script_lines()
        invocation_lines = [
            l for l in lines
            if "snapshot-state.py" in l and not l.strip().startswith("#")
        ]
        assert invocation_lines, (
            "ENFORCE-01: snapshot-state.py appears only in comments, not as an invocation"
        )

    def test_step_0_comes_before_step_1(self):
        """Step 0/6 line must appear before Step 1/6 line."""
        step0_line = _line_number_of("Step 0/6:")
        step1_line = _line_number_of("Step 1/6:")
        assert step0_line > 0, "ENFORCE-01: 'Step 0/6:' not found"
        assert step1_line > 0, "'Step 1/6:' not found"
        assert step0_line < step1_line, (
            f"ENFORCE-01: Step 0/6 (line {step0_line}) must appear before "
            f"Step 1/6 (line {step1_line})"
        )


# ---------------------------------------------------------------------------
# ENFORCE-01: Step 0 snapshot failure aborts
# ---------------------------------------------------------------------------

class TestStep0SnapshotFail:
    """ENFORCE-01: snapshot failure must abort post-session.sh."""

    def test_snapshot_failure_aborts(self):
        """The script must contain 'Snapshot failed' error and exit on failure."""
        content = _read_script()
        assert "Snapshot failed" in content, (
            "ENFORCE-01: 'Snapshot failed' error message missing from post-session.sh"
        )

    def test_state_not_modified_message(self):
        """The failure message must state that state was not modified."""
        content = _read_script()
        assert "State was not modified" in content, (
            "ENFORCE-01: 'State was not modified' message missing from failure branch"
        )

    def test_exit_after_snapshot_failure(self):
        """There must be an exit 1 in the snapshot failure branch."""
        lines = _script_lines()
        # Find the block between "Snapshot failed" and the next step/section
        in_failure_block = False
        found_exit = False
        for line in lines:
            if "Snapshot failed" in line:
                in_failure_block = True
            if in_failure_block and "exit 1" in line:
                found_exit = True
                break
            # Stop scanning if we hit the next step
            if in_failure_block and "Step 1/6:" in line:
                break
        assert found_exit, (
            "ENFORCE-01: 'exit 1' not found after 'Snapshot failed' error"
        )


# ---------------------------------------------------------------------------
# ENFORCE-01: Dry-run skips snapshot
# ---------------------------------------------------------------------------

class TestStep0DryRun:
    """ENFORCE-01: --dry-run must skip snapshot entirely (not 'Would run')."""

    def test_dry_run_skips_snapshot(self):
        """The Step 0 block must contain '[dry-run]' and 'Skipping snapshot'."""
        content = _read_script()
        assert "Skipping snapshot" in content, (
            "ENFORCE-01: 'Skipping snapshot' message missing from dry-run branch"
        )

    def test_dry_run_branch_in_step_0_region(self):
        """The dry-run skip must be in the Step 0 region (before Step 1)."""
        lines = _script_lines()
        step0_line = _line_number_of("Step 0/6:")
        step1_line = _line_number_of("Step 1/6:")
        assert step0_line > 0, "Step 0/6: not found"
        assert step1_line > 0, "Step 1/6: not found"

        # Check that "Skipping snapshot" appears between Step 0 and Step 1
        skip_line = _line_number_of("Skipping snapshot")
        assert skip_line > 0, "ENFORCE-01: 'Skipping snapshot' not found"
        assert step0_line < skip_line < step1_line, (
            f"ENFORCE-01: 'Skipping snapshot' (line {skip_line}) must be "
            f"between Step 0/6 (line {step0_line}) and Step 1/6 (line {step1_line})"
        )

    def test_step_0_not_wrapped_in_run(self):
        """Step 0 must NOT use the run() helper — dry-run must SKIP, not print."""
        lines = _script_lines()
        step0_line = _line_number_of("Step 0/6:")
        step1_line = _line_number_of("Step 1/6:")
        assert step0_line > 0 and step1_line > 0

        # Extract the Step 0 block
        step0_block = lines[step0_line - 1:step1_line - 1]
        for line in step0_block:
            stripped = line.strip()
            # The run() helper pattern is: run python3 ...
            assert not stripped.startswith("run "), (
                f"ENFORCE-01: Step 0 must not use run() helper. Found: '{stripped}'"
            )


# ---------------------------------------------------------------------------
# ENFORCE-09: Transcript FAIL check (Step 4.5)
# ---------------------------------------------------------------------------

class TestTranscriptFail:
    def test_transcript_fail_block_present(self):
        """ENFORCE-09: post-session.sh must check for transcripts/$DATE.md."""
        content = _read_script()
        assert "transcripts/$DATE.md" in content, (
            "ENFORCE-09: post-session.sh must check for transcripts/$DATE.md"
        )
        assert "Step 4.5/6" in content, (
            "ENFORCE-09: post-session.sh must have a 'Step 4.5/6' step for transcript check"
        )

    def test_transcript_fail_gated_on_session_number(self):
        """ENFORCE-09: transcript FAIL must be gated on SESSION_NUMBER > 1."""
        content = _read_script()
        assert "SESSION_NUMBER" in content, (
            "ENFORCE-09: post-session.sh must read SESSION_NUMBER from the session log"
        )
        # Find the region containing SESSION_NUMBER and verify it gates on > 1
        # and includes exit 1
        lines = content.splitlines()
        session_number_region = []
        for i, line in enumerate(lines):
            if "SESSION_NUMBER" in line:
                # Grab surrounding context (10 lines before and after)
                start = max(0, i - 10)
                end = min(len(lines), i + 10)
                session_number_region.extend(lines[start:end])
        region_text = "\n".join(session_number_region)
        assert "-gt 1" in region_text, (
            "ENFORCE-09: SESSION_NUMBER region must contain '-gt 1' gate "
            "(only fail for session_number > 1)"
        )
        assert "exit 1" in region_text, (
            "ENFORCE-09: SESSION_NUMBER region must contain 'exit 1' "
            "(transcript absence after session 1 is a hard failure)"
        )


# ---------------------------------------------------------------------------
# ENFORCE-09: Session 1 warns instead of failing for missing transcript
# ---------------------------------------------------------------------------

class TestTranscriptWarn:
    def test_session_1_warns_not_fails(self):
        """ENFORCE-09: session 1 must warn about missing transcript, not fail."""
        content = _read_script()
        assert "session 1 — exempt" in content, (
            "ENFORCE-09: post-session.sh must contain 'session 1 — exempt' "
            "message for first-session transcript leniency"
        )
        assert 'warn "Transcript file not found' in content, (
            "ENFORCE-09: post-session.sh must warn (not error) about missing "
            "transcript for session 1"
        )
