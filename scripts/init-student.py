#!/usr/bin/env python3
"""Reset all student data to clean templates for sharing or starting over."""
import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from shared import (ROOT, STATE_DIR, load_schema, get_field_default, load_yaml,
                    yaml_value as _yaml_value, atomic_write, green, yellow, red)

# ---------------------------------------------------------------------------
# Schema-driven template generation
# ---------------------------------------------------------------------------

# Schema-to-file mapping and header comments for state files generated from schemas.
SCHEMA_TEMPLATES = {
    "state/learner-profile.yaml": {
        "schema": "learner-profile",
        "header": (
            "# Learner Profile — slow-changing facts about the learner\n"
            "# Updated rarely, typically during first session and at phase transitions.\n"
            "# Schema: schemas/learner-profile.schema.yaml\n"
        ),
    },
    "state/schedule.yaml": {
        "schema": "schedule",
        "header": (
            "# Schedule — the tutor's current plan\n"
            "# Updated at the end of each session.\n"
            "# Schema: schemas/schedule.schema.yaml\n"
        ),
    },
    "state/system-health.yaml": {
        "schema": "system-health",
        "header": (
            "# System Health — meta-metrics on tutoring system effectiveness\n"
            "# Updated at end of each session. Reviewed in detail during weekly reviews.\n"
            "# Schema: schemas/system-health.schema.yaml\n"
        ),
    },
    "state/resource-tracker.yaml": {
        "schema": "resource-tracker",
        "header": (
            "# Resource Tracker — which external resources are in active rotation\n"
            "# Updated when resources are added, swapped, or engagement changes.\n"
            "# Schema: schemas/resource-tracker.schema.yaml\n"
        ),
    },
}




def _render_map_children(children: dict, indent: int) -> str:
    """Render nested map children as YAML lines."""
    lines = []
    prefix = "  " * indent
    for name, spec in children.items():
        if not isinstance(spec, dict):
            continue
        default = get_field_default(spec)
        if spec.get("type") == "map" and "children" in spec:
            lines.append(f"{prefix}{name}:")
            lines.append(_render_map_children(spec["children"], indent + 1))
        else:
            lines.append(f"{prefix}{name}: {_yaml_value(default)}")
    return "\n".join(lines)


def generate_template_from_schema(schema_name: str, header: str = "") -> str:
    """Generate a default YAML template from a schema file.

    Reads schemas/<schema_name>.schema.yaml and builds a YAML string
    using default values from the schema's 'fields' section.
    """
    schema = load_schema(schema_name)
    fields = schema.get("fields", {})

    lines = []
    if header:
        lines.append(header)

    for name, spec in fields.items():
        if not isinstance(spec, dict):
            continue
        default = get_field_default(spec)
        if spec.get("type") == "map" and "children" in spec:
            lines.append(f"{name}:")
            lines.append(_render_map_children(spec["children"], 1))
        else:
            lines.append(f"{name}: {_yaml_value(default)}")

    return "\n".join(lines) + "\n"


# Template files keyed by path relative to ROOT. skill-map.yaml is reset
# in-place (too large for inline template) — see reset_skill_map().
# Schema-driven templates are generated at runtime; parking-lot is static.
TEMPLATES: dict[str, str] = {}

# Generate schema-driven templates
for _rel_path, _info in SCHEMA_TEMPLATES.items():
    TEMPLATES[_rel_path] = generate_template_from_schema(_info["schema"], _info["header"])

TEMPLATES["parking-lot.md"] = (
    "# Parking Lot — Things I Want to Learn\n\n"
    "Add anything here between sessions. Your tutor will review this at the\n"
    "start of each session and work items into lessons.\n\n"
    "## Urgent (need before an upcoming real-world situation)\n\n\n"
    "## Questions\n\n\n## Words & Phrases I Encountered\n\n\n## Completed\n\n"
)

SKILL_MAP_HEADER = (
    "# Skill Map — learner's current mastery state across all skill dimensions\n"
    "# Updated every session. The single source of truth for what has been taught "
    "and how well it's retained.\n# Schema defined in docs/system-design.md\n#\n"
    "# Status values:\n"
    "#   unseen — not yet introduced | introduced — seen once, not yet practiced\n"
    "#   practicing — error rate > 15% | acquired — error rate < 10%\n"
    "#   automatic — spot-checked only | regressed — errors resurfaced\n#\n"
    "# Context performance: null | struggling | competent\n"
    "# Acquisition requires performance_unscaffolded = competent\n\n"
)

ZERO_GRAMMAR = dict(status="unseen", introduced_date=None, last_practiced=None,
    practice_count=0, error_rate_drills=None, error_rate_production=None,
    error_trend=None, performance_scaffolded=None, performance_unscaffolded=None,
    integration_tested_with=[])

