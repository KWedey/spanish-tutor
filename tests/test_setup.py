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
    (root / "journal").mkdir(exist_ok=True)
    (root / "progress-reports").mkdir(exist_ok=True)

    # Gitkeep placeholders so iterdir returns something non-empty but
    # doesn't trigger the "has data" branches
    for rel in (
        "state/sessions/.gitkeep",
        "state/sessions/archive/.gitkeep",
        "state/summaries/.gitkeep",
        "state/milestones/.gitkeep",
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
