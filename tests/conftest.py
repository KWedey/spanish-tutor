"""Shared fixtures for the tutoring system test suite."""
import sys
from pathlib import Path

import pytest
import yaml

# Make scripts/ importable so `from shared import ...` works inside the scripts
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# Minimal valid YAML state data
# ---------------------------------------------------------------------------

MINIMAL_SKILL_MAP = {
    "schema_version": 1,
    "grammar": {
        "A-01-present-regular": {
            "status": "unseen",
            "introduced_date": None,
            "last_practiced": None,
            "practice_count": 0,
            "error_rate_drills": None,
            "error_rate_production": None,
            "error_trend": None,
            "performance_scaffolded": None,
            "performance_unscaffolded": None,
            "integration_tested_with": [],
            "prerequisites": [],
            "notes": "",
        },
        "B-01-preterite-regular": {
            "status": "unseen",
            "introduced_date": None,
            "last_practiced": None,
            "practice_count": 0,
            "error_rate_drills": None,
            "error_rate_production": None,
            "error_trend": None,
            "performance_scaffolded": None,
            "performance_unscaffolded": None,
            "integration_tested_with": [],
            "prerequisites": ["A-01-present-regular"],
            "notes": "",
        },
    },
    "vocabulary": {
        "tier1-greetings-introductions": {
            "status": "unseen",
            "words_total": 30,
            "words_introduced": 0,
            "passive_known": 0,
            "active_known": 0,
            "weak_production": [],
            "weak_recognition": [],
            "last_practiced": None,
            "error_tracking": {
                "error_rate_production": 0.0,
                "common_errors": [],
            },
        },
    },
    "pronunciation": {
        "vowel-sounds": {
            "status": "unseen",
            "last_practiced": None,
            "external_feedback": "",
        },
    },
    "cultural_awareness": {
        "politeness_formulas": {
            "status": "unseen",
            "introduced_at_phase": "B",
            "assessed_through": "",
            "signs_of_acquisition": "",
        },
    },
    "receptive_skills": {
        "listening": {
            "current_level": "L1",
            "hours_at_level": 0,
            "hours_total": 0,
            "comprehension_quality": None,
        },
        "reading": {
            "current_level": "R1",
            "hours_at_level": 0,
            "hours_total": 0,
            "comprehension_quality": None,
            "lookup_frequency": None,
        },
    },
}

MINIMAL_SCHEDULE = {
    "schema_version": 1,
    "current_phase": "A-foundation",
    "current_week": 1,
    "onboarding_complete": False,
    "session_number": 0,
    "last_session_date": None,
    "active_grammar": {"primary": None, "secondary": None},
    "carryover_concepts": [],
    "fluency_accuracy_balance": "accuracy-leaning",
    "placement_validation": {"active": False, "sessions_completed": 0},
    "fluency_days_this_week": 0,
    "last_fluency_day": None,
}

MINIMAL_LEARNER_PROFILE = {
    "schema_version": 1,
    "name": "Test Learner",
    "native_language": "English",
    "target_dialect": "Mexican",
    "initial_placement": {
        "level": None,
        "date": None,
        "self_report": "",
        "grammar_result": "",
        "vocabulary_observation": "",
        "reading_result": "",
        "confidence": "",
        "evidence_summary": "",
    },
}

MINIMAL_SYSTEM_HEALTH = {
    "schema_version": 1,
    "concepts_requiring_reteach_total": 0,
    "average_sessions_to_acquire": 0,
    "reteach_rate_30d": 0.0,
    "homework_completion_rate_30d": 0.0,
    "homework_reported_difficulty_avg": 0.0,
    "days_in_current_phase": 0,
    "concepts_acquired_per_month": 0,
    "concepts_in_practicing_simultaneously": 0,
    "average_session_duration_30d": 0,
    "session_frequency_30d": 0.0,
    "learner_initiated_topics_30d": 0,
    "sessions_rated_too_easy_30d": 0,
    "sessions_rated_too_hard_30d": 0,
    "anki_estimated_deck_size": 0,
    "anki_estimated_daily_review_minutes": 0,
    "last_validation_issues": [],
    "placement_validation_metrics": {
        "placement_level": None,
        "initial_confidence": None,
        "total_concepts_validated": 0,
        "total_downgrades": 0,
        "final_assessment": None,
        "validation_completed": None,
    },
    "goal_tracking": {
        "primary_goal_progress": "",
        "estimated_weeks_remaining": None,
        "concepts_remaining_for_next_phase": 0,
        "concepts_remaining_for_target_level": 0,
        "current_acquisition_rate": 0.0,
        "last_goal_review": None,
        "milestone_progress": [],
    },
    "session_difficulty_tracking": {
        "last_rating": None,
        "consecutive_too_easy": 0,
        "consecutive_too_hard": 0,
        "recent_ratings": [],
    },
    "last_system_review": None,
}

MINIMAL_SESSION_LOG = {
    "date": "2026-04-10",
    "session_number": 5,
    "duration_minutes": 30,
    "session_type": "standard",
    "session_status": "complete",
    "learner_energy": "medium",
    "gap_days": 1,
    "session_activities": [],
    "skill_map_updates": [],
    "assignments": [],
    "decision_engine_trace": {
        "candidates_scored": 3,
        "top_candidates": [],
        "selected_primary": "A-01-present-regular",
        "selected_secondary": "",
        "override_reason": None,
    },
    "session_difficulty_rating": "just-right",
    "next_session": {
        "recommended_focus": "A-01-present-regular",
        "reason": "Continue practice",
        "session_type": "normal",
    },
}

MINIMAL_RESOURCE_TRACKER = {
    "schema_version": 1,
    "input_summary": {
        "total_listening_hours": 0,
        "total_reading_hours": 0,
        "current_listening_level": "L1",
        "current_reading_level": "R1",
    },
    "resources": [],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def state_dir(tmp_path):
    """Create a temporary state directory with minimal valid YAML files."""
    sd = tmp_path / "state"
    sd.mkdir()
    (sd / "sessions").mkdir()

    _write_yaml(sd / "skill-map.yaml", MINIMAL_SKILL_MAP)
    _write_yaml(sd / "schedule.yaml", MINIMAL_SCHEDULE)
    _write_yaml(sd / "learner-profile.yaml", MINIMAL_LEARNER_PROFILE)
    _write_yaml(sd / "system-health.yaml", MINIMAL_SYSTEM_HEALTH)
    _write_yaml(sd / "resource-tracker.yaml", MINIMAL_RESOURCE_TRACKER)

    return sd


@pytest.fixture
def skill_map_data():
    """Return a deep copy of the minimal skill map."""
    import copy
    return copy.deepcopy(MINIMAL_SKILL_MAP)


@pytest.fixture
def schedule_data():
    import copy
    return copy.deepcopy(MINIMAL_SCHEDULE)


@pytest.fixture
def profile_data():
    import copy
    return copy.deepcopy(MINIMAL_LEARNER_PROFILE)


@pytest.fixture
def system_health_data():
    import copy
    return copy.deepcopy(MINIMAL_SYSTEM_HEALTH)


@pytest.fixture
def session_log_data():
    import copy
    return copy.deepcopy(MINIMAL_SESSION_LOG)


@pytest.fixture
def resource_tracker_data():
    import copy
    return copy.deepcopy(MINIMAL_RESOURCE_TRACKER)


def _write_yaml(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