ZERO_VOCAB = dict(status="unseen", words_introduced=0, passive_known=0, active_known=0,
    weak_production=[], weak_recognition=[], last_practiced=None)

ZERO_PRONUN = dict(status="unseen", last_practiced=None, external_feedback="")


def reset_skill_map() -> None:
    """Load skill-map.yaml, zero all progress values, and rewrite.

    On a fresh clone the working file is gitignored and therefore absent —
    in that case we bootstrap from state/skill-map.template.yaml (which is
    tracked). The template is pristine already, but we still run the zero
    pass so that a stale or hand-edited template can't leak progress values.
    """
    path = STATE_DIR / "skill-map.yaml"
    template = STATE_DIR / "skill-map.template.yaml"
    if not path.exists():
        if template.exists():
            path.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
            print(yellow(f"  BOOTSTRAPPED from {template.relative_to(ROOT)}"))
        else:
            print(red(
                f"  MISSING: {path.relative_to(ROOT)} (and no template at "
                f"{template.relative_to(ROOT)})"
            ))
            return
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for entry in (data.get("grammar") or {}).values():
        if isinstance(entry, dict):
            entry.update(ZERO_GRAMMAR)
    for entry in (data.get("vocabulary") or {}).values():
        if isinstance(entry, dict):
            entry.update({k: (list(v) if isinstance(v, list) else v) for k, v in ZERO_VOCAB.items()})
    for entry in (data.get("pronunciation") or {}).values():
        if isinstance(entry, dict):
            entry.update(ZERO_PRONUN)
    for entry in (data.get("writing") or {}).values():
        if isinstance(entry, dict):
            entry["status"], entry["last_practiced"] = "unseen", None
    for key in ("listening", "reading"):
        if key in (data.get("receptive_skills") or {}):
            data["receptive_skills"][key] = {f: (None if f != "notes" else "") for f in data["receptive_skills"][key]}
    for entry in (data.get("cultural_awareness") or {}).values():
        if isinstance(entry, dict):
            entry["status"] = "unseen"
    for key in (data.get("fluency_metrics") or {}):
        data["fluency_metrics"][key] = ""
    oe = data.get("overall_estimates") or {}
    oe.update(cefr_estimate="A0", estimated_active_vocabulary=0, estimated_passive_vocabulary=0,
              production_gap=0, strongest_skill=None, weakest_skill=None, last_formal_assessment=None)
    data = {"schema_version": 1, **{k: v for k, v in data.items() if k != "schema_version"}}
    content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    path.write_text(SKILL_MAP_HEADER + content, encoding="utf-8")
    print(green(f"  RESET: {path.relative_to(ROOT)}"))


def clear_directory(rel_path: str) -> int:
    """Remove all files in a directory except .gitkeep. Returns count removed."""
    dirpath = ROOT / rel_path
    if not dirpath.exists():
        print(yellow(f"  SKIP: {rel_path}/ (does not exist)")); return 0
    files = [f for f in dirpath.iterdir() if f.name != ".gitkeep" and not f.is_dir()]
    for f in files:
        f.unlink()
    count = len(files)
    print(green(f"  CLEARED: {rel_path}/ ({count} files)") if count else f"  CLEAN: {rel_path}/")
    return count


def _dir_has_file(root, rel_path: str, suffix: str | None = None) -> bool:
    """True if root/rel_path contains any non-.gitkeep file.

    If `suffix` is given, only files with that extension count.
    """
    d = root / rel_path
    if not d.exists():
        return False
    for f in d.iterdir():
        if not f.is_file() or f.name == ".gitkeep":
            continue
        if suffix is None or f.suffix == suffix:
            return True
    return False


