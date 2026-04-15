#!/usr/bin/env python3
"""Validate state files against expected schemas and cross-references."""
import argparse, re, sys
from datetime import datetime
from pathlib import Path
try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr); sys.exit(1)

from shared import (ROOT, STATE_DIR as STATE, CURRICULUM_DIR as CURRICULUM,
                     PHASE_DIRS, TIER_DIRS, load_yaml, load_schema,
                     get_required_fields)


# ---------------------------------------------------------------------------
# Results collector — encapsulates validation output
# ---------------------------------------------------------------------------

class ValidationResults:
    """Collects PASS / WARN / FAIL results for a validation run."""

    def __init__(self) -> None:
        self._items: list[tuple[str, str]] = []

    # Convenience shortcuts -------------------------------------------------
    def pass_(self, msg: str) -> None:
        self._items.append(("PASS", msg))

    def warn(self, msg: str) -> None:
        self._items.append(("WARN", msg))

    def fail(self, msg: str) -> None:
        self._items.append(("FAIL", msg))

    # Access ----------------------------------------------------------------
    @property
    def items(self) -> list[tuple[str, str]]:
        return list(self._items)

    def counts(self) -> dict[str, int]:
        return {k: sum(1 for lvl, _ in self._items if lvl == k)
                for k in ("PASS", "WARN", "FAIL")}

    def clear(self) -> None:
        self._items.clear()


# Module-level instance — used by main() and importable for tests
results = ValidationResults()


# ---------------------------------------------------------------------------
# YAML loader (delegates to shared.load_yaml, reports to results)
# ---------------------------------------------------------------------------

def load_yaml_validated(path: Path, res: ValidationResults) -> dict | None:
    """Load a YAML file, reporting missing/invalid files to *res*."""
    if not path.exists():
        res.fail(f"Missing file: {path.relative_to(ROOT)}")
        return None
    data = load_yaml(path)
    if data is None:
        res.fail(f"YAML syntax error in {path.relative_to(ROOT)}")
        return None
    if not isinstance(data, dict):
        res.fail(f"Expected mapping at top level: {path.relative_to(ROOT)}")
        return None
    res.pass_(f"YAML syntax OK: {path.relative_to(ROOT)}")
    return data


# ---------------------------------------------------------------------------
# Path resolvers
# ---------------------------------------------------------------------------

def grammar_path(cid: str) -> Path:
    return CURRICULUM / "grammar" / PHASE_DIRS.get(cid[0], "") / f"{cid[2:]}.md"

def vocab_path(cid: str) -> Path:
    return CURRICULUM / "vocabulary" / TIER_DIRS.get(cid[4], "") / f"{cid[6:]}.md"


# --- 1. Required-field checks ------------------------------------------------

def check_required_fields(data: dict, schema_name: str, file_label: str,
                          res: ValidationResults) -> None:
    """Generic required-field checker driven by a schema file.

    Loads schemas/<schema_name>.schema.yaml and checks that every field
    marked required: true is present in *data*.
    """
    schema = load_schema(schema_name)
    required = get_required_fields(schema)
    missing = [f for f in required if f not in data]
    if missing:
        for f in missing:
            res.fail(f"{file_label}: missing required field '{f}'")
    else:
        res.pass_(f"{file_label}: all {len(required)} required fields present")


def check_learner_profile(data: dict, has_sessions: bool,
                          res: ValidationResults) -> None:
    check_required_fields(data, "learner-profile", "learner-profile", res)
    # Additional semantic check: warn if critical fields are empty after session 1
    for f in ("name", "native_language", "target_dialect"):
        if f in data and has_sessions and not data[f]:
            res.warn(f"learner-profile: '{f}' is empty after session 1")


