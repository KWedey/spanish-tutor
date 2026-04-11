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
    "goals": ["travel"],
    "initial_placement": {"level": None},
}

MINIMAL_SYSTEM_HEALTH = {
    "schema_version": 1,
    "last_session": None,
    "total_sessions": 0,
    "consecutive_days": 0,
    "state_errors": [],
    "auto_fixes": [],
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
def resource_tracker_data():
    import copy
    return copy.deepcopy(MINIMAL_RESOURCE_TRACKER)


def _write_yaml(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
