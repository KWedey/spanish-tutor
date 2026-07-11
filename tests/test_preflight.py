"""Tests for scripts/preflight.py go/no-go readiness gate.

scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
Each check shells out via preflight.run(); the tests monkeypatch that single
seam so the summary-string parsing and the main() verdict logic can be exercised
without running the real subprocesses.
"""
import sys

import pytest

import preflight


def _patch_run(monkeypatch, result):
    """Make preflight.run return a fixed (ok, output) tuple for any command."""
    monkeypatch.setattr(preflight, "run", lambda *a, **k: result)


# ---------------------------------------------------------------------------
# 1. check_state_validation — exit code first, then WARN-strict string parse
# ---------------------------------------------------------------------------

class TestStateValidation:
    def test_clean_summary_passes(self, monkeypatch):
        _patch_run(monkeypatch, (True, "--- Summary: 5 passed, 0 warnings, 0 failures ---"))
        ok, detail = preflight.check_state_validation()
        assert ok is True
        assert "0 warnings, 0 failures" in detail

    def test_warning_is_treated_as_failure(self, monkeypatch):
        """A WARN exits 0 but must NOT pass the gate — the summary string
        (1 warnings) is what makes this check strict."""
        _patch_run(monkeypatch, (True, "Summary: 5 passed, 1 warnings, 0 failures"))
        ok, _ = preflight.check_state_validation()
        assert ok is False

    def test_nonzero_exit_fails(self, monkeypatch):
        _patch_run(monkeypatch, (False, "Traceback (most recent call last): ..."))
        ok, detail = preflight.check_state_validation()
        assert ok is False
        assert "Traceback" in detail

    def test_no_summary_line_falls_through_to_exit_code(self, monkeypatch):
        """No 'failures' line present → the check falls back to the exit code."""
        _patch_run(monkeypatch, (True, "unexpected output with no summary"))
        ok, _ = preflight.check_state_validation()
        assert ok is True


# ---------------------------------------------------------------------------
# 2. check_test_suite — gated on pytest's exit code
# ---------------------------------------------------------------------------

class TestTestSuite:
    def test_passing_run(self, monkeypatch):
        _patch_run(monkeypatch, (True, "647 passed in 3.21s"))
        ok, detail = preflight.check_test_suite()
        assert ok is True
        assert "passed" in detail

    def test_failing_run(self, monkeypatch):
        _patch_run(monkeypatch, (False, "1 failed, 646 passed in 3.4s"))
        ok, _ = preflight.check_test_suite()
        assert ok is False


# ---------------------------------------------------------------------------
# 3. check_vault_generation — summary string, with exit-0 fall-through
# ---------------------------------------------------------------------------

class TestVaultGeneration:
    def test_summary_line_passes(self, monkeypatch):
        _patch_run(monkeypatch, (True, "Full generation complete: 80 files written to vault"))
        ok, detail = preflight.check_vault_generation()
        assert ok is True
        assert "files written" in detail

    def test_nonzero_exit_fails(self, monkeypatch):
        _patch_run(monkeypatch, (False, "Traceback: generation crashed"))
        ok, _ = preflight.check_vault_generation()
        assert ok is False

    def test_exit_zero_without_summary_still_passes(self, monkeypatch):
        """Documents the known fall-through: exit 0 with no 'files written' /
        'complete' summary line still returns ok (the false-GO vector noted in
        the audit, partly mitigated by check_obsidian_ready)."""
        _patch_run(monkeypatch, (True, "some unrelated stdout"))
        ok, _ = preflight.check_vault_generation()
        assert ok is True


# ---------------------------------------------------------------------------
# 4. main() verdict, exit code, and skip logic
# ---------------------------------------------------------------------------

def _stub_check(name, result, calls):
    """Build a (name, fn) CHECKS entry that records when it is invoked."""
    def fn():
        calls.append(name)
        return result
    return name, fn


class TestMainVerdict:
    def test_all_pass_exits_zero(self, monkeypatch, capsys):
        calls = []
        monkeypatch.setattr(preflight, "CHECKS", [
            _stub_check("A", (True, "ok"), calls),
            _stub_check("B", (True, "ok"), calls),
        ])
        monkeypatch.setattr(sys, "argv", ["preflight.py"])
        with pytest.raises(SystemExit) as exc:
            preflight.main()
        assert exc.value.code == 0
        assert calls == ["A", "B"]
        assert "GO" in capsys.readouterr().out

    def test_any_failure_exits_one(self, monkeypatch, capsys):
        calls = []
        monkeypatch.setattr(preflight, "CHECKS", [
            _stub_check("A", (True, "ok"), calls),
            _stub_check("B", (False, "boom"), calls),
        ])
        monkeypatch.setattr(sys, "argv", ["preflight.py"])
        with pytest.raises(SystemExit) as exc:
            preflight.main()
        assert exc.value.code == 1
        assert "NO-GO" in capsys.readouterr().out


class TestMainSkipLogic:
    def test_quick_skips_test_suite(self, monkeypatch):
        calls = []
        monkeypatch.setattr(preflight, "CHECKS", [
            _stub_check("Test suite", (True, "ok"), calls),
            _stub_check("Key files exist", (True, "ok"), calls),
        ])
        monkeypatch.setattr(sys, "argv", ["preflight.py", "--quick"])
        with pytest.raises(SystemExit) as exc:
            preflight.main()
        assert exc.value.code == 0
        assert "Test suite" not in calls       # QUICK_SKIP member, not run
        assert "Key files exist" in calls

    def test_fresh_init_skipped_by_default(self, monkeypatch):
        calls = []
        monkeypatch.setattr(preflight, "CHECKS", [
            _stub_check("Fresh init cycle", (True, "ok"), calls),
            _stub_check("Key files exist", (True, "ok"), calls),
        ])
        monkeypatch.setattr(sys, "argv", ["preflight.py"])
        with pytest.raises(SystemExit) as exc:
            preflight.main()
        assert exc.value.code == 0
        assert "Fresh init cycle" not in calls   # destructive; off by default

    def test_fresh_init_runs_with_flag(self, monkeypatch):
        calls = []
        monkeypatch.setattr(preflight, "CHECKS", [
            _stub_check("Fresh init cycle", (True, "ok"), calls),
        ])
        monkeypatch.setattr(sys, "argv", ["preflight.py", "--include-fresh-init"])
        with pytest.raises(SystemExit) as exc:
            preflight.main()
        assert exc.value.code == 0
        assert "Fresh init cycle" in calls