def check_skill_map(data: dict, res: ValidationResults) -> None:
    grammar = data.get("grammar", {})
    if not grammar:
        res.fail("skill-map: 'grammar' section missing or empty")
    else:
        # Load grammar entry template to get required fields
        sm_schema = load_schema("skill-map")
        grammar_required = [
            name for name, spec in sm_schema.get("grammar_entry_template", {}).items()
            if isinstance(spec, dict) and spec.get("required")
        ]
        for cid, entry in grammar.items():
            if isinstance(entry, dict):
                for f in grammar_required:
                    if f not in entry:
                        res.fail(f"skill-map grammar '{cid}': missing '{f}'")
        res.pass_(f"skill-map: checked {len(grammar)} grammar entries for required fields")
    vocab = data.get("vocabulary", {})
    if not vocab: res.fail("skill-map: 'vocabulary' section missing or empty")
    else:         res.pass_(f"skill-map: {len(vocab)} vocabulary clusters present")


def check_schedule(data: dict, res: ValidationResults) -> None:
    check_required_fields(data, "schedule", "schedule", res)


def check_system_health(data: dict, res: ValidationResults) -> None:
    check_required_fields(data, "system-health", "system-health", res)


# --- 2. Cross-reference checks -----------------------------------------------

def check_curriculum_cross_refs(sm: dict, sched: dict | None,
                                res: ValidationResults) -> None:
    for section, resolver, label in [
        ("grammar", grammar_path, "grammar concepts"),
        ("vocabulary", vocab_path, "vocabulary clusters"),
    ]:
        items = sm.get(section, {})
        missing = [(c, resolver(c).relative_to(ROOT)) for c in items if not resolver(c).exists()]
        if missing:
            for cid, p in missing: res.fail(f"{label.title().rstrip('s')} '{cid}' has no curriculum file at {p}")
        else:
            res.pass_(f"All {len(items)} {label} have matching curriculum files")

    # S-18: Pronunciation cross-reference validation
    if sched is not None:
        pron = sched.get("active_pronunciation") or {}
        focus = pron.get("focus", "")
        if focus:
            pron_file = CURRICULUM / "pronunciation" / f"{focus}.md"
            if not pron_file.exists():
                res.fail(f"schedule active_pronunciation.focus '{focus}' has no curriculum file at {pron_file.relative_to(ROOT)}")
            else:
                res.pass_(f"schedule active_pronunciation.focus '{focus}' has matching curriculum file")


def check_schedule_refs(sched: dict, sm: dict,
                        res: ValidationResults) -> None:
    grammar_ids = sm.get("grammar", {})
    active = sched.get("active_grammar", {})

    # Primary
    primary = active.get("primary", "")
    if primary and primary not in grammar_ids:
        res.fail(f"schedule active_grammar.primary '{primary}' not found in skill-map")
    elif primary:
        res.pass_(f"schedule active_grammar.primary '{primary}' exists in skill-map")

    # E-29: Secondary
    secondary = active.get("secondary", "")
    if secondary and secondary not in grammar_ids:
        res.fail(f"schedule active_grammar.secondary '{secondary}' not found in skill-map")
    elif secondary:
        res.pass_(f"schedule active_grammar.secondary '{secondary}' exists in skill-map")

    # E-29: Maintenance
    maintenance = active.get("maintenance") or []
    for cid in maintenance:
        if cid not in grammar_ids:
            res.fail(f"schedule active_grammar.maintenance '{cid}' not found in skill-map")
    if maintenance:
        res.pass_(f"schedule active_grammar.maintenance: checked {len(maintenance)} refs")

    # E-29: Vocabulary
    active_vocab = sched.get("active_vocabulary", {})
    vocab_ids = sm.get("vocabulary", {})
    vocab_primary = active_vocab.get("primary", "")
    if vocab_primary and vocab_primary not in vocab_ids:
        res.fail(f"schedule active_vocabulary.primary '{vocab_primary}' not found in skill-map")
    elif vocab_primary:
        res.pass_(f"schedule active_vocabulary.primary '{vocab_primary}' exists in skill-map")

    vocab_review = active_vocab.get("review") or []
    for cid in vocab_review:
        if cid not in vocab_ids:
            res.fail(f"schedule active_vocabulary.review '{cid}' not found in skill-map")
    if vocab_review:
        res.pass_(f"schedule active_vocabulary.review: checked {len(vocab_review)} refs")

    # E-29: Pronunciation
    active_pron = sched.get("active_pronunciation", {})
    pron_ids = sm.get("pronunciation", {})
    pron_focus = active_pron.get("focus", "")
    if pron_focus and pron_focus not in pron_ids:
        res.fail(f"schedule active_pronunciation.focus '{pron_focus}' not found in skill-map")
    elif pron_focus:
        res.pass_(f"schedule active_pronunciation.focus '{pron_focus}' exists in skill-map")


