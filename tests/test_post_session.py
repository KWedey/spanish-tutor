"""Structural tests for scripts/post-session.sh.

Most tests here read the shell script and assert that required patterns are
present, that ordering invariants hold (Step 0 before Step 1), and that
dry-run and failure branches exist.  They do NOT execute the script at
runtime — this mirrors the TestSetupBatExitCode / test_pre_commit_hook
structural-assertion pattern from Phases 1 and 2.

The TestCommitPhaseRollback class at the end is the exception: it executes
the real script against a stubbed temp ROOT to verify the A2 rollback-scope
behavior at runtime.

Requirements covered: ENFORCE-01 (Step 0 snapshot), ENFORCE-09 (transcript FAIL),
A2 (commit-phase failures must not roll back validated state).
"""
import os
import shutil
import subprocess
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
        """Step 0 header line exists in the script (any total step count)."""
        content = _read_script()
        assert "Step 0/" in content and "Snapshotting state before writes" in content, (
            "ENFORCE-01: 'Step 0/N: Snapshotting state before writes' missing"
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
        """Step 0 line must appear before Step 1 line."""
        step0_line = _line_number_of("Step 0/")
        step1_line = _line_number_of("Step 1/")
        assert step0_line > 0, "ENFORCE-01: 'Step 0/' not found"
        assert step1_line > 0, "'Step 1/' not found"
        assert step0_line < step1_line, (
            f"ENFORCE-01: Step 0 (line {step0_line}) must appear before "
            f"Step 1 (line {step1_line})"
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
            if in_failure_block and "Step 1/" in line:
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
        step0_line = _line_number_of("Step 0/")
        step1_line = _line_number_of("Step 1/")
        assert step0_line > 0, "Step 0/ not found"
        assert step1_line > 0, "Step 1/ not found"

        # Check that "Skipping snapshot" appears between Step 0 and Step 1
        skip_line = _line_number_of("Skipping snapshot")
        assert skip_line > 0, "ENFORCE-01: 'Skipping snapshot' not found"
        assert step0_line < skip_line < step1_line, (
            f"ENFORCE-01: 'Skipping snapshot' (line {skip_line}) must be "
            f"between Step 0 (line {step0_line}) and Step 1 (line {step1_line})"
        )

    def test_step_0_not_wrapped_in_run(self):
        """Step 0 must NOT use the run() helper — dry-run must SKIP, not print."""
        lines = _script_lines()
        step0_line = _line_number_of("Step 0/")
        step1_line = _line_number_of("Step 1/")
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
        assert "Step 4.5/" in content, (
            "ENFORCE-09: post-session.sh must have a 'Step 4.5/N' step for transcript check"
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


# ---------------------------------------------------------------------------
# Phase 5 LOAD: Step 5c today_stretch reset (D-04 / Pitfall 3)
# ---------------------------------------------------------------------------


class TestTodayStretchReset:
    """LOAD / D-04 / Pitfall 3: post-session.sh Step 5c resets study_time_budget.today_stretch to 0.

    Uses the Phase 4 quoted-heredoc + sys.argv pattern (CR-01 commits c4139b2, e273529).
    Step 5c must land between Step 5b (recast aggregation) and Step 6 (git commit).
    """

    def test_reset_step_header_present(self):
        assert _line_number_of("Step 5c/") > 0, (
            "LOAD/D-04: post-session.sh must contain a 'Step 5c/' header for today_stretch reset"
        )

    def test_today_stretch_token_present(self):
        script = _read_script()
        assert "today_stretch" in script, (
            "LOAD/D-04: post-session.sh must reference today_stretch somewhere in Step 5c"
        )

    def test_step_5c_after_step_5b(self):
        line_5b = _line_number_of("Step 5b/")
        line_5c = _line_number_of("Step 5c/")
        assert line_5b > 0 and line_5c > 0, "Both Step 5b and Step 5c headers must exist"
        assert line_5b < line_5c, (
            f"Step 5b at line {line_5b} must come before Step 5c at line {line_5c}"
        )

    def test_step_5c_before_step_6(self):
        line_5c = _line_number_of("Step 5c/")
        line_6 = _line_number_of("Step 6/")
        assert line_5c > 0 and line_6 > 0
        assert line_5c < line_6, (
            f"Step 5c (line {line_5c}) must come before Step 6 (line {line_6})"
        )

    def test_uses_quoted_heredoc(self):
        """CR-01: quoted heredoc <<'PYEOF' prevents shell expansion into Python."""
        script = _read_script()
        # There must be at least TWO quoted heredocs — one for 5b (existing), one for 5c (new)
        count = script.count("<<'PYEOF'")
        assert count >= 2, (
            f"CR-01: Step 5c must use quoted heredoc <<'PYEOF' (found {count} total; expected >=2 — one each for 5b and 5c)"
        )

    def test_uses_sys_argv(self):
        """CR-01: dynamic data flows via sys.argv, not shell interpolation."""
        lines = _script_lines()
        step_5c_line = _line_number_of("Step 5c/")
        assert step_5c_line > 0
        block = "\n".join(lines[step_5c_line - 1 : step_5c_line + 40])
        assert "sys.argv" in block, (
            "CR-01: Step 5c Python block must reference sys.argv (not rely on shell interpolation into heredoc)"
        )

    def test_honors_dry_run(self):
        lines = _script_lines()
        step_5c_line = _line_number_of("Step 5c/")
        assert step_5c_line > 0
        block = "\n".join(lines[step_5c_line - 1 : step_5c_line + 30])
        assert "DRY_RUN" in block or "[dry-run]" in block, (
            "Step 5c must honor --dry-run (DRY_RUN branch present)"
        )

    def test_exit_on_failure(self):
        """Step 5c must propagate failure via `if ! python3 ... then error ...; exit 1; fi` pattern."""
        lines = _script_lines()
        step_5c_line = _line_number_of("Step 5c/")
        assert step_5c_line > 0
        block = "\n".join(lines[step_5c_line - 1 : step_5c_line + 60])
        assert "exit 1" in block, (
            "Step 5c Python invocation must fail-fast with exit 1 on error (set -e compliance)"
        )

    def test_step_count_renumbered_to_8(self):
        """After adding Step 5c, all Step N/7 labels must become Step N/8."""
        script = _read_script()
        # Filter out comment-only lines; look for real "/7:" references in step headers/printfs
        real_lines = [l for l in script.splitlines() if not l.lstrip().startswith("#") and "/7:" in l]
        assert not real_lines, (
            f"Step count not renumbered: {len(real_lines)} line(s) still reference /7: {real_lines[:3]}"
        )


# ---------------------------------------------------------------------------
# A2: Commit-phase failures must NOT roll back already-validated state
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    shutil.which("bash") is None or shutil.which("git") is None,
    reason="A2 runtime test requires bash and git",
)
class TestCommitPhaseRollback:
    """A2: runtime behavior of the Step 0 rollback trap.

    The trap must roll back the snapshot when a *pedagogy* step (validate,
    aggregate, recompute, ...) fails, but must NOT roll back when only the
    git commit (Step 6) fails — a VCS-layer error (hook reject, GPG, no
    signing key) should leave the already-validated state on disk.

    These tests run the REAL post-session.sh against a temp ROOT whose
    helper scripts are stubs. snapshot-state.py's `rollback` stub drops a
    ROLLBACK_HAPPENED sentinel so the test can detect whether the trap
    actually rolled back.
    """

    DATE = "2026-04-15"

    def _build_root(self, tmp_path: Path, *, fail_step: str | None) -> Path:
        """Lay out a temp ROOT with a copy of post-session.sh + stub scripts.

        ``fail_step`` names a stub script that should exit 1 to simulate a
        pre-commit-phase failure (e.g. "validate-state.py"); None means every
        pedagogy step succeeds and only the (separately arranged) git commit
        will fail.
        """
        root = tmp_path / "root"
        scripts = root / "scripts"
        scripts.mkdir(parents=True)

        # The real script under test.
        shutil.copy(SCRIPT_PATH, scripts / "post-session.sh")

        # snapshot-state.py stub: snapshot succeeds; rollback drops a sentinel.
        (scripts / "snapshot-state.py").write_text(
            "import sys\n"
            "from pathlib import Path\n"
            "ROOT = Path(__file__).resolve().parent.parent\n"
            "action = sys.argv[1] if len(sys.argv) > 1 else ''\n"
            "if action == 'rollback':\n"
            "    (ROOT / 'ROLLBACK_HAPPENED').write_text('1')\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )

        # All other pedagogy-step stubs: succeed unless this is the fail_step.
        stub_names = [
            "generate-vault.py",
            "archive-sessions.py",
            "validate-state.py",
            "check-session-log.py",
            "recompute-metrics.py",
            "update-fluency-tracking.py",
        ]
        for name in stub_names:
            code = "import sys; sys.exit(1)\n" if name == fail_step else "import sys; sys.exit(0)\n"
            (scripts / name).write_text(code, encoding="utf-8")

        # Minimal valid session log (session_number 1 => transcript is exempt,
        # warns instead of failing). No recasts/schedule => Steps 5b/5c no-op.
        sessions = root / "state" / "sessions"
        sessions.mkdir(parents=True)
        (sessions / f"{self.DATE}.yaml").write_text(
            f"date: {self.DATE}\nsession_number: 1\n", encoding="utf-8"
        )

        # Step 6 runs `git add state/ vault/ transcripts/ progress-reports/
        # journal/`; git errors if a pathspec matches nothing. Create the dirs
        # so `git add` succeeds and the ONLY failure is the rejecting commit hook.
        for d in ("vault", "transcripts", "progress-reports", "journal"):
            (root / d).mkdir(parents=True, exist_ok=True)
            (root / d / ".gitkeep").write_text("", encoding="utf-8")

        # Make ROOT a git repo so Step 6 can stage + attempt a commit.
        env = self._git_env()
        subprocess.run(["git", "init", "-q"], cwd=root, check=True, env=env)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=root, check=True, env=env,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=root, check=True, env=env
        )
        # A failing pre-commit hook isolates the failure to the commit itself.
        hooks = root / ".git" / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        return root

    @staticmethod
    def _git_env() -> dict:
        env = dict(os.environ)
        # Deterministic identity + ignore any global hooksPath override.
        env.setdefault("GIT_CONFIG_NOSYSTEM", "1")
        return env

    def _run(self, root: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(root / "scripts" / "post-session.sh"), self.DATE],
            cwd=root,
            capture_output=True,
            text=True,
            env=self._git_env(),
        )

    def test_commit_failure_does_not_roll_back(self, tmp_path):
        """A2 core: a Step 6 git-commit failure must NOT roll back state."""
        root = self._build_root(tmp_path, fail_step=None)
        result = self._run(root)
        # The script still exits non-zero (the commit genuinely failed)...
        assert result.returncode != 0, (
            "expected non-zero exit from the failed commit; "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )
        # ...but the validated pedagogy state must remain (no rollback).
        assert not (root / "ROLLBACK_HAPPENED").exists(), (
            "A2 regression: a commit-phase failure rolled back already-validated "
            f"state. stdout={result.stdout!r} stderr={result.stderr!r}"
        )

    def test_pre_commit_failure_still_rolls_back(self, tmp_path):
        """A2 guard: a pedagogy-step failure (Step 3) must STILL roll back.

        Ensures the COMMIT_PHASE carve-out did not disable rollback wholesale.
        """
        root = self._build_root(tmp_path, fail_step="validate-state.py")
        result = self._run(root)
        assert result.returncode != 0, "expected non-zero exit from the failed step"
        assert (root / "ROLLBACK_HAPPENED").exists(), (
            "A2 regression: a pre-commit-phase failure did NOT roll back. "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )
