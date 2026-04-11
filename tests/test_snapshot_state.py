"""Tests for scripts/snapshot-state.py snapshot/rollback mechanism."""
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import importlib
snapshot_state = importlib.import_module("snapshot-state")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_state(tmp_path, monkeypatch):
    """Create a temporary state directory with sample files and patch constants."""
    sd = tmp_path / "state"
    sd.mkdir()
    (sd / "sessions").mkdir()

    # Write sample state files
    for name in ("skill-map.yaml", "schedule.yaml", "learner-profile.yaml"):
        (sd / name).write_text(f"file: {name}\n", encoding="utf-8")
    (sd / "sessions" / "2026-04-10.yaml").write_text("session: 1\n", encoding="utf-8")

    monkeypatch.setattr(snapshot_state, "STATE_DIR", sd)
    monkeypatch.setattr(snapshot_state, "SNAPSHOT_DIR", sd / ".snapshot")
    monkeypatch.setattr(snapshot_state, "ROOT", tmp_path)
    return sd


# ---------------------------------------------------------------------------
# 1. Snapshot creates a timestamped backup
# ---------------------------------------------------------------------------

class TestSnapshot:
    def test_creates_snapshot_with_all_files(self, mock_state):
        rc = snapshot_state.cmd_snapshot()

        assert rc == 0
        snapshots = snapshot_state._list_snapshots()
        assert len(snapshots) == 1

        snap = snapshots[0]
        assert (snap / "skill-map.yaml").exists()
        assert (snap / "schedule.yaml").exists()
        assert (snap / "learner-profile.yaml").exists()
        assert (snap / "sessions" / "2026-04-10.yaml").exists()

    def test_dry_run_does_not_create_snapshot(self, mock_state):
        rc = snapshot_state.cmd_snapshot(dry_run=True)

        assert rc == 0
        assert not (mock_state / ".snapshot").exists()


# ---------------------------------------------------------------------------
# 2. Rollback restores from the most recent snapshot
# ---------------------------------------------------------------------------

class TestRollback:
    def test_restores_state_from_snapshot(self, mock_state):
        # Take snapshot
        snapshot_state.cmd_snapshot()

        # Modify a state file
        (mock_state / "schedule.yaml").write_text("modified: true\n", encoding="utf-8")
        assert "modified" in (mock_state / "schedule.yaml").read_text()

        # Rollback
        rc = snapshot_state.cmd_rollback()

        assert rc == 0
        assert (mock_state / "schedule.yaml").read_text() == "file: schedule.yaml\n"

    def test_rollback_with_no_snapshots_fails(self, mock_state):
        rc = snapshot_state.cmd_rollback()
        assert rc == 1


# ---------------------------------------------------------------------------
# 3. List shows available snapshots
# ---------------------------------------------------------------------------

class TestList:
    def test_lists_snapshots(self, mock_state, capsys):
        snapshot_state.cmd_snapshot()

        rc = snapshot_state.cmd_list()

        assert rc == 0
        output = capsys.readouterr().out
        assert "1 snapshot(s) available" in output

    def test_lists_empty_when_none(self, mock_state, capsys):
        rc = snapshot_state.cmd_list()

        assert rc == 0
        output = capsys.readouterr().out
        assert "No snapshots found" in output


# ---------------------------------------------------------------------------
# 4. Clean removes old snapshots
# ---------------------------------------------------------------------------

class TestClean:
    def test_removes_old_snapshots(self, mock_state):
        # Create an old snapshot manually
        old_ts = (datetime.now() - timedelta(days=10)).strftime(snapshot_state.TIMESTAMP_FMT)
        old_dir = mock_state / ".snapshot" / old_ts
        old_dir.mkdir(parents=True)
        (old_dir / "schedule.yaml").write_text("old: true\n", encoding="utf-8")

        # Create a recent snapshot
        snapshot_state.cmd_snapshot()

        # Clean
        rc = snapshot_state.cmd_clean()

        assert rc == 0
        remaining = snapshot_state._list_snapshots()
        assert len(remaining) == 1
        # The old one should be gone, only the recent one remains
        assert old_ts not in [s.name for s in remaining]

    def test_clean_dry_run_preserves_snapshots(self, mock_state):
        old_ts = (datetime.now() - timedelta(days=10)).strftime(snapshot_state.TIMESTAMP_FMT)
        old_dir = mock_state / ".snapshot" / old_ts
        old_dir.mkdir(parents=True)
        (old_dir / "schedule.yaml").write_text("old: true\n", encoding="utf-8")

        rc = snapshot_state.cmd_clean(dry_run=True)

        assert rc == 0
        assert old_dir.exists()


# ---------------------------------------------------------------------------
# 5. Snapshot excludes .snapshot/ directory itself
# ---------------------------------------------------------------------------

class TestSnapshotExclusion:
    def test_snapshot_does_not_include_itself(self, mock_state):
        # Take two snapshots
        snapshot_state.cmd_snapshot()
        time.sleep(1)  # Ensure different timestamp
        snapshot_state.cmd_snapshot()

        snapshots = snapshot_state._list_snapshots()
        assert len(snapshots) == 2

        # Second snapshot should not contain .snapshot/ contents
        second = snapshots[-1]
        nested = list(second.rglob(".snapshot"))
        assert len(nested) == 0