def check_vocab_passive_active(sm: dict, res: ValidationResults) -> None:
    violations = []
    for cid, e in sm.get("vocabulary", {}).items():
        if not isinstance(e, dict): continue
        p, a = (e.get("passive_known", 0) or 0), (e.get("active_known", 0) or 0)
        if p < a: violations.append((cid, p, a))
    if violations:
        for cid, p, a in violations:
            res.fail(f"Vocabulary '{cid}': passive_known ({p}) < active_known ({a})")
    else:
        res.pass_("All vocabulary clusters: passive_known >= active_known")


# --- 3. Consistency checks ----------------------------------------------------

def check_acquired_consistency(sm: dict, res: ValidationResults) -> None:
    grammar = sm.get("grammar", {})
    acquired = []
    for cid, e in grammar.items():
        if not isinstance(e, dict) or e.get("status") != "acquired": continue
        acquired.append(cid)
        err = e.get("error_rate_production")
        # E-05: threshold matches CLAUDE.md spec (< 10%)
        if err is not None and err > 0.10:
            res.fail(f"Grammar '{cid}': acquired but error_rate_production={err} (> 0.10)")
        err_drills = e.get("error_rate_drills")
        # ENFORCE-07: threshold matches CLAUDE.md acquisition rule (< 0.10)
        if err_drills is not None and err_drills > 0.10:
            res.fail(f"Grammar '{cid}': acquired but error_rate_drills={err_drills} (> 0.10)")
        perf = e.get("performance_unscaffolded")
        if perf is not None and perf != "competent":
            res.fail(f"Grammar '{cid}': acquired but performance_unscaffolded='{perf}' (expected 'competent')")
    if acquired: res.pass_(f"Checked {len(acquired)} acquired concepts for consistency")
    else:        res.pass_("No acquired concepts to check (all unseen/practicing)")


def check_performance_enums(sm: dict, res: ValidationResults) -> None:
    valid_perf = {None, "struggling", "competent"}
    grammar = sm.get("grammar", {})
    for cid, e in grammar.items():
        if not isinstance(e, dict): continue
        for field in ("performance_scaffolded", "performance_unscaffolded"):
            val = e.get(field)
            if val not in valid_perf:
                res.fail(f"Grammar '{cid}': {field}='{val}' is not a valid value (expected: null, struggling, or competent)")
    res.pass_("Performance enum values are valid")


def check_session_filenames(res: ValidationResults) -> None:
    sdir = STATE / "sessions"
    if not sdir.exists():
        res.warn("state/sessions/ directory does not exist"); return
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}\.yaml$")
    bad = [f.name for f in sdir.iterdir() if f.is_file() and not f.name.startswith(".") and not date_re.match(f.name)]
    if bad:
        for name in bad: res.warn(f"Session file '{name}' does not match YYYY-MM-DD.yaml pattern")
    else:
        n = sum(1 for f in sdir.iterdir() if f.is_file() and not f.name.startswith("."))
        res.pass_(f"All {n} session files have valid date filenames" if n else "No session files yet")


def check_carryover_concepts(sched: dict, sm: dict,
                             res: ValidationResults) -> None:
    carryover = sched.get("carryover_concepts") or []
    if not carryover:
        res.pass_("No carryover concepts to check")
        return
    grammar = sm.get("grammar", {})
    for cid in carryover:
        if cid not in grammar:
            res.fail(f"Carryover concept '{cid}' not found in skill-map grammar section")
        else:
            entry = grammar[cid]
            if isinstance(entry, dict):
                status = entry.get("status")
                if status in ("acquired", "automatic"):
                    res.warn(f"Carryover concept '{cid}' has status '{status}' — should be removed from carryover list")
    res.pass_(f"Checked {len(carryover)} carryover concepts")