def has_existing_learner_data(root, state_dir=None) -> bool:
    """Detect whether the repo already holds real learner data.

    Canonical detector for the whole toolchain: setup.py's has_existing_state()
    delegates here so the two scripts can never disagree about what counts as
    real data (init-student is the one that actually wipes it on reset).
    `state_dir` overrides where the state tree lives (defaults to root/state);
    callers that write to a redirected STATE_DIR must pass it so the guard
    inspects the same directory the writer targets. Returns
    True on any of:
      - A session log in state/sessions/
      - A journal entry in journal/
      - An archived session in state/sessions/archive/
      - A weekly summary in state/summaries/
      - A milestone in state/milestones/
      - A progress report in progress-reports/
      - Any file in state/offline-guides/
      - parking-lot.md modified from its pristine template
      - state/learner-profile.yaml with a populated name
      - state/resource-tracker.yaml with any entries in `resources`

    main() wipes all of these on --force, so any one of them must trigger a
    recovery snapshot first (P2-c: a crash or hand-edit can leave session logs
    behind an empty profile name; A2: archived-only history was the gap). Cheap
    directory iteration runs first; YAML parses are the most expensive and run
    last, failing safe (return True) on a corrupt-but-present file so --force
    never clobbers a recoverable one.
    """
    state_dir = Path(state_dir) if state_dir is not None else root / "state"

    # Directory-level checks — no file content read.
    if _dir_has_file(state_dir, "sessions", ".yaml"):
        return True
    if _dir_has_file(root, "journal", ".md"):
        return True
    if _dir_has_file(state_dir, "sessions/archive", ".yaml"):
        return True
    if _dir_has_file(state_dir, "summaries", ".yaml"):
        return True
    if _dir_has_file(state_dir, "milestones", ".yaml"):
        return True
    if _dir_has_file(root, "progress-reports", ".md"):
        return True
    if _dir_has_file(state_dir, "offline-guides"):
        return True

    # Parking lot: compare against pristine template. rstrip so a trailing
    # newline drift between platforms doesn't trigger a false positive.
    parking_lot = root / "parking-lot.md"
    if parking_lot.exists():
        try:
            if parking_lot.read_text(encoding="utf-8").rstrip() != TEMPLATES["parking-lot.md"].rstrip():
                return True
        except OSError:
            pass

    # YAML parses — most expensive checks go last. A parse failure (corrupt-but-
    # present state) must read as "state present" (return True), NOT swallowed
    # into the fall-through `return False`; otherwise --force WIPES a recoverable
    # file. Narrow the except to the parse/IO errors we expect and fail safe.
    profile_path = state_dir / "learner-profile.yaml"
    if profile_path.exists():
        try:
            data = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
            name = data.get("name")
            if name and str(name).strip():
                return True
        except (OSError, yaml.YAMLError):
            # Corrupt or unreadable — refuse to clobber it.
            return True

    # Resource tracker: any populated `resources` list counts as user data.
    # The pristine template has `resources: []`; --force would wipe anything
    # the learner added.
    rt_path = state_dir / "resource-tracker.yaml"
    if rt_path.exists():
        try:
            data = yaml.safe_load(rt_path.read_text(encoding="utf-8")) or {}
            if data.get("resources"):
                return True
        except (OSError, yaml.YAMLError):
            # Corrupt or unreadable — refuse to clobber it.
            return True

    return False


# ---------------------------------------------------------------------------
# Demo seeding (--demo): a realistic mid-Phase-B sample learner
# ---------------------------------------------------------------------------
#
# `--demo` populates state/ with a coherent sample learner ("Alex Demo") so a
# prospective user can preview a fully-populated system without running
# onboarding. Every value below is chosen so that scripts/validate-state.py
# reports 0 warnings AND 0 failures — respecting each invariant that script
# enforces: the acquired error-rate gate (< 0.10) and performance_unscaffolded
# == competent, the 3+-session acquisition floor (all acquired grammar has
# practice_count >= 3), passive_known >= active_known, receptive vs
# resource-tracker level agreement (L2 / R2), the D-11 homework-load counters
# pinned at 0, and the Phase-B entry prerequisites (A-01/A-02/A-04) all
# acquired. Dates are fixed historical strings; NONE are compared against
# "today" by the validator — learner_interest is deliberately omitted so its
# 28-day staleness check can never start firing as the demo ages on disk.
#
# route_session(state) boots this seed into "first-session" (Row 1: no session
# logs exist), which is the sane deterministic route for a fresh preview with
# last_session_date null and an empty sessions/ directory.

