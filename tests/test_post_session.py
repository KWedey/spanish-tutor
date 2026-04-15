"""Regression tests for scripts/post-session.sh (Phase 3 ENFORCE).

These tests read the post-session.sh script file and assert that required
structural patterns are present. They do NOT execute the script — this mirrors
the structural-assertion pattern from tests/test_pre_commit_hook.py.

Requirements covered: ENFORCE-01 (Step 0 snapshot), ENFORCE-09 (transcript FAIL).
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POST_SESSION = REPO_ROOT / "scripts" / "post-session.sh"


def _read_script() -> str:
    assert POST_SESSION.exists(), (
        f"post-session.sh missing at {POST_SESSION} — required by Phase 3 ENFORCE."
    )
    return POST_SESSION.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# ENFORCE-01: Step 0 invokes snapshot-state.py before any other step
# ---------------------------------------------------------------------------

class TestStep0Snapshot:
    def test_step_0_invokes_snapshot_state(self):
        """ENFORCE-01: post-session.sh must have a Step 0/6 that runs snapshot-state.py."""
        content = _read_script()
        assert "snapshot-state.py" in content, (
            "ENFORCE-01: post-session.sh must invoke snapshot-state.py"
        )
        assert "Step 0/6" in content, (
            "ENFORCE-01: post-session.sh must have a 'Step 0/6' step that runs snapshot-state.py"
        )

    def test_step_0_comes_before_step_1(self):
        """ENFORCE-01: Step 0/6 must appear before Step 1/6 in the script."""
        content = _read_script()
        assert "Step 0/6" in content, (
            "ENFORCE-01: 'Step 0/6' not found in post-session.sh"
        )
        assert content.index("Step 0/6") < content.index("Step 1/6"), (
            "ENFORCE-01: Step 0/6 must appear before Step 1/6 — "
            "snapshot must run before any other post-session step"
        )


# ---------------------------------------------------------------------------
# ENFORCE-01: Step 0 snapshot failure aborts the script
# ---------------------------------------------------------------------------

class TestStep0SnapshotFail:
    def test_snapshot_failure_aborts(self):
        """ENFORCE-01: snapshot failure in Step 0 must trigger exit 1."""
        content = _read_script()
        # Isolate the Step 0 region (everything before Step 1/6)
        assert "Step 1/6" in content, (
            "ENFORCE-01: 'Step 1/6' not found — cannot isolate Step 0 region"
        )
        step0_region = content.split("Step 1/6")[0]
        assert "Snapshot failed" in step0_region, (
            "ENFORCE-01: Step 0 region must contain 'Snapshot failed' error message"
        )
        assert "exit 1" in step0_region, (
            "ENFORCE-01: Step 0 region must contain 'exit 1' to abort on snapshot failure"
        )


# ---------------------------------------------------------------------------
# ENFORCE-01: Step 0 dry-run skips snapshot entirely
# ---------------------------------------------------------------------------

class TestStep0DryRun:
    def test_dry_run_skips_snapshot(self):
        """ENFORCE-01: dry-run mode must skip snapshot, not just print it."""
        content = _read_script()
        assert "Step 1/6" in content, (
            "ENFORCE-01: 'Step 1/6' not found — cannot isolate Step 0 region"
        )
        step0_region = content.split("Step 1/6")[0]
        assert "[dry-run]" in step0_region, (
            "ENFORCE-01: Step 0 region must contain '[dry-run]' marker for skip path"
        )
        assert "Skipping snapshot" in step0_region, (
            "ENFORCE-01: Step 0 dry-run path must contain 'Skipping snapshot' message"
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
