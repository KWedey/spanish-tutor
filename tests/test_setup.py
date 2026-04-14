"""Tests for scripts/setup.py — specifically has_existing_state()."""
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