# Grammar: 10 Phase-A concepts acquired (placement-acquired at early-B, then
# reinforced — practice_count 4-8, error rates < 0.10), 2 early-Phase-B
# concepts practicing (error rates 0.15-0.30). integration_tested_with refs all
# resolve to concepts present in the skill map.
DEMO_GRAMMAR = {
    "A-00-communication-repair": dict(
        status="acquired", introduced_date="2026-05-02", last_practiced="2026-06-26",
        practice_count=8, error_rate_drills=0.03, error_rate_production=0.05,
        error_trend="stable", performance_scaffolded="competent",
        performance_unscaffolded="competent", integration_tested_with=[]),
    "A-01-present-regular": dict(
        status="acquired", introduced_date="2026-05-02", last_practiced="2026-06-28",
        practice_count=8, error_rate_drills=0.04, error_rate_production=0.06,
        error_trend="stable", performance_scaffolded="competent",
        performance_unscaffolded="competent",
        integration_tested_with=["A-02-ser-vs-estar", "A-07-present-irregular-common"]),
    "A-02-ser-vs-estar": dict(
        status="acquired", introduced_date="2026-05-05", last_practiced="2026-06-28",
        practice_count=7, error_rate_drills=0.05, error_rate_production=0.08,
        error_trend="stable", performance_scaffolded="competent",
        performance_unscaffolded="competent",
        integration_tested_with=["A-01-present-regular"]),
    "A-03-gender-agreement": dict(
        status="acquired", introduced_date="2026-05-07", last_practiced="2026-06-22",
        practice_count=6, error_rate_drills=0.05, error_rate_production=0.08,
        error_trend="improving", performance_scaffolded="competent",
        performance_unscaffolded="competent", integration_tested_with=[]),
    "A-04-articles-prepositions": dict(
        status="acquired", introduced_date="2026-05-10", last_practiced="2026-06-20",
        practice_count=6, error_rate_drills=0.06, error_rate_production=0.08,
        error_trend="stable", performance_scaffolded="competent",
        performance_unscaffolded="competent", integration_tested_with=[]),
    "A-05-basic-questions": dict(
        status="acquired", introduced_date="2026-05-12", last_practiced="2026-06-18",
        practice_count=5, error_rate_drills=0.04, error_rate_production=0.07,
        error_trend="stable", performance_scaffolded="competent",
        performance_unscaffolded="competent", integration_tested_with=[]),
    "A-06-gustar-type-verbs": dict(
        status="acquired", introduced_date="2026-05-15", last_practiced="2026-06-15",
        practice_count=5, error_rate_drills=0.06, error_rate_production=0.09,
        error_trend="improving", performance_scaffolded="competent",
        performance_unscaffolded="competent", integration_tested_with=[]),
    "A-07-present-irregular-common": dict(
        status="acquired", introduced_date="2026-05-17", last_practiced="2026-06-27",
        practice_count=7, error_rate_drills=0.05, error_rate_production=0.08,
        error_trend="stable", performance_scaffolded="competent",
        performance_unscaffolded="competent",
        integration_tested_with=["A-01-present-regular"]),
    "A-08-numbers-quantifiers": dict(
        status="acquired", introduced_date="2026-05-20", last_practiced="2026-06-12",
        practice_count=4, error_rate_drills=0.05, error_rate_production=0.07,
        error_trend="stable", performance_scaffolded="competent",
        performance_unscaffolded="competent", integration_tested_with=[]),
    "A-09-accent-stress-rules": dict(
        status="acquired", introduced_date="2026-05-22", last_practiced="2026-06-10",
        practice_count=4, error_rate_drills=0.07, error_rate_production=0.09,
        error_trend="stable", performance_scaffolded="competent",
        performance_unscaffolded="competent", integration_tested_with=[]),
    "B-01-preterite-regular": dict(
        status="practicing", introduced_date="2026-06-14", last_practiced="2026-06-28",
        practice_count=3, error_rate_drills=0.18, error_rate_production=0.25,
        error_trend="improving", performance_scaffolded="competent",
        performance_unscaffolded="struggling", integration_tested_with=[]),
    "B-02-preterite-irregular": dict(
        status="practicing", introduced_date="2026-06-21", last_practiced="2026-06-27",
        practice_count=2, error_rate_drills=0.24, error_rate_production=0.30,
        error_trend="stable", performance_scaffolded="struggling",
        performance_unscaffolded="struggling", integration_tested_with=[]),
}

# Vocabulary: 3 acquired tier-1 clusters (error_rate_production < 0.10) + 1
# practicing tier-2 cluster. passive_known >= active_known everywhere.
DEMO_VOCAB = {
    "tier1-greetings-introductions": dict(
        status="acquired", words_introduced=49, passive_known=47, active_known=42,
        weak_production=["presentarse"], weak_recognition=[], last_practiced="2026-06-20",
        error_tracking=dict(error_rate_production=0.04,
                            common_errors=["formality: tú vs usted in greetings"],
                            last_observed="2026-06-20")),
    "tier1-numbers-time-dates": dict(
        status="acquired", words_introduced=77, passive_known=70, active_known=60,
        weak_production=["la madrugada"], weak_recognition=[], last_practiced="2026-06-18",
        error_tracking=dict(error_rate_production=0.05,
                            common_errors=["24-hour vs 12-hour time"],
                            last_observed="2026-06-18")),
    "tier1-food-restaurant": dict(
        status="acquired", words_introduced=64, passive_known=58, active_known=48,
        weak_production=["la cuenta", "el mesero"], weak_recognition=[],
        last_practiced="2026-06-24",
        error_tracking=dict(error_rate_production=0.06,
                            common_errors=["ordering register (¿me da...? vs quiero)"],
                            last_observed="2026-06-24")),
    "tier2-home-household": dict(
        status="practicing", words_introduced=30, passive_known=28, active_known=18,
        weak_production=["el fregadero", "la cobija"], weak_recognition=["el enchufe"],
        last_practiced="2026-06-28",
        error_tracking=dict(error_rate_production=0.16,
                            common_errors=["gender on appliance nouns"],
                            last_observed="2026-06-28")),
}

