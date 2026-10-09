"""Tests for scripts/archive-sessions.py session-log archiving.

scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
"""
from datetime import date, timedelta

import importlib
import pytest

archive_sessions = importlib.import_module("archive-sessions")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sessions_dir(tmp_path, monkeypatch):
    """Point the module's SESSIONS_DIR/ARCHIVE_DIR at a temp state dir.

    SESSIONS_DIR and ARCHIVE_DIR are derived from STATE_DIR at import time, so
    patching STATE_DIR alone would not redirect them — patch the two paths the
    module actually reads.
    """
    sd = tmp_path / "state" / "sessions"
    sd.mkdir(parents=True)
    monkeypatch.setattr(archive_sessions, "SESSIONS_DIR", sd)
    monkeypatch.setattr(archive_sessions, "ARCHIVE_DIR", sd / "archive")
    return sd


def _write_session(sessions_dir, session_date: date) -> None:
    """Create a session log named YYYY-MM-DD.yaml with the given date."""
    (sessions_dir / f"{session_date.isoformat()}.yaml").write_text(
        "session_number: 1\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# 1. Files older than the threshold move to archive/
# ---------------------------------------------------------------------------

class TestArchivesOldSessions:
    def test_moves_files_older_than_60_days(self, sessions_dir):
        old_date = date.today() - timedelta(days=90)
        _write_session(sessions_dir, old_date)

        moved = archive_sessions.archive_sessions()

        assert moved == 1
        old_name = f"{old_date.isoformat()}.yaml"
        assert not (sessions_dir / old_name).exists()
        assert (sessions_dir / "archive" / old_name).exists()

    def test_archived_content_is_preserved(self, sessions_dir):
        old_date = date.today() - timedelta(days=90)
        _write_session(sessions_dir, old_date)

        archive_sessions.archive_sessions()

        dest = sessions_dir / "archive" / f"{old_date.isoformat()}.yaml"
        assert dest.read_text(encoding="utf-8") == "session_number: 1\n"


# ---------------------------------------------------------------------------
# 2. Recent files stay put
# ---------------------------------------------------------------------------

class TestKeepsRecentSessions:
    def test_recent_file_is_not_archived(self, sessions_dir):
        recent_date = date.today() - timedelta(days=10)
        _write_session(sessions_dir, recent_date)

        moved = archive_sessions.archive_sessions()

        assert moved == 0
        assert (sessions_dir / f"{recent_date.isoformat()}.yaml").exists()
        assert not (sessions_dir / "archive").exists()

    def test_file_exactly_at_threshold_stays(self, sessions_dir):
        """cutoff = today - 60 days; a session dated exactly at the cutoff is
        not strictly older than it, so it must stay (boundary check)."""
        boundary_date = date.today() - timedelta(days=60)
        _write_session(sessions_dir, boundary_date)

        moved = archive_sessions.archive_sessions()

        assert moved == 0
        assert (sessions_dir / f"{boundary_date.isoformat()}.yaml").exists()

    def test_mixed_old_and_recent_split_correctly(self, sessions_dir):
        old_date = date.today() - timedelta(days=120)
        recent_date = date.today() - timedelta(days=5)
        _write_session(sessions_dir, old_date)
        _write_session(sessions_dir, recent_date)

        moved = archive_sessions.archive_sessions()

        assert moved == 1
        assert (sessions_dir / "archive" / f"{old_date.isoformat()}.yaml").exists()
        assert (sessions_dir / f"{recent_date.isoformat()}.yaml").exists()


# ---------------------------------------------------------------------------
# 3. Idempotent re-run
# ---------------------------------------------------------------------------

class TestIdempotentRerun:
    def test_second_run_moves_nothing(self, sessions_dir):
        old_date = date.today() - timedelta(days=90)
        _write_session(sessions_dir, old_date)

        first = archive_sessions.archive_sessions()
        second = archive_sessions.archive_sessions()

        assert first == 1
        assert second == 0
        # The archived file is still in archive/, not re-created in sessions/.
        assert (sessions_dir / "archive" / f"{old_date.isoformat()}.yaml").exists()
        assert not (sessions_dir / f"{old_date.isoformat()}.yaml").exists()

    def test_already_archived_files_are_not_reconsidered(self, sessions_dir):
        """Files under archive/ are never scanned — only direct children of
        sessions/ are candidates, so a stale archived file cannot double-move."""
        old_date = date.today() - timedelta(days=200)
        archive_dir = sessions_dir / "archive"
        archive_dir.mkdir()
        (archive_dir / f"{old_date.isoformat()}.yaml").write_text(
            "old: true\n", encoding="utf-8"
        )

        moved = archive_sessions.archive_sessions()

        assert moved == 0


# ---------------------------------------------------------------------------
# 4. dry-run reports without moving
# ---------------------------------------------------------------------------

class TestDryRun:
    def test_dry_run_does_not_move(self, sessions_dir):
        old_date = date.today() - timedelta(days=90)
        _write_session(sessions_dir, old_date)

        moved = archive_sessions.archive_sessions(dry_run=True)

        assert moved == 1  # count of would-be moves
        assert (sessions_dir / f"{old_date.isoformat()}.yaml").exists()
        assert not (sessions_dir / "archive").exists()


# ---------------------------------------------------------------------------
# 5. Threshold override and non-session files
# ---------------------------------------------------------------------------

class TestThresholdAndFiltering:
    def test_custom_days_threshold(self, sessions_dir):
        session_date = date.today() - timedelta(days=40)
        _write_session(sessions_dir, session_date)

        assert archive_sessions.archive_sessions(days=60) == 0
        assert archive_sessions.archive_sessions(days=30) == 1

    def test_non_matching_filenames_ignored(self, sessions_dir):
        (sessions_dir / "README.md").write_text("notes\n", encoding="utf-8")
        (sessions_dir / "2026-13-40.yaml").write_text("bad date\n", encoding="utf-8")
        (sessions_dir / ".hidden.yaml").write_text("hidden\n", encoding="utf-8")

        moved = archive_sessions.archive_sessions()

        assert moved == 0
        assert (sessions_dir / "README.md").exists()
        assert (sessions_dir / "2026-13-40.yaml").exists()

    def test_missing_sessions_dir_is_safe(self, sessions_dir, monkeypatch):
        monkeypatch.setattr(archive_sessions, "SESSIONS_DIR", sessions_dir / "nope")
        assert archive_sessions.find_archivable_sessions(60) == []


# ---------------------------------------------------------------------------
# 5b. --keep spares the session post-session.sh is processing
# ---------------------------------------------------------------------------

class TestKeep:
    def test_kept_session_stays_while_other_old_sessions_move(self, sessions_dir):
        kept = date.today() - timedelta(days=200)
        other = date.today() - timedelta(days=100)
        _write_session(sessions_dir, kept)
        _write_session(sessions_dir, other)

        moved = archive_sessions.archive_sessions(keep=kept)

        assert moved == 1
        assert (sessions_dir / f"{kept.isoformat()}.yaml").exists()
        assert (sessions_dir / "archive" / f"{other.isoformat()}.yaml").exists()

    def test_keep_flag_on_the_command_line(self, sessions_dir, monkeypatch):
        kept = date.today() - timedelta(days=200)
        _write_session(sessions_dir, kept)
        monkeypatch.setattr("sys.argv", ["archive-sessions.py", "--keep", kept.isoformat()])

        archive_sessions.main()

        assert (sessions_dir / f"{kept.isoformat()}.yaml").exists()
        assert not (sessions_dir / "archive").exists()

    def test_keep_rejects_a_malformed_date(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.argv", ["archive-sessions.py", "--keep", "2026-02-31"])

        with pytest.raises(SystemExit) as exc:
            archive_sessions.main()

        assert exc.value.code == 2
        assert "argument --keep: invalid" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# 6. parse_session_date filename parsing
# ---------------------------------------------------------------------------

class TestParseSessionDate:
    def test_parses_valid_filename(self):
        assert archive_sessions.parse_session_date("2026-03-15.yaml") == date(2026, 3, 15)

    @pytest.mark.parametrize("name", [
        "notes.md",
        "2026-03-15.txt",
        "session-2026-03-15.yaml",
        "2026-3-15.yaml",
        "2026-13-40.yaml",  # matches pattern but is not a real calendar date
    ])
    def test_rejects_bad_filenames(self, name):
        assert archive_sessions.parse_session_date(name) is None