def check_schedule_enums(sched: dict, res: ValidationResults) -> None:
    valid_phases = {"A-foundation", "B-conversational", "C-intermediate", "D-advanced"}
    phase = sched.get("current_phase", "")
    if phase and phase not in valid_phases:
        res.fail(f"schedule.current_phase='{phase}' is not a valid phase")
    valid_balance = {"accuracy-leaning", "balanced", "fluency-leaning"}
    balance = sched.get("fluency_accuracy_balance", "")
    if balance and balance not in valid_balance:
        res.fail(f"schedule.fluency_accuracy_balance='{balance}' is not valid")
    week = sched.get("current_week", 0)
    if isinstance(week, int) and week < 0:
        res.fail(f"schedule.current_week={week} is negative")
    res.pass_("Schedule enum values are valid")


def check_integration_tested_with(sm: dict, res: ValidationResults) -> None:
    grammar = sm.get("grammar", {})
    grammar_ids = set(grammar.keys())
    for cid, entry in grammar.items():
        if not isinstance(entry, dict): continue
        # Legacy boolean field check
        if "integration_tested" in entry:
            res.warn(f"Grammar '{cid}': legacy field 'integration_tested' found — should be 'integration_tested_with' (list)")
        itw = entry.get("integration_tested_with")
        if itw is None:
            # Field simply absent — not a blocker, schema may be partial
            pass
        elif not isinstance(itw, list):
            res.fail(f"Grammar '{cid}': 'integration_tested_with' should be a list, got {type(itw).__name__}")
        else:
            for ref in itw:
                if ref not in grammar_ids:
                    res.fail(f"Grammar '{cid}': 'integration_tested_with' references unknown concept '{ref}'")
    res.pass_("Checked integration_tested_with format for all grammar concepts")


def check_acquired_zero_practice(sm: dict, profile: dict,
                                 res: ValidationResults) -> None:
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
            res.pass_(f"Grammar '{cid}': acquired with practice_count=0 (placement-exempt: below {placement_phase}-level placement)")
        else:
            res.warn(f"Grammar '{cid}': acquired with practice_count=0 — cannot acquire without practice unless placement-validated")


def check_placement_validation_consistency(sched: dict,
                                           res: ValidationResults) -> None:
    pv = sched.get("placement_validation") or {}
    pv_active = pv.get("active", False)
    onboarding_complete = sched.get("onboarding_complete", False)
    if pv_active and not onboarding_complete:
        res.fail("Placement validation active but onboarding not complete — contradictory state")
    elif pv_active:
        res.pass_("Placement validation active and onboarding_complete is true — consistent")
    else:
        res.pass_("Placement validation not active — no consistency check needed")


def check_receptive_skills(skill_map: dict, res: ValidationResults) -> None:
    """Validate receptive_skills schema and level values."""
    rs = skill_map.get('receptive_skills', {})
    if not rs:
        res.warn('receptive_skills section missing from skill-map')
        return

    valid_listening = {'L1', 'L2', 'L3', 'L4', 'L5'}
    valid_reading = {'R1', 'R2', 'R3', 'R4', 'R5'}
    valid_quality = {None, 'gist', 'main_ideas', 'details', 'inference'}
    valid_lookup = {None, 'frequent', 'occasional', 'rare', 'none'}

    listening = rs.get('listening', {})
    reading = rs.get('reading', {})

    level = listening.get('current_level')
    if level and level not in valid_listening:
        res.fail(f'receptive_skills.listening.current_level invalid: {level} (expected L1-L5)')
    else:
        res.pass_('receptive_skills.listening.current_level valid')

    quality = listening.get('comprehension_quality')
    if quality not in valid_quality:
        res.fail(f'receptive_skills.listening.comprehension_quality invalid: {quality}')

    level = reading.get('current_level')
    if level and level not in valid_reading:
        res.fail(f'receptive_skills.reading.current_level invalid: {level} (expected R1-R5)')
    else:
        res.pass_('receptive_skills.reading.current_level valid')

    lookup = reading.get('lookup_frequency')
    if lookup not in valid_lookup:
        res.fail(f'receptive_skills.reading.lookup_frequency invalid: {lookup}')

    # Hours should be non-negative
    for skill_name, skill in [('listening', listening), ('reading', reading)]:
        for field in ['hours_at_level', 'hours_total']:
            val = skill.get(field, 0)
            if val is not None and val < 0:
                res.fail(f'receptive_skills.{skill_name}.{field} is negative: {val}')

    # hours_total >= hours_at_level
    for skill_name, skill in [('listening', listening), ('reading', reading)]:
        total = skill.get('hours_total', 0) or 0
        at_level = skill.get('hours_at_level', 0) or 0
        if at_level > total:
            res.warn(f'receptive_skills.{skill_name}.hours_at_level ({at_level}) > hours_total ({total})')