# Receptive skills: around L2 / R2, with hours_at_level <= hours_total. Kept in
# lockstep with resource-tracker.input_summary levels (check_resource_skill_map_levels).
DEMO_RECEPTIVE = {
    "listening": dict(
        current_level="L2", comprehension_quality="main_ideas",
        hours_at_level=12.0, hours_total=22.5,
        level_up_evidence=["2026-06-15: followed a Dreaming Spanish Beginner story without rewinding"],
        level_history=[{"level": "L1", "date": "2026-05-01"},
                       {"level": "L2", "date": "2026-06-05"}]),
    "reading": dict(
        current_level="R2", comprehension_quality="main_ideas",
        lookup_frequency="occasional", hours_at_level=5.0, hours_total=8.0,
        level_up_evidence=["2026-06-19: finished a graded-reader chapter with occasional lookups"],
        level_history=[{"level": "R1", "date": "2026-05-01"},
                       {"level": "R2", "date": "2026-06-12"}]),
}

DEMO_OVERALL = dict(
    cefr_estimate="A2", estimated_active_vocabulary=168,
    estimated_passive_vocabulary=203, production_gap=35,
    strongest_skill="listening", weakest_skill="speaking",
    last_formal_assessment="2026-05-01")

DEMO_FLUENCY = dict(
    speaking_pace="slow-deliberate", hesitation_frequency="occasional",
    self_correction_rate="high", circumlocution="occasional",
    willingness_to_risk="tries and sometimes fails",
    thinking_language="still translating from English")

DEMO_PROFILE = dict(
    name="Alex Demo",
    native_language="English",
    target_dialect="Mexican",
    started="2026-05-01",
    primary_goal="Conversational fluency for travel and connecting with family in Mexico",
    target_level="B2",
    milestone_goals=[
        "Order a meal and chat with the staff in Mexico City",
        "Hold a 10-minute phone call with a Spanish-speaking relative",
    ],
    graduation_criteria="Comfortable in unscripted daily conversations without switching to English",
    typical_weekday_minutes=30,
    typical_weekend_minutes=45,
    preferred_session_time="evening",
    max_new_concepts_per_week=2,
    weekly_review_day="Sunday",
    grammar_preference="examples-first",
    error_correction_preference="gentle-inline",
    vocabulary_retention_method="contextual",
    motivation_style="encouragement-driven",
    energy_pattern="Higher energy on weekday evenings; lighter on weekends",
    calibration=dict(self_report_accuracy=0.7, tendency="accurate", trust_weight=0.6),
    motivation=dict(
        current_level="high", streak_days=3, longest_streak=8, total_sessions=14,
        days_since_last_milestone=4, plateau_risk=False,
        high_motivation_triggers=["visible roadmap progress", "real conversations"],
        low_motivation_triggers=["long grammar drills"],
        preferred_recovery="a quick win followed by a real-world debrief"),
    input_hours=dict(listening_total=22.5, reading_total=8.0, last_updated="2026-06-28"),
    tools=dict(srs="Anki", pronunciation="Speechling", conversation_partner="",
               listening_primary="Dreaming Spanish",
               reading_current="Short Stories in Spanish (Olly Richards)"),
    notes="Sample learner seeded by `init-student.py --demo` to preview a populated system. Not a real learner.",
    initial_placement=dict(
        level="early-B", date="2026-05-01", self_report="intermediate",
        grammar_result="early-B", vocabulary_observation="narrow",
        reading_result="at-expected", confidence="medium",
        evidence_summary=("Comfortable with the present tense and ser/estar; beginning the "
                          "past tenses. Placed at early B with Phase A concepts pre-acquired.")),
)

DEMO_SCHEDULE = dict(
    current_phase="B-conversational",
    current_week=6,
    onboarding_complete=True,
    current_onboarding_session=None,
    last_session_date=None,
    autonomy_level="guided",
    active_grammar=dict(primary="B-01-preterite-regular", secondary="A-02-ser-vs-estar",
                        maintenance=["A-01-present-regular", "A-07-present-irregular-common"]),
    active_vocabulary=dict(primary="tier2-home-household",
                           review=["tier1-greetings-introductions", "tier1-food-restaurant"]),
    active_pronunciation=dict(focus="rr-trill"),
    active_writing=dict(current_level="sentence", journal_active=True),
    weekly_topic=dict(topic="Cooking and eating at home",
                      vocabulary_cluster="tier2-home-household",
                      grammar_reinforcement="B-01-preterite-regular", started="2026-06-22"),
    fluency_accuracy_balance="balanced",
    fluency_days_this_week=0,
    last_fluency_day=None,
    grammar_queue=["B-03-imperfect", "B-04-preterite-vs-imperfect"],
    vocabulary_queue=["tier2-work-office"],
    placement_validation=dict(active=False, confidence="validated", sessions_completed=3,
                              listening_baseline_set=True, total_downgrades=0, queue=[]),
    study_time_budget=dict(daily_minimum=15, daily_target=30, daily_maximum=45,
                           weekly_goal=180, today_stretch=0),
    session_number=14,
    consecutive_too_much_count=0,
    consecutive_just_right_count=0,
    just_right_streak=0,
    topic_history=[
        {"topic_id": "daily-routines", "week": 4, "date_started": "2026-06-01"},
        {"topic_id": "cooking-and-eating", "week": 6, "date_started": "2026-06-22"},
    ],
)

