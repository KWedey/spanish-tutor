#!/usr/bin/env python3
"""Validate state files against expected schemas and cross-references."""
import argparse, re, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr); sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
CURRICULUM = ROOT / "curriculum"
PHASE_DIRS = {"A": "A-foundation", "B": "B-conversational", "C": "C-intermediate", "D": "D-advanced"}
TIER_DIRS = {"1": "tier1-survival", "2": "tier2-daily-life", "3": "tier3-social", "4": "tier4-abstract"}

HEALTH_COUNTERS = [
    "concepts_requiring_reteach_total", "average_sessions_to_acquire", "reteach_rate_30d",
    "homework_completion_rate_30d", "homework_reported_difficulty_avg", "days_in_current_phase",
    "concepts_acquired_per_month", "concepts_in_practicing_simultaneously",
    "average_session_duration_30d", "session_frequency_30d", "learner_initiated_topics_30d",
    "sessions_rated_too_easy_30d", "sessions_rated_too_hard_30d",
    "anki_estimated_deck_size", "anki_estimated_daily_review_minutes",
]

results: list[tuple[str, str]] = []
def pass_(msg): results.append(("PASS", msg))
def warn(msg):  results.append(("WARN", msg))
def fail(msg):  results.append(("FAIL", msg))

def load_yaml(path: Path) -> dict | None:
    if not path.exists():
        fail(f"Missing file: {path.relative_to(ROOT)}"); return None
    try:
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            fail(f"Expected mapping at top level: {path.relative_to(ROOT)}"); return None
        pass_(f"YAML syntax OK: {path.relative_to(ROOT)}")
        return data
    except yaml.YAMLError as e:
        fail(f"YAML syntax error in {path.relative_to(ROOT)}: {e}"); return None


def grammar_path(cid: str) -> Path:
    return CURRICULUM / "grammar" / PHASE_DIRS.get(cid[0], "") / f"{cid[2:]}.md"

def vocab_path(cid: str) -> Path:
    return CURRICULUM / "vocabulary" / TIER_DIRS.get(cid[4], "") / f"{cid[6:]}.md"


# --- 1. Required-field checks ------------------------------------------------

def check_learner_profile(data: dict, has_sessions: bool) -> None:
    for f in ("name", "native_language", "target_dialect"):
        if f not in data:       fail(f"learner-profile: missing required field '{f}'")
        elif has_sessions and not data[f]: warn(f"learner-profile: '{f}' is empty after session 1")
        else:                   pass_(f"learner-profile: '{f}' present")


def check_skill_map(data: dict) -> None:
    grammar = data.get("grammar", {})
    if not grammar:
        fail("skill-map: 'grammar' section missing or empty")
    else:
        for cid, entry in grammar.items():
            if isinstance(entry, dict):
                for f in ("status", "practice_count", "prerequisites"):
                    if f not in entry:
                        fail(f"skill-map grammar '{cid}': missing '{f}'")
        pass_(f"skill-map: checked {len(grammar)} grammar entries for required fields")
    vocab = data.get("vocabulary", {})
    if not vocab: fail("skill-map: 'vocabulary' section missing or empty")
    else:         pass_(f"skill-map: {len(vocab)} vocabulary clusters present")


def check_schedule(data: dict) -> None:
    for f in ("current_phase", "onboarding_complete", "fluency_accuracy_balance"):
        if f not in data: fail(f"schedule: missing required field '{f}'")
        else:             pass_(f"schedule: '{f}' present")


def check_system_health(data: dict) -> None:
    missing = [f for f in HEALTH_COUNTERS if f not in data]
    if missing:
        for f in missing: fail(f"system-health: missing counter field '{f}'")
    else:
        pass_(f"system-health: all {len(HEALTH_COUNTERS)} counter fields present")


# --- 2. Cross-reference checks -----------------------------------------------

def check_curriculum_cross_refs(sm: dict) -> None:
    for section, resolver, label in [
        ("grammar", grammar_path, "grammar concepts"),
        ("vocabulary", vocab_path, "vocabulary clusters"),
    ]:
        items = sm.get(section, {})
        missing = [(c, resolver(c).relative_to(ROOT)) for c in items if not resolver(c).exists()]
        if missing:
            for cid, p in missing: fail(f"{label.title().rstrip('s')} '{cid}' has no curriculum file at {p}")
        else:
            pass_(f"All {len(items)} {label} have matching curriculum files")


def check_schedule_refs(sched: dict, sm: dict) -> None:
    primary = sched.get("active_grammar", {}).get("primary", "")
    if primary and primary not in sm.get("grammar", {}):
        fail(f"schedule active_grammar.primary '{primary}' not found in skill-map")
    elif primary:
        pass_(f"schedule active_grammar.primary '{primary}' exists in skill-map")


