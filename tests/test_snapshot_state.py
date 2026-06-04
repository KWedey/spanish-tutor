"""Tests for scripts/snapshot-state.py snapshot/rollback mechanism.

scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
"""
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

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

    def test_rollback_preserves_session_log_absent_from_snapshot(self, mock_state):
        """QR-S3: a session log written after the snapshot must survive rollback
        (STUDENT-GUIDE promises 'your session log stays' while skill-map etc.
        revert)."""
        snapshot_state.cmd_snapshot()
        # Simulate a session: modify skill-map AND add today's log (not in snapshot)
        (mock_state / "skill-map.yaml").write_text("modified: true\n", encoding="utf-8")
        today_log = mock_state / "sessions" / "2026-06-03.yaml"
        today_log.write_text("session_number: 2\n", encoding="utf-8")

        rc = snapshot_state.cmd_rollback()

        assert rc == 0
        # skill-map reverted...
        assert (mock_state / "skill-map.yaml").read_text() == "file: skill-map.yaml\n"
        # ...but today's session log preserved
        assert today_log.exists(), "QR-S3: today's session log must survive rollback"
        assert today_log.read_text() == "session_number: 2\n"

    def test_rollback_restores_session_log_present_in_snapshot(self, mock_state):
        """A session log that WAS in the snapshot is restored to its snapshot
        content (not the preservation path)."""
        snapshot_state.cmd_snapshot()
        # Modify the pre-existing (snapshotted) log
        (mock_state / "sessions" / "2026-04-10.yaml").write_text("session: 999\n", encoding="utf-8")
        rc = snapshot_state.cmd_rollback()
        assert rc == 0
        assert (mock_state / "sessions" / "2026-04-10.yaml").read_text() == "session: 1\n"


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


# ---------------------------------------------------------------------------
# 6. Suffix-tolerant timestamp parsing
# ---------------------------------------------------------------------------

class TestSuffixedTimestamps:
    def test_parses_plain_timestamp(self):
        """_snapshot_timestamp handles standard YYYYMMDD-HHMMSS names."""
        p = Path("20260413-141500")
        result = snapshot_state._snapshot_timestamp(p)
        assert result is not None
        assert result.year == 2026
        assert result.month == 4

    def test_parses_suffixed_timestamp(self):
        """_snapshot_timestamp strips single-letter suffix before parsing."""
        p = Path("20260413-141500-a")
        result = snapshot_state._snapshot_timestamp(p)
        assert result is not None
        assert result.year == 2026

    def test_rejects_tmpdir_name(self):
        """_snapshot_timestamp returns None for .tmp-* dir names."""
        p = Path(".tmp-12345-20260413-141500")
        result = snapshot_state._snapshot_timestamp(p)
        assert result is None


# ---------------------------------------------------------------------------
# 7. Atomic rename — no .tmp-* left after success, collision uses suffix
# ---------------------------------------------------------------------------

class TestAtomicRename:
    def test_no_tmpdir_remains_after_snapshot(self, mock_state):
        """After successful snapshot, no .tmp-* directory should exist."""
        snapshot_state.cmd_snapshot()
        snap_dir = mock_state / ".snapshot"
        tmpdirs = [d for d in snap_dir.iterdir() if d.name.startswith(".tmp-")]
        assert len(tmpdirs) == 0

    def test_collision_uses_suffix(self, mock_state):
        """When timestamp dir already exists, snapshot uses -a suffix."""
        # Create the first snapshot
        snapshot_state.cmd_snapshot()
        snapshots_before = snapshot_state._list_snapshots()
        assert len(snapshots_before) == 1

        # Force collision by pre-creating the expected timestamp dir
        from datetime import datetime as _dt
        stamp = _dt.now().strftime(snapshot_state.TIMESTAMP_FMT)
        collision_dir = mock_state / ".snapshot" / stamp
        collision_dir.mkdir(parents=True, exist_ok=True)

        snapshot_state.cmd_snapshot()
        all_snapshots = snapshot_state._list_snapshots()
        # Should have at least 2 snapshots (first + collision-suffixed or later timestamp)
        assert len(all_snapshots) >= 2

    def test_suffixed_snapshot_in_list(self, mock_state):
        """A suffixed snapshot dir appears in _list_snapshots."""
        snap_dir = mock_state / ".snapshot"
        snap_dir.mkdir(parents=True, exist_ok=True)
        suffixed = snap_dir / "20260413-141500-a"
        suffixed.mkdir()
        (suffixed / "schedule.yaml").write_text("test: true\n")

        snapshots = snapshot_state._list_snapshots()
        names = [s.name for s in snapshots]
        assert "20260413-141500-a" in names


# ---------------------------------------------------------------------------
# 8. Orphan sweep — old orphans removed, recent ones preserved
# ---------------------------------------------------------------------------

class TestOrphanSweep:
    def test_sweeps_old_orphan(self, mock_state):
        """Orphan .tmp-* dirs older than 1 hour are removed."""
        snap_dir = mock_state / ".snapshot"
        snap_dir.mkdir(parents=True, exist_ok=True)

        # Create an old orphan (timestamp 2 hours ago)
        from datetime import datetime as _dt, timedelta as _td
        old_stamp = (_dt.now() - _td(hours=2)).strftime(snapshot_state.TIMESTAMP_FMT)
        orphan = snap_dir / f".tmp-99999-{old_stamp}"
        orphan.mkdir()
        (orphan / "junk.yaml").write_text("orphan\n")

        snapshot_state._sweep_orphan_tmpdirs()
        assert not orphan.exists()

    def test_keeps_recent_orphan(self, mock_state):
        """Orphan .tmp-* dirs newer than 1 hour are left alone."""
        snap_dir = mock_state / ".snapshot"
        snap_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime as _dt
        recent_stamp = _dt.now().strftime(snapshot_state.TIMESTAMP_FMT)
        orphan = snap_dir / f".tmp-99999-{recent_stamp}"
        orphan.mkdir()

        snapshot_state._sweep_orphan_tmpdirs()
        assert orphan.exists()

    def test_cmd_snapshot_sweeps_orphans(self, mock_state):
        """cmd_snapshot calls _sweep_orphan_tmpdirs at the top."""
        snap_dir = mock_state / ".snapshot"
        snap_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime as _dt, timedelta as _td
        old_stamp = (_dt.now() - _td(hours=2)).strftime(snapshot_state.TIMESTAMP_FMT)
        orphan = snap_dir / f".tmp-99999-{old_stamp}"
        orphan.mkdir()
        (orphan / "junk.yaml").write_text("orphan\n")

        snapshot_state.cmd_snapshot()
        assert not orphan.exists()

    def test_cmd_clean_sweeps_orphans(self, mock_state):
        """cmd_clean also sweeps orphan .tmp-* dirs."""
        snap_dir = mock_state / ".snapshot"
        snap_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime as _dt, timedelta as _td
        old_stamp = (_dt.now() - _td(hours=2)).strftime(snapshot_state.TIMESTAMP_FMT)
        orphan = snap_dir / f".tmp-99999-{old_stamp}"
        orphan.mkdir()
        (orphan / "junk.yaml").write_text("orphan\n")

        snapshot_state.cmd_clean()
        assert not orphan.exists()