DEMO_HEALTH = dict(
    concepts_requiring_reteach_total=1,
    average_sessions_to_acquire=4,
    reteach_rate_30d=0.08,
    homework_completion_rate_30d=0.85,
    homework_reported_difficulty_avg=3.0,
    assignment_skip_patterns=[],
    days_in_current_phase=21,
    concepts_acquired_per_month=6,
    concepts_in_practicing_simultaneously=2,
    average_session_duration_30d=32,
    session_frequency_30d=4.0,
    learner_initiated_topics_30d=3,
    sessions_rated_too_easy_30d=1,
    sessions_rated_too_hard_30d=1,
    anki_estimated_deck_size=180,
    anki_estimated_daily_review_minutes=12,
    last_validation_issues=[],
    load_adjustments=[],
    auto_fixes=[],
    placement_validation_metrics=dict(
        placement_level="early-B", initial_confidence="medium",
        total_concepts_validated=8, total_downgrades=0,
        final_assessment="placement-confirmed", validation_completed="2026-05-10"),
    goal_tracking=dict(
        primary_goal_progress="on-track", estimated_weeks_remaining=18,
        concepts_remaining_for_next_phase=6, concepts_remaining_for_target_level=40,
        current_acquisition_rate=1.5, last_goal_review="2026-06-28", milestone_progress=[]),
    session_difficulty_tracking=dict(
        last_rating="just-right", consecutive_too_easy=0, consecutive_too_hard=0,
        recent_ratings=["just-right", "too-easy", "just-right"]),
    maintenance_sessions_total=0,
    regressions_detected_in_maintenance=0,
    last_system_review="2026-06-28",
)

DEMO_RESOURCE_TRACKER = dict(
    input_summary=dict(total_listening_hours=22.5, total_reading_hours=8.0,
                       current_listening_level="L2", current_reading_level="R2"),
    resources=[
        dict(name="Dreaming Spanish", type="listening", level_range=["L1", "L3"],
             sessions_assigned=12, sessions_completed=10, hours_logged=18.0,
             comprehension_trend="improving", vocabulary_extracted=40,
             last_assigned="2026-06-28", last_completed="2026-06-28",
             learner_engagement="enthusiastic", notes="Superbeginner → Beginner playlists"),
        dict(name="Short Stories in Spanish (Olly Richards)", type="reading",
             level_range=["R1", "R2"], sessions_assigned=6, sessions_completed=5,
             hours_logged=6.5, comprehension_trend="stable", vocabulary_extracted=22,
             last_assigned="2026-06-25", last_completed="2026-06-25",
             learner_engagement="neutral", notes=""),
    ],
)