def check_vocab_passive_active(sm: dict) -> None:
    violations = []
    for cid, e in sm.get("vocabulary", {}).items():
        if not isinstance(e, dict): continue
        p, a = (e.get("passive_known", 0) or 0), (e.get("active_known", 0) or 0)
        if p < a: violations.append((cid, p, a))
    if violations:
        for cid, p, a in violations:
            fail(f"Vocabulary '{cid}': passive_known ({p}) < active_known ({a})")
    else:
        pass_("All vocabulary clusters: passive_known >= active_known")


# --- 3. Consistency checks ----------------------------------------------------

def check_acquired_consistency(sm: dict) -> None:
    grammar = sm.get("grammar", {})
    acquired = []
    for cid, e in grammar.items():
        if not isinstance(e, dict) or e.get("status") != "acquired": continue
        acquired.append(cid)
        err = e.get("error_rate_production")
        if err is not None and err > 0.15:
            fail(f"Grammar '{cid}': acquired but error_rate_production={err} (> 0.15)")
        perf = e.get("performance_unscaffolded")
        if perf is not None and perf != "competent":
            fail(f"Grammar '{cid}': acquired but performance_unscaffolded='{perf}' (expected 'competent')")
    if acquired: pass_(f"Checked {len(acquired)} acquired concepts for consistency")
    else:        pass_("No acquired concepts to check (all unseen/practicing)")


def check_performance_enums(sm: dict) -> None:
    valid_perf = {None, "struggling", "competent"}
    grammar = sm.get("grammar", {})
    for cid, e in grammar.items():
        if not isinstance(e, dict): continue
        for field in ("performance_scaffolded", "performance_unscaffolded"):
            val = e.get(field)
            if val not in valid_perf:
                fail(f"Grammar '{cid}': {field}='{val}' is not a valid value (expected: null, struggling, or competent)")
    pass_("Performance enum values are valid")


def check_session_filenames() -> None:
    sdir = STATE / "sessions"
    if not sdir.exists():
        warn("state/sessions/ directory does not exist"); return
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}\.yaml$")
    bad = [f.name for f in sdir.iterdir() if f.is_file() and not f.name.startswith(".") and not date_re.match(f.name)]
    if bad:
        for name in bad: warn(f"Session file '{name}' does not match YYYY-MM-DD.yaml pattern")
    else:
        n = sum(1 for f in sdir.iterdir() if f.is_file() and not f.name.startswith("."))
        pass_(f"All {n} session files have valid date filenames" if n else "No session files yet")


def check_carryover_concepts(sched: dict, sm: dict) -> None:
    carryover = sched.get("carryover_concepts") or []
    if not carryover:
        pass_("No carryover concepts to check")
        return
    grammar = sm.get("grammar", {})
    for cid in carryover:
        if cid not in grammar:
            fail(f"Carryover concept '{cid}' not found in skill-map grammar section")
        else:
            entry = grammar[cid]
            if isinstance(entry, dict):
                status = entry.get("status")
                if status in ("acquired", "automatic"):
                    warn(f"Carryover concept '{cid}' has status '{status}' — should be removed from carryover list")
    pass_(f"Checked {len(carryover)} carryover concepts")


def check_schedule_enums(sched: dict) -> None:
    valid_phases = {"A-foundation", "B-conversational", "C-intermediate", "D-advanced"}
    phase = sched.get("current_phase", "")
    if phase and phase not in valid_phases:
        fail(f"schedule.current_phase='{phase}' is not a valid phase")
    valid_balance = {"accuracy-leaning", "balanced", "fluency-leaning"}
    balance = sched.get("fluency_accuracy_balance", "")
    if balance and balance not in valid_balance:
        fail(f"schedule.fluency_accuracy_balance='{balance}' is not valid")
    week = sched.get("current_week", 0)
    if isinstance(week, int) and week < 0:
        fail(f"schedule.current_week={week} is negative")
    pass_("Schedule enum values are valid")


def check_integration_tested_with(sm: dict) -> None:
    grammar = sm.get("grammar", {})
    grammar_ids = set(grammar.keys())
    for cid, entry in grammar.items():
        if not isinstance(entry, dict): continue
        # Legacy boolean field check
        if "integration_tested" in entry:
            warn(f"Grammar '{cid}': legacy field 'integration_tested' found — should be 'integration_tested_with' (list)")
        itw = entry.get("integration_tested_with")
        if itw is None:
            # Field simply absent — not a blocker, schema may be partial
            pass
        elif not isinstance(itw, list):
            fail(f"Grammar '{cid}': 'integration_tested_with' should be a list, got {type(itw).__name__}")
        else:
            for ref in itw:
                if ref not in grammar_ids:
                    fail(f"Grammar '{cid}': 'integration_tested_with' references unknown concept '{ref}'")
    pass_("Checked integration_tested_with format for all grammar concepts")