def check_vocab_error_tracking(skill_map: dict, res: ValidationResults) -> None:
    """Validate vocabulary cluster error_tracking fields."""
    vocab = skill_map.get('vocabulary', {})
    for cluster_id, cluster in vocab.items():
        et = cluster.get('error_tracking')
        if et is None:
            res.warn(f'vocabulary.{cluster_id} missing error_tracking section')
            continue

        rate = et.get('error_rate_production')
        if rate is not None:
            if not (0.0 <= rate <= 1.0):
                res.fail(f'vocabulary.{cluster_id}.error_tracking.error_rate_production out of range: {rate}')

        if not isinstance(et.get('common_errors', []), list):
            res.fail(f'vocabulary.{cluster_id}.error_tracking.common_errors should be a list')

    res.pass_(f'vocabulary error_tracking validated for {len(vocab)} clusters')


def check_resource_tracker(resource_tracker: dict,
                           res: ValidationResults) -> None:
    """Validate resource-tracker schema."""
    # E-04: check required fields
    check_required_fields(resource_tracker, "resource-tracker", "resource-tracker", res)

    summary = resource_tracker.get('input_summary', {})
    if not summary:
        res.warn('resource-tracker missing input_summary section')
        return

    valid_listening = {'L1', 'L2', 'L3', 'L4', 'L5'}
    valid_reading = {'R1', 'R2', 'R3', 'R4', 'R5'}

    cl = summary.get('current_listening_level')
    if cl and cl not in valid_listening:
        res.fail(f'resource-tracker.input_summary.current_listening_level invalid: {cl}')

    cr = summary.get('current_reading_level')
    if cr and cr not in valid_reading:
        res.fail(f'resource-tracker.input_summary.current_reading_level invalid: {cr}')

    for field in ['total_listening_hours', 'total_reading_hours']:
        val = summary.get(field, 0)
        if val is not None and val < 0:
            res.fail(f'resource-tracker.input_summary.{field} is negative: {val}')

    resources = resource_tracker.get('resources', [])
    valid_types = {'listening', 'reading', 'mixed'}
    valid_trends = {None, 'improving', 'stable', 'declining'}
    valid_engagement = {None, 'enthusiastic', 'neutral', 'reluctant'}

    for r in resources:
        name = r.get('name', 'unknown')
        if r.get('type') not in valid_types:
            res.fail(f'resource-tracker resource "{name}" has invalid type: {r.get("type")}')
        if r.get('comprehension_trend') not in valid_trends:
            res.warn(f'resource-tracker resource "{name}" has invalid comprehension_trend')
        if r.get('learner_engagement') not in valid_engagement:
            res.warn(f'resource-tracker resource "{name}" has invalid learner_engagement')

    res.pass_(f'resource-tracker validated ({len(resources)} resources)')


# --- 4. Session log validation (E-03) ----------------------------------------