def _deep_update(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base*. Nested dicts merge key-by-key;
    everything else (scalars, lists) is replaced wholesale. Mutates and returns
    *base*."""
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def _demo_state_doc(schema_name: str, overrides: dict) -> dict:
    """Build a demo state document: start from the schema's default template so
    every field the validator's required-field check expects is present, then
    layer the demo overrides on top."""
    base = yaml.safe_load(generate_template_from_schema(schema_name)) or {}
    return _deep_update(base, overrides)


def _demo_skill_map() -> dict:
    """Build the demo skill map from the pristine tracked template.

    Starts from state/skill-map.template.yaml (all concepts present with every
    required field) so nothing is missing, then overrides the ~12 practiced
    grammar concepts, the 4 populated vocabulary clusters, receptive skills,
    overall estimates, and fluency metrics. The template is read from the repo
    (ROOT) rather than STATE_DIR, since STATE_DIR may be redirected to an empty
    scratch directory via TUTOR_STATE_DIR."""
    template_path = ROOT / "state" / "skill-map.template.yaml"
    data = yaml.safe_load(template_path.read_text(encoding="utf-8"))

    grammar = data["grammar"]
    # The template shares one anchored empty list across every
    # integration_tested_with; give each entry its own list so overrides and the
    # YAML dump can't alias.
    for entry in grammar.values():
        if isinstance(entry, dict):
            entry["integration_tested_with"] = list(entry.get("integration_tested_with") or [])
    for cid, override in DEMO_GRAMMAR.items():
        grammar[cid].update(override)

    vocab = data["vocabulary"]
    for cid, override in DEMO_VOCAB.items():
        override = dict(override)
        et = override.pop("error_tracking", None)
        vocab[cid].update(override)
        if et is not None:
            vocab[cid]["error_tracking"].update(et)

    data["receptive_skills"] = DEMO_RECEPTIVE
    data["overall_estimates"].update(DEMO_OVERALL)
    data["fluency_metrics"].update(DEMO_FLUENCY)
    return data


def seed_demo(root: Path, state_dir: Path) -> None:
    """Write the demo learner's state into *state_dir* (state YAMLs + an empty
    sessions/ directory) and a pristine parking-lot under *root*."""
    state_dir.mkdir(parents=True, exist_ok=True)
    sessions = state_dir / "sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    # Keep an empty (but present) sessions/ dir: validate-state WARNs if it is
    # missing, and route_session boots a log-free seed into "first-session".
    (sessions / ".gitkeep").write_text("", encoding="utf-8")

    for name, overrides in (("learner-profile", DEMO_PROFILE),
                            ("schedule", DEMO_SCHEDULE),
                            ("system-health", DEMO_HEALTH),
                            ("resource-tracker", DEMO_RESOURCE_TRACKER)):
        data = _demo_state_doc(name, overrides)
        header = SCHEMA_TEMPLATES[f"state/{name}.yaml"]["header"]
        content = header + yaml.dump(data, default_flow_style=False,
                                     allow_unicode=True, sort_keys=False)
        atomic_write(state_dir / f"{name}.yaml", content)
        print(green(f"  SEEDED: {name}.yaml"))

    sm_content = SKILL_MAP_HEADER + yaml.dump(_demo_skill_map(), default_flow_style=False,
                                              allow_unicode=True, sort_keys=False)
    atomic_write(state_dir / "skill-map.yaml", sm_content)
    print(green("  SEEDED: skill-map.yaml"))

    atomic_write(root / "parking-lot.md", TEMPLATES["parking-lot.md"])
    print(green("  SEEDED: parking-lot.md"))


def _clear_demo_data(root: Path, state_dir: Path) -> None:
    """Remove leftover session/journal data (except .gitkeep) so a --force demo
    reseed lands on a clean slate. Mirrors the plain-reset clear set, rooted at
    the demo's state_dir / root."""
    for d in (state_dir / "sessions", state_dir / "sessions" / "archive",
              state_dir / "summaries", state_dir / "milestones",
              state_dir / "offline-guides", root / "journal",
              root / "progress-reports"):
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.is_file() and f.name != ".gitkeep":
                f.unlink()