def check_acquired_zero_practice(sm: dict, profile: dict) -> None:
    grammar = sm.get("grammar", {})
    placement_level = None
    if isinstance(profile, dict):
        placement_level = (profile.get("initial_placement") or {}).get("level") or None
    # Extract the phase letter from a placement level string like "B-conversational" or just "B"
    placement_phase: str | None = None
    if placement_level:
        placement_phase = placement_level[0].upper() if placement_level else None

    phase_order = {"A": 0, "B": 1, "C": 2, "D": 3}

    for cid, entry in grammar.items():
        if not isinstance(entry, dict): continue
        if entry.get("status") != "acquired": continue
        if (entry.get("practice_count") or 0) != 0: continue
        # Concept is acquired with practice_count == 0
        concept_phase = cid[0].upper() if cid else None
        if (placement_phase
                and concept_phase in phase_order
                and placement_phase in phase_order
                and phase_order[concept_phase] < phase_order[placement_phase]):
            # Below placement level — exempt
            pass_(f"Grammar '{cid}': acquired with practice_count=0 (placement-exempt: below {placement_phase}-level placement)")
        else:
            warn(f"Grammar '{cid}': acquired with practice_count=0 — cannot acquire without practice unless placement-validated")


def check_placement_validation_consistency(sched: dict) -> None:
    pv = sched.get("placement_validation") or {}
    pv_active = pv.get("active", False)
    onboarding_complete = sched.get("onboarding_complete", False)
    if pv_active and not onboarding_complete:
        fail("Placement validation active but onboarding not complete — contradictory state")
    elif pv_active:
        pass_("Placement validation active and onboarding_complete is true — consistent")
    else:
        pass_("Placement validation not active — no consistency check needed")


def check_receptive_skills(skill_map: dict) -> None:
    """Validate receptive_skills schema and level values."""
    rs = skill_map.get('receptive_skills', {})
    if not rs:
        warn('receptive_skills section missing from skill-map')
        return

    valid_listening = {'L1', 'L2', 'L3', 'L4', 'L5'}
    valid_reading = {'R1', 'R2', 'R3', 'R4', 'R5'}
    valid_quality = {None, 'gist', 'main_ideas', 'details', 'inference'}
    valid_lookup = {None, 'frequent', 'occasional', 'rare', 'none'}

    listening = rs.get('listening', {})
    reading = rs.get('reading', {})

    level = listening.get('current_level')
    if level and level not in valid_listening:
        fail(f'receptive_skills.listening.current_level invalid: {level} (expected L1-L5)')
    else:
        pass_('receptive_skills.listening.current_level valid')

    quality = listening.get('comprehension_quality')
    if quality not in valid_quality:
        fail(f'receptive_skills.listening.comprehension_quality invalid: {quality}')

    level = reading.get('current_level')
    if level and level not in valid_reading:
        fail(f'receptive_skills.reading.current_level invalid: {level} (expected R1-R5)')
    else:
        pass_('receptive_skills.reading.current_level valid')

    lookup = reading.get('lookup_frequency')
    if lookup not in valid_lookup:
        fail(f'receptive_skills.reading.lookup_frequency invalid: {lookup}')

    # Hours should be non-negative
    for skill_name, skill in [('listening', listening), ('reading', reading)]:
        for field in ['hours_at_level', 'hours_total']:
            val = skill.get(field, 0)
            if val is not None and val < 0:
                fail(f'receptive_skills.{skill_name}.{field} is negative: {val}')

    # hours_total >= hours_at_level
    for skill_name, skill in [('listening', listening), ('reading', reading)]:
        total = skill.get('hours_total', 0) or 0
        at_level = skill.get('hours_at_level', 0) or 0
        if at_level > total:
            warn(f'receptive_skills.{skill_name}.hours_at_level ({at_level}) > hours_total ({total})')


