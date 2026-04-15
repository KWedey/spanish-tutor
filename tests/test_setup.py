"""Tests for scripts/setup.py — specifically has_existing_state()."""
import ast
import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _load_setup_module():
    """Load scripts/setup.py as a module despite the dashless name.

    We use importlib directly because `setup.py` is not a conventional
    package module (it sits alongside init-student.py, which has a dash
    in its filename and can't be imported by normal `import` either).
    """
    spec = importlib.util.spec_from_file_location(
        "setup_module", SCRIPTS_DIR / "setup.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def setup_module():
    return _load_setup_module()


def _seed_pristine(root: Path, setup_module) -> None:
    """Create a pristine install layout matching what init-student.py produces.

    All state directories exist, parking-lot.md matches the tracked template,
    learner-profile.yaml has a blank name. has_existing_state() must return
    False against this layout.
    """
    (root / "state").mkdir(exist_ok=True)
    (root / "state" / "sessions").mkdir(exist_ok=True)
    (root / "state" / "sessions" / "archive").mkdir(exist_ok=True)
    (root / "state" / "summaries").mkdir(exist_ok=True)
    (root / "state" / "milestones").mkdir(exist_ok=True)
    (root / "state" / "offline-guides").mkdir(exist_ok=True)
    (root / "journal").mkdir(exist_ok=True)
    (root / "progress-reports").mkdir(exist_ok=True)

    for rel in (
        "state/sessions/.gitkeep",
        "state/sessions/archive/.gitkeep",
        "state/summaries/.gitkeep",
        "state/milestones/.gitkeep",
        "state/offline-guides/.gitkeep",
        "journal/.gitkeep",
        "progress-reports/.gitkeep",
    ):
        (root / rel).write_text("", encoding="utf-8")

    (root / "parking-lot.md").write_text(
        setup_module.PARKING_LOT_TEMPLATE, encoding="utf-8"
    )
    (root / "state" / "learner-profile.yaml").write_text(
        "name: \"\"\n", encoding="utf-8"
    )
    (root / "state" / "resource-tracker.yaml").write_text(
        "schema_version: 1\nresources: []\n", encoding="utf-8"
    )


class TestHasExistingState:
    def test_pristine_template_returns_false(self, tmp_path, monkeypatch, setup_module):
        _seed_pristine(tmp_path, setup_module)
        monkeypatch.setattr(setup_module, "ROOT", tmp_path)
        assert setup_module.has_existing_state() is False

    def test_populated_name_returns_true(self, tmp_path, monkeypatch, setup_module):
        _seed_pristine(tmp_path, setup_module)
        (tmp_path / "state" / "learner-profile.yaml").write_text(
            "name: Alice\n", encoding="utf-8"
        )
        monkeypatch.setattr(setup_module, "ROOT", tmp_path)
        assert setup_module.has_existing_state() is True

    def test_session_log_returns_true(self, tmp_path, monkeypatch, setup_module):
        _seed_pristine(tmp_path, setup_module)
        (tmp_path / "state" / "sessions" / "2026-04-10.yaml").write_text(
            "date: 2026-04-10\n", encoding="utf-8"
        )
        monkeypatch.setattr(setup_module, "ROOT", tmp_path)
        assert setup_module.has_existing_state() is True

    def test_journal_entry_returns_true(self, tmp_path, monkeypatch, setup_module):
        _seed_pristine(tmp_path, setup_module)
        (tmp_path / "journal" / "2026-04-10.md").write_text(
            "Hoy estudié dos horas.\n", encoding="utf-8"
        )
        monkeypatch.setattr(setup_module, "ROOT", tmp_path)
        assert setup_module.has_existing_state() is True

    def test_parking_lot_modified_returns_true(self, tmp_path, monkeypatch, setup_module):
        _seed_pristine(tmp_path, setup_module)
        modified = (
            setup_module.PARKING_LOT_TEMPLATE
            + "\n- How do I order at a restaurant in Mexico City?\n"
        )
        (tmp_path / "parking-lot.md").write_text(modified, encoding="utf-8")
        monkeypatch.setattr(setup_module, "ROOT", tmp_path)
        assert setup_module.has_existing_state() is True

    def test_archived_session_returns_true(self, tmp_path, monkeypatch, setup_module):
        _seed_pristine(tmp_path, setup_module)
        (tmp_path / "state" / "sessions" / "archive" / "2026-03-01.yaml").write_text(
            "date: 2026-03-01\n", encoding="utf-8"
        )
        monkeypatch.setattr(setup_module, "ROOT", tmp_path)
        assert setup_module.has_existing_state() is True

    def test_parking_lot_mid_edit_returns_true(self, tmp_path, monkeypatch, setup_module):
        """User edits the Urgent section (middle of file, not trailing append)."""
        _seed_pristine(tmp_path, setup_module)
        content = setup_module.PARKING_LOT_TEMPLATE.replace(
            "## Urgent (need before an upcoming real-world situation)\n\n\n",
            "## Urgent (need before an upcoming real-world situation)\n\n"
            "- Trip to Mexico in 2 weeks\n\n",
        )
        (tmp_path / "parking-lot.md").write_text(content, encoding="utf-8")
        monkeypatch.setattr(setup_module, "ROOT", tmp_path)
        assert setup_module.has_existing_state() is True

    def test_offline_guide_returns_true(self, tmp_path, monkeypatch, setup_module):
        _seed_pristine(tmp_path, setup_module)
        (tmp_path / "state" / "offline-guides" / "restaurant-phrases.md").write_text(
            "# Restaurant phrases\n", encoding="utf-8"
        )
        monkeypatch.setattr(setup_module, "ROOT", tmp_path)
        assert setup_module.has_existing_state() is True

    def test_resource_with_entries_returns_true(self, tmp_path, monkeypatch, setup_module):
        _seed_pristine(tmp_path, setup_module)
        (tmp_path / "state" / "resource-tracker.yaml").write_text(
            "schema_version: 1\nresources:\n  - id: dreaming-spanish\n", encoding="utf-8"
        )
        monkeypatch.setattr(setup_module, "ROOT", tmp_path)
        assert setup_module.has_existing_state() is True

    def test_parking_lot_template_matches_init_student(self, setup_module):
        """Ensure setup.PARKING_LOT_TEMPLATE stays in sync with init-student.py.

        init-student.py is the source of truth for the template; setup.py
        inlines a copy for fast comparison. This test fails loudly if the
        two drift.
        """
        init_student_path = SCRIPTS_DIR / "init-student.py"
        spec = importlib.util.spec_from_file_location(
            "init_student_module", init_student_path
        )
        init_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(init_module)
        assert (
            setup_module.PARKING_LOT_TEMPLATE
            == init_module.TEMPLATES["parking-lot.md"]
        )


def _make_version(major, minor, micro=0, releaselevel="final", serial=0):
    """Return a fake version_info tuple compatible with sys.version_info's
    attribute access (.major, .minor, .micro) and tuple comparison (v < (3, 10)).

    ``type(sys.version_info)(...)`` is not constructable on all Python versions
    (raises TypeError on 3.14+). We use a namedtuple so both attribute access
    and tuple comparison work correctly.
    """
    import collections
    _VersionInfo = collections.namedtuple(
        "version_info", ["major", "minor", "micro", "releaselevel", "serial"]
    )
    return _VersionInfo(major, minor, micro, releaselevel, serial)


class TestCheckPython:
    def test_check_python_clear_error(self, setup_module, monkeypatch, capsys):
        """WIN-05: check_python() must emit a clear, actionable error on Python < 3.10.

        The error message must name the version floor (Python 3.10+), the version
        that was found, and the install URL — so a Windows user on Python 3.8 sees
        a helpful message, not a SyntaxError stack trace.
        """
        # Stub sys.version_info on the loaded setup_module's sys reference.
        # setup_module imports `sys` at module level, so patch the module's sys.
        fake_version = _make_version(3, 8, 0, "final", 0)
        monkeypatch.setattr(setup_module.sys, "version_info", fake_version)

        with pytest.raises(SystemExit) as excinfo:
            setup_module.check_python()

        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        combined = captured.out + captured.err
        assert "Python 3.10+ required" in combined, (
            f"error message missing version floor; got: {combined!r}"
        )
        assert "https://python.org" in combined, (
            f"error message missing install URL; got: {combined!r}"
        )
        assert "found 3.8" in combined, (
            f"error message missing actual version; got: {combined!r}"
        )

    def test_check_python_at_floor_passes(self, setup_module, monkeypatch, capsys):
        """WIN-05 negative case: Python 3.10 (at the floor) must not exit."""
        fake_version = _make_version(3, 10, 0, "final", 0)
        monkeypatch.setattr(setup_module.sys, "version_info", fake_version)

        # Must NOT raise SystemExit.
        setup_module.check_python()

        captured = capsys.readouterr()
        combined = captured.out + captured.err
        assert "Python 3.10.0" in combined, (
            f"version confirmation missing; got: {combined!r}"
        )


class TestSetupBatExitCode:
    """Regression test for CR-01: setup.bat exit code propagation.

    The 2026-04-13 code review (02-REVIEW.md) found that ``exit /b %ERRORLEVEL%``
    inside a parenthesized ``if`` block is expanded at parse time by cmd.exe,
    not at execution time. The block is only entered when its outer condition
    succeeded (``where py`` or ``where python`` returned 0), so %ERRORLEVEL%
    is substituted as 0 before the inner ``py scripts\\setup.py %*`` ever runs.
    Both success branches then always exit 0, masking every sys.exit(1) path
    in setup.py. See 02-REVIEW.md CR-01 for the full analysis.

    The fix is to restructure setup.bat with goto labels so each
    ``exit /b %ERRORLEVEL%`` line lives OUTSIDE any parenthesized block.
    Outside the block, cmd.exe expands %ERRORLEVEL% at execution time, which
    correctly reflects the exit code of the preceding py/python command.

    This test is static content-based because setup.bat cannot run on macOS
    or Linux. The runtime verification on Windows is a human verification
    step (see 02-VERIFICATION.md).
    """

    REPO_ROOT = SCRIPTS_DIR.parent
    SETUP_BAT = REPO_ROOT / "setup.bat"

    def _read_setup_bat(self):
        assert self.SETUP_BAT.exists(), (
            f"setup.bat missing at {self.SETUP_BAT} — "
            "it must live at the project root per WIN-04."
        )
        return self.SETUP_BAT.read_text(encoding="utf-8")

    def test_setup_bat_exit_code_propagation_uses_goto(self):
        """CR-01 regression: setup.bat must use goto-based structure.

        Asserts the fix from 02-REVIEW.md is present and the buggy
        parenthesized-if pattern is absent. This locks setup.bat against
        re-introduction of the exit-code-masking bug.
        """
        content = self._read_setup_bat()
        lines = content.splitlines()

        # Normalize for assertions — strip only trailing CR (file is CRLF on disk
        # but splitlines() handles both CRLF and LF correctly; be defensive).
        stripped_lines = [line.rstrip("\r") for line in lines]

        # 1. Goto labels must be present as standalone lines.
        assert ":use_py" in stripped_lines, (
            "CR-01 regression: :use_py label missing from setup.bat. "
            "See 02-REVIEW.md CR-01 for the canonical goto-based fix."
        )
        assert ":use_python" in stripped_lines, (
            "CR-01 regression: :use_python label missing from setup.bat. "
            "See 02-REVIEW.md CR-01 for the canonical goto-based fix."
        )
        assert ":no_python" in stripped_lines, (
            "CR-01 regression: :no_python label missing from setup.bat. "
            "See 02-REVIEW.md CR-01 for the canonical goto-based fix."
        )

        # 2. Goto branches must be present (the probes must branch to labels,
        #    not open parenthesized blocks).
        assert "if %ERRORLEVEL% equ 0 goto :use_py" in stripped_lines, (
            "CR-01 regression: 'if %ERRORLEVEL% equ 0 goto :use_py' branch missing."
        )
        assert "if %ERRORLEVEL% equ 0 goto :use_python" in stripped_lines, (
            "CR-01 regression: 'if %ERRORLEVEL% equ 0 goto :use_python' branch missing."
        )
        assert "goto :no_python" in stripped_lines, (
            "CR-01 regression: 'goto :no_python' fall-through missing."
        )

        # 3. No parenthesized if-block opens may exist anywhere in the file.
        #    The CR-01 bug pattern is `if ... (` on one line with
        #    `exit /b %ERRORLEVEL%` on a later line inside the block.
        #    We forbid the generalized form: any `if` line ending with `(`.
        paren_if_lines = [
            (i, line) for i, line in enumerate(stripped_lines)
            if line.strip().startswith("if ") and line.strip().endswith("(")
        ]
        assert not paren_if_lines, (
            "CR-01 regression: parenthesized if block(s) found in setup.bat. "
            "cmd.exe expands %ERRORLEVEL% at parse time inside such blocks, "
            "masking setup.py's exit code. Use the goto-based structure from "
            f"02-REVIEW.md CR-01. Offending lines: {paren_if_lines}"
        )

        # 4. Exactly two `exit /b %ERRORLEVEL%` lines (one per success branch).
        exit_errorlevel_lines = [
            line for line in stripped_lines
            if line.strip() == "exit /b %ERRORLEVEL%"
        ]
        assert len(exit_errorlevel_lines) == 2, (
            f"CR-01 regression: expected exactly 2 'exit /b %ERRORLEVEL%' "
            f"lines (one for the py branch, one for the python fallback), "
            f"got {len(exit_errorlevel_lines)}."
        )

        # 5. Each `exit /b %ERRORLEVEL%` line must NOT be inside a parenthesized
        #    block. We already assert no `if ... (` exists, so this is belt+suspenders:
        #    walk the file and verify no open-paren is currently "in scope" when
        #    an `exit /b %ERRORLEVEL%` line is encountered.
        depth = 0
        for i, line in enumerate(stripped_lines):
            stripped = line.strip()
            # Approximate: count raw ( and ) at line-trailing / leading positions.
            if stripped.endswith("("):
                depth += 1
            if stripped == ")":
                depth -= 1
            if stripped == "exit /b %ERRORLEVEL%":
                assert depth == 0, (
                    f"CR-01 regression: line {i} 'exit /b %ERRORLEVEL%' is "
                    f"inside a parenthesized block (depth={depth}). cmd.exe "
                    f"will expand %ERRORLEVEL% at parse time — see 02-REVIEW.md CR-01."
                )

        # 6. The three locked error lines (from 02-VERIFICATION.md human
        #    verification step 2) must still be present verbatim.
        assert "echo Error: Python not found on PATH." in stripped_lines, (
            "Locked error line missing: 'echo Error: Python not found on PATH.'"
        )
        assert "echo Install Python 3.10+ from https://python.org" in stripped_lines, (
            "Locked error line missing: 'echo Install Python 3.10+ from https://python.org'"
        )
        assert 'echo During installation, check "Add Python to PATH".' in stripped_lines, (
            "Locked error line missing: 'echo During installation, check \"Add Python to PATH\".'"
        )

        # 7. Final exit /b 1 (the "no python found" error path) is still present.
        assert "exit /b 1" in stripped_lines, (
            "Final 'exit /b 1' error path missing — the no-python-found branch "
            "must still exit 1."
        )

        # 8. File starts with @echo off (no BOM, no leading whitespace).
        assert stripped_lines[0] == "@echo off", (
            f"setup.bat first line must be '@echo off', got: {stripped_lines[0]!r}"
        )


class TestConfigureGitHooks:
    """Regression lock for Phase 2.1: configure_git_hooks must exist,
    be called from main(), and configure core.hooksPath=.githooks.

    Commit da6cf51 silently deleted this function and its call site
    during a worktree realignment. These assertions prevent a future
    worktree collapse from doing the same and inerting the LEAK hook.
    """

    SETUP_PY = Path(__file__).resolve().parent.parent / "scripts" / "setup.py"

    def test_configure_git_hooks_function_exists(self):
        source = self.SETUP_PY.read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        assert "configure_git_hooks" in names, (
            "configure_git_hooks() missing from scripts/setup.py — "
            "Phase 2.1 regression: commit da6cf51 deleted this before."
        )

    def test_configure_git_hooks_called_from_main(self):
        source = self.SETUP_PY.read_text(encoding="utf-8")
        tree = ast.parse(source)
        main_fn = next(
            (n for n in ast.walk(tree)
             if isinstance(n, ast.FunctionDef) and n.name == "main"),
            None,
        )
        assert main_fn is not None, "main() missing from scripts/setup.py"
        called = {
            node.func.id
            for node in ast.walk(main_fn)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert "configure_git_hooks" in called, (
            "main() does not call configure_git_hooks() — "
            "function exists but is dead code. LEAK hook will not activate."
        )

    def test_configure_git_hooks_sets_githooks_path(self):
        source = self.SETUP_PY.read_text(encoding="utf-8")
        assert '"core.hooksPath"' in source, (
            "configure_git_hooks must invoke 'git config core.hooksPath'"
        )
        assert '".githooks"' in source, (
            "configure_git_hooks must set core.hooksPath to '.githooks' exactly"
        )