def check_session_logs(res: ValidationResults) -> None:
    """Validate each session log in state/sessions/ against the session-log schema."""
    sdir = STATE / "sessions"
    if not sdir.exists():
        res.warn("state/sessions/ directory does not exist")
        return

    schema = load_schema("session-log")
    required = get_required_fields(schema)
    fields_spec = schema.get("fields", {})

    # Collect enum specs for validation
    enum_fields: dict[str, set] = {}
    for fname, spec in fields_spec.items():
        if isinstance(spec, dict) and "enum" in spec:
            enum_fields[fname] = set(spec["enum"])

    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}\.yaml$")
    checked = 0

    for f in sorted(sdir.iterdir()):
        if not f.is_file() or f.name.startswith("."):
            continue
        if f.parent.name == "archive":
            continue
        if not date_re.match(f.name):
            continue  # filename validation handled by check_session_filenames

        data = load_yaml(f)
        if data is None:
            res.fail(f"Session log {f.name}: YAML parse error or empty")
            continue
        if not isinstance(data, dict):
            res.fail(f"Session log {f.name}: expected mapping at top level")
            continue

        # Check required fields
        missing = [field for field in required if field not in data]
        if missing:
            for field in missing:
                res.fail(f"Session log {f.name}: missing required field '{field}'")

        # Check enum values
        for fname, allowed in enum_fields.items():
            val = data.get(fname)
            if val is not None and val not in allowed:
                res.fail(f"Session log {f.name}: {fname}='{val}' is not a valid enum value (expected one of {sorted(str(v) for v in allowed if v is not None)})")

        checked += 1

    if checked:
        res.pass_(f"Validated {checked} session log(s) against schema")
    else:
        res.pass_("No session logs to validate")


# --- 5. Cross-validation: resource-tracker vs skill-map (E-30) ---------------

def check_resource_skill_map_levels(resource_tracker: dict, skill_map: dict,
                                    res: ValidationResults) -> None:
    """Cross-validate receptive skill levels between resource-tracker and skill-map."""
    rt_summary = resource_tracker.get("input_summary", {})
    sm_receptive = skill_map.get("receptive_skills", {})

    if not rt_summary or not sm_receptive:
        res.pass_("resource-tracker/skill-map cross-validation: insufficient data to compare")
        return

    # Listening level
    rt_listening = rt_summary.get("current_listening_level")
    sm_listening = (sm_receptive.get("listening") or {}).get("current_level")
    if rt_listening and sm_listening and rt_listening != sm_listening:
        res.warn(
            f"Receptive skill level mismatch — resource-tracker listening level '{rt_listening}' "
            f"vs skill-map listening level '{sm_listening}'"
        )

    # Reading level
    rt_reading = rt_summary.get("current_reading_level")
    sm_reading = (sm_receptive.get("reading") or {}).get("current_level")
    if rt_reading and sm_reading and rt_reading != sm_reading:
        res.warn(
            f"Receptive skill level mismatch — resource-tracker reading level '{rt_reading}' "
            f"vs skill-map reading level '{sm_reading}'"
        )

    if not any(m for lvl, m in res.items if lvl == "WARN" and "Receptive skill level mismatch" in m):
        res.pass_("resource-tracker/skill-map receptive levels are consistent")


# --- 6. Last-session-date drift check (ENFORCE-06) ----------------------------