def check_vocab_error_tracking(skill_map: dict) -> None:
    """Validate vocabulary cluster error_tracking fields."""
    vocab = skill_map.get('vocabulary', {})
    for cluster_id, cluster in vocab.items():
        et = cluster.get('error_tracking')
        if et is None:
            warn(f'vocabulary.{cluster_id} missing error_tracking section')
            continue

        rate = et.get('error_rate_production')
        if rate is not None:
            if not (0.0 <= rate <= 1.0):
                fail(f'vocabulary.{cluster_id}.error_tracking.error_rate_production out of range: {rate}')

        if not isinstance(et.get('common_errors', []), list):
            fail(f'vocabulary.{cluster_id}.error_tracking.common_errors should be a list')

    pass_(f'vocabulary error_tracking validated for {len(vocab)} clusters')


def check_resource_tracker(resource_tracker: dict) -> None:
    """Validate resource-tracker schema."""
    summary = resource_tracker.get('input_summary', {})
    if not summary:
        warn('resource-tracker missing input_summary section')
        return

    valid_listening = {'L1', 'L2', 'L3', 'L4', 'L5'}
    valid_reading = {'R1', 'R2', 'R3', 'R4', 'R5'}

    cl = summary.get('current_listening_level')
    if cl and cl not in valid_listening:
        fail(f'resource-tracker.input_summary.current_listening_level invalid: {cl}')

    cr = summary.get('current_reading_level')
    if cr and cr not in valid_reading:
        fail(f'resource-tracker.input_summary.current_reading_level invalid: {cr}')

    for field in ['total_listening_hours', 'total_reading_hours']:
        val = summary.get(field, 0)
        if val is not None and val < 0:
            fail(f'resource-tracker.input_summary.{field} is negative: {val}')

    resources = resource_tracker.get('resources', [])
    valid_types = {'listening', 'reading', 'mixed'}
    valid_trends = {None, 'improving', 'stable', 'declining'}
    valid_engagement = {None, 'enthusiastic', 'neutral', 'reluctant'}

    for r in resources:
        name = r.get('name', 'unknown')
        if r.get('type') not in valid_types:
            fail(f'resource-tracker resource "{name}" has invalid type: {r.get("type")}')
        if r.get('comprehension_trend') not in valid_trends:
            warn(f'resource-tracker resource "{name}" has invalid comprehension_trend')
        if r.get('learner_engagement') not in valid_engagement:
            warn(f'resource-tracker resource "{name}" has invalid learner_engagement')

    pass_(f'resource-tracker validated ({len(resources)} resources)')


# --- Main ---------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Validate tutoring system state files")
    ap.add_argument("--verbose", action="store_true", help="Show PASS results in addition to WARN/FAIL")
    args = ap.parse_args()

    profile          = load_yaml(STATE / "learner-profile.yaml")
    skill_map        = load_yaml(STATE / "skill-map.yaml")
    schedule         = load_yaml(STATE / "schedule.yaml")
    health           = load_yaml(STATE / "system-health.yaml")
    resource_tracker = load_yaml(STATE / "resource-tracker.yaml")

    sdir = STATE / "sessions"
    has_sessions = sdir.exists() and any(f.is_file() and f.suffix == ".yaml" for f in sdir.iterdir())

    if profile is not None:   check_learner_profile(profile, has_sessions)
    if skill_map is not None: check_skill_map(skill_map)
    if schedule is not None:  check_schedule(schedule)
    if health is not None:    check_system_health(health)

    if skill_map is not None:
        check_curriculum_cross_refs(skill_map)
        check_vocab_passive_active(skill_map)
    if schedule is not None and skill_map is not None:
        check_schedule_refs(schedule, skill_map)

    if skill_map is not None: check_acquired_consistency(skill_map)
    if skill_map is not None: check_performance_enums(skill_map)
    if skill_map is not None: check_integration_tested_with(skill_map)
    if skill_map is not None and profile is not None:
        check_acquired_zero_practice(skill_map, profile)
    if skill_map is not None:
        check_receptive_skills(skill_map)
        check_vocab_error_tracking(skill_map)
    check_session_filenames()
    if schedule is not None:
        check_schedule_enums(schedule)
        check_placement_validation_consistency(schedule)
    if schedule is not None and skill_map is not None:
        check_carryover_concepts(schedule, skill_map)
    if resource_tracker is not None:
        check_resource_tracker(resource_tracker)

    for lvl, msg in results:
        if lvl == "PASS" and not args.verbose: continue
        print(f"[{lvl}] {msg}")

    counts = {k: sum(1 for l, _ in results if l == k) for k in ("PASS", "WARN", "FAIL")}
    print(f"\n--- Summary: {counts['PASS']} passed, {counts['WARN']} warnings, {counts['FAIL']} failures ---")

    if counts["FAIL"]:
        sys.exit(1)
    if counts["WARN"]:
        print("Exiting with 0 (warnings are non-blocking)")
    sys.exit(0)


if __name__ == "__main__":
    main()