def run_demo(force: bool) -> int:
    """Seed the demo learner. Returns a process exit code.

    Writes state to STATE_DIR (honoring TUTOR_STATE_DIR) and treats
    STATE_DIR.parent as the install root — which equals ROOT in normal use and
    lets a test redirect the whole seed into a scratch dir. Refuses to overwrite
    real learner data unless *force* is set (taking a recovery snapshot first)."""
    state_dir = STATE_DIR
    root = STATE_DIR.parent

    if has_existing_learner_data(root, state_dir=state_dir):
        if not force:
            print(red(
                f"Existing learner data detected under {root} — refusing to "
                f"overwrite it with demo data.\nRe-run with `--demo --force` to "
                f"replace it (a recovery snapshot is taken first)."))
            return 1
        print(yellow("\n=== Taking recovery snapshot before demo overwrite ==="))
        snap = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "snapshot-state.py"), "snapshot"],
            cwd=str(ROOT),
        )
        if snap.returncode != 0:
            print(red("Snapshot failed — cannot safely overwrite. Aborting."))
            return 1
        _clear_demo_data(root, state_dir)
    else:
        print(green("No prior learner detected — seeding demo learner into clean state."))

    print("\n=== Seeding demo learner (Alex Demo — mid-Phase-B, Mexican dialect) ===")
    seed_demo(root, state_dir)

    # Vault preview is a bonus for a real install; skip it when STATE_DIR is
    # redirected (tests) since generate-vault.py writes to ROOT/vault regardless.
    if state_dir == ROOT / "state":
        vault_script = ROOT / "scripts" / "generate-vault.py"
        if vault_script.exists():
            r = subprocess.run([sys.executable, str(vault_script), "--full"],
                               cwd=str(ROOT), capture_output=True, text=True)
            if r.returncode == 0:
                print(green(f"  {r.stdout.strip()}"))
            else:
                print(yellow(f"  Vault generation skipped (non-fatal): {r.stderr.strip()}"))

    print(green(
        "\nDemo learner 'Alex Demo' is ready. Start a session to preview the "
        "populated system, or run `python3 scripts/init-student.py` to reset to "
        "a blank learner."))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset all student data to clean templates.")
    parser.add_argument("--force", action="store_true",
                        help="Skip the interactive confirmation prompt (a recovery snapshot is taken whenever prior learner data is detected)")
    parser.add_argument("--demo", action="store_true",
                        help="Seed a realistic sample learner (Alex Demo — mid-Phase-B, Mexican dialect) instead of blank templates, so you can preview a populated system without running onboarding. Refuses to overwrite existing learner data unless --force is also given (a recovery snapshot is taken first).")
    args = parser.parse_args()

    if args.demo:
        sys.exit(run_demo(force=args.force))

    # --- Step 0: Detect prior learner state (D-09 gate) ---
    profile_path = ROOT / "state" / "learner-profile.yaml"
    profile_data = load_yaml(profile_path) or {}
    name = profile_data.get("name")
    has_prior_learner = has_existing_learner_data(ROOT)

    if has_prior_learner:
        # --- Step 1: Snapshot BEFORE any writes (D-07, unconditional even under --force) ---
        print(yellow("\n=== Taking recovery snapshot ==="))
        snapshot_result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "snapshot-state.py"), "snapshot"],
            cwd=str(ROOT),
        )
        if snapshot_result.returncode != 0:
            print(red("Snapshot failed — cannot safely reset. Aborting."))
            sys.exit(1)

        # --- Step 2: Gather pre-wipe state for display ---
        schedule_data = load_yaml(ROOT / "state" / "schedule.yaml") or {}
        last_session = schedule_data.get("last_session_date", None)
        if not last_session:
            # Fall back to most recent session log filename
            session_dir = ROOT / "state" / "sessions"
            if session_dir.exists():
                logs = sorted(f.stem for f in session_dir.glob("*.yaml") if f.name != ".gitkeep")
                last_session = logs[-1] if logs else "unknown"
            else:
                last_session = "unknown"

        session_count = 0
        session_dir = ROOT / "state" / "sessions"
        if session_dir.exists():
            session_count = len([f for f in session_dir.glob("*.yaml") if f.name != ".gitkeep"])

        journal_count = 0
        journal_dir = ROOT / "journal"
        if journal_dir.exists():
            journal_count = len([f for f in journal_dir.glob("*.md") if f.name != ".gitkeep"])

        snapshot_path = str((ROOT / "state" / ".snapshot").relative_to(ROOT)) + "/"

        # --- Step 3: Confirmation (D-08 type-to-confirm, D-10 --force skips prompt) ---
        if not args.force:
            print(f"\nAbout to erase all progress for: {name or '(unnamed learner — session/journal data present)'}")
            print(f"  Last session: {last_session}")
            print(f"  {session_count} session log(s) will be cleared")
            print(f"  {journal_count} journal entry/entries will be cleared")
            print(f"  Recovery snapshot saved to: {snapshot_path}")
            has_name = bool(name and str(name).strip())
            if has_name:
                print(f'\nType the learner name "{name}" or "RESET" to confirm:')
            else:
                print('\nType "RESET" to confirm:')
            answer = input("> ").strip()
            if not (answer == "RESET" or (has_name and answer == str(name))):
                print("Aborted.")
                sys.exit(0)
        else:
            print(yellow(f"  --force: skipping confirmation for learner '{name}'"))
    else:
        # --- Fresh install path (D-09): no snapshot, no prompt ---
        print(green("No prior learner detected — initializing clean state."))

    # --- Proceed with writes (unchanged from original) ---
    print("\n=== Resetting state files ===")
    for rel_path, content in TEMPLATES.items():
        (ROOT / rel_path).write_text(content, encoding="utf-8")
        print(green(f"  RESET: {rel_path}"))
    reset_skill_map()

    print("\n=== Clearing session data ===")
    total_removed = sum(clear_directory(d) for d in [
        "state/sessions", "state/sessions/archive", "state/summaries",
        "state/milestones", "state/offline-guides", "journal", "progress-reports"])

    print("\n=== Regenerating vault ===")
    vault_script = ROOT / "scripts" / "generate-vault.py"
    vault_failed = False
    if vault_script.exists():
        r = subprocess.run([sys.executable, str(vault_script), "--full"],
                           cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode == 0:
            print(green(f"  {r.stdout.strip()}"))
        else:
            print(red(f"  Vault generation failed: {r.stderr.strip()}"))
            vault_failed = True
    else:
        print(yellow("  SKIP: generate-vault.py not found"))

    print("\n=== Summary ===")
    print(f"  State files reset: {len(TEMPLATES) + 1}")  # +1 for skill-map
    print(f"  Data files removed: {total_removed}")
    if vault_failed:
        print(red("\nState was reset, but vault generation FAILED — run "
                  "`python3 scripts/generate-vault.py --full` and fix the error "
                  "before the first session."))
        sys.exit(1)
    print(green("\nStudent data has been reset to a clean state."))


if __name__ == "__main__":
    main()