def check_last_session_date(sched: dict, res: ValidationResults,
                             dry_run: bool = False) -> None:
    """Detect and auto-fix last_session_date vs most-recent session log disagreement."""
    sdir = STATE / "sessions"
    if not sdir.exists():
        res.pass_("last_session_date: no sessions directory — skip check")
        return

    date_re = re.compile(r"^(\d{4}-\d{2}-\d{2})\.yaml$")
    logs = sorted(
        (m.group(1) for f in sdir.iterdir()
         if f.is_file() and not f.name.startswith(".")
         and (m := date_re.match(f.name))),
        reverse=True
    )
    if not logs:
        res.pass_("last_session_date: no session logs found — skip check")
        return

    most_recent = logs[0]
    recorded = sched.get("last_session_date")

    if recorded is not None and not isinstance(recorded, str):
        recorded = str(recorded)

    if recorded == most_recent:
        res.pass_(f"last_session_date matches most recent session log: {most_recent}")
        return

    if dry_run:
        res.warn(
            f"last_session_date='{recorded}' but most recent session log is {most_recent} "
            f"[dry-run: would auto-fix]"
        )
        return

    sched_path = STATE / "schedule.yaml"
    sched["last_session_date"] = most_recent
    with sched_path.open("w") as f:
        import yaml as _yaml
        _yaml.dump(sched, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    health_path = STATE / "system-health.yaml"
    if health_path.exists():
        health = load_yaml(health_path) or {}
        fixes = health.setdefault("auto_fixes", [])
        fixes.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "field": "schedule.last_session_date",
            "old_value": recorded,
            "new_value": most_recent,
            "reason": "Disagreed with most recent session log filename",
            "detected_by": "validate-state.py:check_last_session_date",
        })
        with health_path.open("w") as f:
            import yaml as _yaml
            _yaml.dump(health, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    res.pass_(
        f"Auto-fixed last_session_date: '{recorded}' → '{most_recent}' "
        f"(logged in system-health.yaml)"
    )


# --- Main ---------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Validate tutoring system state files")
    ap.add_argument("--verbose", action="store_true", help="Show PASS results in addition to WARN/FAIL")
    ap.add_argument("--dry-run", action="store_true", help="Preview auto-fixes without writing")
    args = ap.parse_args()

    res = results  # use module-level instance

    profile          = load_yaml_validated(STATE / "learner-profile.yaml", res)
    skill_map        = load_yaml_validated(STATE / "skill-map.yaml", res)
    schedule         = load_yaml_validated(STATE / "schedule.yaml", res)
    health           = load_yaml_validated(STATE / "system-health.yaml", res)
    resource_tracker = load_yaml_validated(STATE / "resource-tracker.yaml", res)

    sdir = STATE / "sessions"
    has_sessions = sdir.exists() and any(f.is_file() and f.suffix == ".yaml" for f in sdir.iterdir())

    if profile is not None:   check_learner_profile(profile, has_sessions, res)
    if skill_map is not None: check_skill_map(skill_map, res)
    if schedule is not None:  check_schedule(schedule, res)
    if health is not None:    check_system_health(health, res)

    if skill_map is not None:
        check_curriculum_cross_refs(skill_map, schedule, res)
        check_vocab_passive_active(skill_map, res)
    if schedule is not None and skill_map is not None:
        check_schedule_refs(schedule, skill_map, res)

    if skill_map is not None: check_acquired_consistency(skill_map, res)
    if skill_map is not None: check_performance_enums(skill_map, res)
    if skill_map is not None: check_integration_tested_with(skill_map, res)
    if skill_map is not None and profile is not None:
        check_acquired_zero_practice(skill_map, profile, res)
    if skill_map is not None:
        check_receptive_skills(skill_map, res)
        check_vocab_error_tracking(skill_map, res)
    check_session_filenames(res)
    check_session_logs(res)
    if schedule is not None:
        check_last_session_date(schedule, res, dry_run=args.dry_run)
        check_schedule_enums(schedule, res)
        check_placement_validation_consistency(schedule, res)
    if schedule is not None and skill_map is not None:
        check_carryover_concepts(schedule, skill_map, res)
    if resource_tracker is not None:
        check_resource_tracker(resource_tracker, res)
    if resource_tracker is not None and skill_map is not None:
        check_resource_skill_map_levels(resource_tracker, skill_map, res)

    for lvl, msg in res.items:
        if lvl == "PASS" and not args.verbose: continue
        print(f"[{lvl}] {msg}")

    counts = res.counts()
    print(f"\n--- Summary: {counts['PASS']} passed, {counts['WARN']} warnings, {counts['FAIL']} failures ---")

    if counts["FAIL"]:
        sys.exit(1)
    if counts["WARN"]:
        print("Exiting with 0 (warnings are non-blocking)")
    sys.exit(0)


if __name__ == "__main__":
    main()
