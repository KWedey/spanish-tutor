"""Tests for scripts/recompute-metrics.py (QR-P1/QR-P2 calibration wiring).

scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
"""
import importlib
from datetime import date

import yaml

rm = importlib.import_module("recompute-metrics")


def _seed(tmp_path, skill_map=None, health=None, sessions=None):
    state = tmp_path / "state"
    (state / "sessions").mkdir(parents=True)
    if skill_map is not None:
        (state / "skill-map.yaml").write_text(
            "# skill-map header\n" + yaml.safe_dump(skill_map), encoding="utf-8"
        )
    if health is not None:
        (state / "system-health.yaml").write_text(
            "# health header\n" + yaml.safe_dump(health), encoding="utf-8"
        )
    for name, data in (sessions or {}).items():
        (state / "sessions" / f"{name}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    return state


class TestRegressionCounts:
    def test_regressed_increments(self, tmp_path):
        state = _seed(tmp_path,
            skill_map={"grammar": {"X": {"status": "regressed", "regression_session_count": 2}}},
            health={"concepts_requiring_reteach_total": 0,
                    "sessions_rated_too_easy_30d": 0, "sessions_rated_too_hard_30d": 0})
        rm.recompute(state, date(2026, 6, 3))
        sm = yaml.safe_load((state / "skill-map.yaml").read_text())
        assert sm["grammar"]["X"]["regression_session_count"] == 3

    def test_reacquired_resets_to_zero(self, tmp_path):
        state = _seed(tmp_path,
            skill_map={"grammar": {"Y": {"status": "acquired", "regression_session_count": 4}}},
            health={"concepts_requiring_reteach_total": 0,
                    "sessions_rated_too_easy_30d": 0, "sessions_rated_too_hard_30d": 0})
        rm.recompute(state, date(2026, 6, 3))
        sm = yaml.safe_load((state / "skill-map.yaml").read_text())
        assert sm["grammar"]["Y"]["regression_session_count"] == 0

    def test_vocab_regressed_does_not_get_grammar_only_counter(self, tmp_path):
        """P2-t: regression_session_count is grammar-only (schema + system-design.md);
        a regressed vocabulary cluster must NOT receive it (no reader; not declared on
        vocabulary_entry_template). count_reteach still counts vocab — see below."""
        state = _seed(tmp_path,
            skill_map={"vocabulary": {"V": {"status": "regressed"}}},
            health={"concepts_requiring_reteach_total": 0,
                    "sessions_rated_too_easy_30d": 0, "sessions_rated_too_hard_30d": 0})
        rm.recompute(state, date(2026, 6, 3))
        sm = yaml.safe_load((state / "skill-map.yaml").read_text())
        assert "regression_session_count" not in sm["vocabulary"]["V"]

    def test_header_preserved(self, tmp_path):
        state = _seed(tmp_path,
            skill_map={"grammar": {"X": {"status": "regressed"}}},
            health={"concepts_requiring_reteach_total": 0,
                    "sessions_rated_too_easy_30d": 0, "sessions_rated_too_hard_30d": 0})
        rm.recompute(state, date(2026, 6, 3))
        assert (state / "skill-map.yaml").read_text().startswith("# skill-map header")


class TestSystemHealthCounters:
    def test_reteach_total_counts_regressed(self, tmp_path):
        state = _seed(tmp_path,
            skill_map={"grammar": {"X": {"status": "regressed"}, "Z": {"status": "acquired"}},
                       "vocabulary": {"V": {"status": "regressed"}}},
            health={"concepts_requiring_reteach_total": 0,
                    "sessions_rated_too_easy_30d": 0, "sessions_rated_too_hard_30d": 0})
        rm.recompute(state, date(2026, 6, 3))
        h = yaml.safe_load((state / "system-health.yaml").read_text())
        assert h["concepts_requiring_reteach_total"] == 2

    def test_difficulty_window(self, tmp_path):
        state = _seed(tmp_path,
            skill_map={"grammar": {}},
            health={"concepts_requiring_reteach_total": 0,
                    "sessions_rated_too_easy_30d": 0, "sessions_rated_too_hard_30d": 0},
            sessions={
                "2026-06-03": {"session_difficulty_rating": "too-easy"},
                "2026-06-02": {"session_difficulty_rating": "too-hard"},
                "2026-01-01": {"session_difficulty_rating": "too-easy"},  # outside 30d
            })
        rm.recompute(state, date(2026, 6, 3))
        h = yaml.safe_load((state / "system-health.yaml").read_text())
        assert h["sessions_rated_too_easy_30d"] == 1
        assert h["sessions_rated_too_hard_30d"] == 1

    def test_difficulty_window_counts_archived_logs(self, tmp_path):
        state = _seed(tmp_path,
            skill_map={"grammar": {}},
            health={"concepts_requiring_reteach_total": 0,
                    "sessions_rated_too_easy_30d": 0, "sessions_rated_too_hard_30d": 0},
            sessions={"2026-06-03": {"session_difficulty_rating": "too-easy"}})
        archive = state / "sessions" / "archive"
        archive.mkdir()
        (archive / "2026-05-20.yaml").write_text(
            yaml.safe_dump({"session_difficulty_rating": "too-easy"}), encoding="utf-8")
        (archive / "2026-05-21.yaml").write_text(
            yaml.safe_dump({"session_difficulty_rating": "too-hard"}), encoding="utf-8")

        rm.recompute(state, date(2026, 6, 3))

        h = yaml.safe_load((state / "system-health.yaml").read_text())
        assert h["sessions_rated_too_easy_30d"] == 2
        assert h["sessions_rated_too_hard_30d"] == 1

    def test_missing_state_files_no_crash(self, tmp_path):
        state = tmp_path / "state"
        (state / "sessions").mkdir(parents=True)
        summary = rm.recompute(state, date(2026, 6, 3))  # no skill-map / health
        assert summary["reteach_total"] == 0


class TestCorruptInputNotClobbered:
    """A3: a corrupt skill-map on this write-back path must RAISE, not be
    silently re-serialized as {} (which would erase every concept).
    """

    def test_corrupt_skill_map_raises_and_preserves_file(self, tmp_path):
        import pytest

        state = tmp_path / "state"
        (state / "sessions").mkdir(parents=True)
        sm = state / "skill-map.yaml"
        corrupt = "# skill-map header\ngrammar: [unterminated\n  : : :\n"
        sm.write_text(corrupt, encoding="utf-8")

        with pytest.raises(yaml.YAMLError):
            rm.recompute(state, date(2026, 6, 3))

        # The corrupt-but-recoverable file must be left byte-for-byte intact,
        # never overwritten with an empty/default mapping.
        assert sm.read_text(encoding="utf-8") == corrupt
