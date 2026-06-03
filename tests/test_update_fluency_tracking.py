"""Tests for scripts/update-fluency-tracking.py (C1 fluency-counter wiring).

The router (route_session._is_fluency_day) reads `fluency_days_this_week` and
`last_fluency_day` from schedule.yaml at session START. This script is the
WRITER that post-session.sh runs at session END: on a fluency session it
increments the week-aware counter and stamps last_fluency_day. Before this
script existed, nothing wrote those fields, so the router's fluency predicate
was permanently false in production (the project's signature tested-but-unwired
defect).
"""
import importlib
import sys
from datetime import date
from pathlib import Path

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

uft = importlib.import_module("update-fluency-tracking")


def _seed(tmp_path, schedule, session_type, *, date_str="2026-05-14"):
    state = tmp_path / "state"
    (state / "sessions").mkdir(parents=True)
    (state / "schedule.yaml").write_text(
        "# schedule header — schema: schemas/schedule.schema.yaml\n"
        + yaml.safe_dump(schedule, sort_keys=False),
        encoding="utf-8",
    )
    if session_type is not None:
        (state / "sessions" / f"{date_str}.yaml").write_text(
            yaml.safe_dump({"session_type": session_type}), encoding="utf-8"
        )
    return state


def _read_schedule(state):
    return yaml.safe_load((state / "schedule.yaml").read_text(encoding="utf-8"))


class TestFluencyIncrement:
    def test_fluency_session_increments_and_stamps_same_week(self, tmp_path):
        """last_fluency_day already in today's ISO week → increment the counter."""
        state = _seed(
            tmp_path,
            {"fluency_days_this_week": 1, "last_fluency_day": "2026-05-11"},  # wk20
            "fluency",
            date_str="2026-05-14",  # wk20
        )
        result = uft.update_fluency_tracking("2026-05-14", state)
        assert result is not None
        sched = _read_schedule(state)
        assert sched["fluency_days_this_week"] == 2
        assert sched["last_fluency_day"] == "2026-05-14"

    def test_fluency_session_resets_counter_on_new_week(self, tmp_path):
        """last_fluency_day in a PRIOR ISO week → counter resets to 1, not stale+1."""
        state = _seed(
            tmp_path,
            {"fluency_days_this_week": 3, "last_fluency_day": "2026-05-06"},  # wk19
            "fluency",
            date_str="2026-05-14",  # wk20
        )
        uft.update_fluency_tracking("2026-05-14", state)
        sched = _read_schedule(state)
        assert sched["fluency_days_this_week"] == 1
        assert sched["last_fluency_day"] == "2026-05-14"

    def test_fluency_session_from_null_last_day(self, tmp_path):
        """Null last_fluency_day → first fluency day of the week → counter = 1."""
        state = _seed(
            tmp_path,
            {"fluency_days_this_week": 0, "last_fluency_day": None},
            "fluency",
            date_str="2026-05-14",
        )
        uft.update_fluency_tracking("2026-05-14", state)
        sched = _read_schedule(state)
        assert sched["fluency_days_this_week"] == 1
        assert sched["last_fluency_day"] == "2026-05-14"


class TestNoOp:
    def test_non_fluency_session_is_noop(self, tmp_path):
        state = _seed(
            tmp_path,
            {"fluency_days_this_week": 1, "last_fluency_day": "2026-05-11"},
            "standard",
            date_str="2026-05-14",
        )
        result = uft.update_fluency_tracking("2026-05-14", state)
        assert result is None
        sched = _read_schedule(state)
        assert sched["fluency_days_this_week"] == 1
        assert sched["last_fluency_day"] == "2026-05-11"

    def test_missing_session_log_is_noop(self, tmp_path):
        state = _seed(
            tmp_path,
            {"fluency_days_this_week": 1, "last_fluency_day": "2026-05-11"},
            None,  # no session log written
            date_str="2026-05-14",
        )
        result = uft.update_fluency_tracking("2026-05-14", state)
        assert result is None
        assert _read_schedule(state)["fluency_days_this_week"] == 1

    def test_same_day_rerun_is_idempotent(self, tmp_path):
        """A date hosts one session — re-running for an already-stamped date
        must not double-count the counter."""
        state = _seed(
            tmp_path,
            {"fluency_days_this_week": 2, "last_fluency_day": "2026-05-14"},
            "fluency",
            date_str="2026-05-14",
        )
        result = uft.update_fluency_tracking("2026-05-14", state)
        assert result is None
        assert _read_schedule(state)["fluency_days_this_week"] == 2

    def test_missing_schedule_is_noop(self, tmp_path):
        state = tmp_path / "state"
        (state / "sessions").mkdir(parents=True)
        (state / "sessions" / "2026-05-14.yaml").write_text(
            yaml.safe_dump({"session_type": "fluency"}), encoding="utf-8"
        )
        # No schedule.yaml at all.
        assert uft.update_fluency_tracking("2026-05-14", state) is None


class TestPersistence:
    def test_preserves_leading_header_comment(self, tmp_path):
        state = _seed(
            tmp_path,
            {"fluency_days_this_week": 0, "last_fluency_day": None},
            "fluency",
            date_str="2026-05-14",
        )
        uft.update_fluency_tracking("2026-05-14", state)
        text = (state / "schedule.yaml").read_text(encoding="utf-8")
        assert text.startswith("# schedule header")

    def test_does_not_clobber_other_fields(self, tmp_path):
        state = _seed(
            tmp_path,
            {
                "current_phase": "B-conversational",
                "onboarding_complete": True,
                "fluency_days_this_week": 0,
                "last_fluency_day": None,
            },
            "fluency",
            date_str="2026-05-14",
        )
        uft.update_fluency_tracking("2026-05-14", state)
        sched = _read_schedule(state)
        assert sched["current_phase"] == "B-conversational"
        assert sched["onboarding_complete"] is True


class TestSameIsoWeek:
    def test_same_week_true(self):
        assert uft.same_iso_week(date(2026, 5, 11), date(2026, 5, 14)) is True

    def test_prior_week_false(self):
        assert uft.same_iso_week(date(2026, 5, 6), date(2026, 5, 14)) is False

    def test_cross_year_week_boundary(self):
        # 2025-12-29 is ISO week 1 of 2026 (ISO weeks can cross calendar years).
        assert uft.same_iso_week(date(2025, 12, 29), date(2026, 1, 1)) is True
