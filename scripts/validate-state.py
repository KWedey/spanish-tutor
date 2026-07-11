#!/usr/bin/env python3
"""Validate state files against expected schemas and cross-references."""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr); sys.exit(1)

from shared import (ROOT, STATE_DIR as STATE, CURRICULUM_DIR as CURRICULUM,
                     PHASE_DIRS, TIER_DIRS, load_yaml, load_schema,
                     get_required_fields, atomic_write, leading_header)
import phase_prereqs


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

def display_path(path: Path):
    """Render *path* relative to ROOT for display, tolerating paths outside it.

    The validator can be pointed at a STATE dir outside the repo (the
    corruption-stress harness redirects STATE to a temp copy via
    TUTOR_STATE_DIR). ``Path.relative_to(ROOT)`` raises ValueError for such
    paths, so fall back to the absolute path rather than crashing on a purely
    cosmetic display string.
    """
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def load_yaml_validated(path: Path, res: ValidationResults) -> dict | None:
    """Load a YAML file, reporting missing/invalid files to *res*."""
    if not path.exists():
        res.fail(f"Missing file: {display_path(path)}")
        return None
    data = load_yaml(path)
    if data is None:
        res.fail(f"YAML syntax error in {display_path(path)}")
        return None
    if not isinstance(data, dict):
        res.fail(f"Expected mapping at top level: {display_path(path)}")
        return None
    res.pass_(f"YAML syntax OK: {display_path(path)}")
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


def _collect_media_bank_dialects(media_bank: dict) -> set:
    """Collect every `dialect:` tag value anywhere in the media-bank tree."""
    found: set = set()

    def walk(node):
        if isinstance(node, dict):
            d = node.get("dialect")
            if isinstance(d, str) and d:
                found.add(d)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(media_bank or {})
    return found


def check_media_bank_dialect_coverage(media_bank: dict, dialects: dict,
                                      res: ValidationResults) -> None:
    """CC-3 (C9): every media-bank `dialect:` tag must be recognized by the
    *resource* sets in curriculum/dialects.yaml. An unrecognized tag means the
    dialect-advisory matrix in check-session-log.py silently cannot classify
    that resource — the matrix would never fire for it. The taxonomy is the
    single source of truth shared by both scripts."""
    if not dialects:
        # Fail loud, mirroring check-session-log.py's import-time RuntimeError:
        # a missing/empty source-of-truth file must not let this guard evaporate.
        res.fail(
            "curriculum/dialects.yaml is missing or empty — required by the "
            "media-bank dialect coverage check (CC-3). check-session-log.py "
            "fails loudly on the same condition; validate-state must too."
        )
        return
    recognized = (
        set(dialects.get("peninsular_resource_dialects") or [])
        | set(dialects.get("latam_resource_dialects") or [])
        | set(dialects.get("mixed_neutral_resource_dialects") or [])
    )
    tags = _collect_media_bank_dialects(media_bank)
    unknown = sorted(t for t in tags if t not in recognized)
    if unknown:
        res.fail(
            f"media-bank dialect tag(s) {unknown} not recognized by "
            f"curriculum/dialects.yaml resource sets — the dialect-advisory "
            f"matrix (check-session-log.py) cannot classify them (CC-3). Add "
            f"each to the appropriate *_resource_dialects set."
        )
    else:
        res.pass_(
            f"media-bank: all {len(tags)} dialect tag(s) recognized by "
            f"curriculum/dialects.yaml (CC-3)"
        )


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
    """LOAD-01 / D-02: CORE acquisition consistency for grammar AND vocabulary.

    Iterates the two CORE categories (CLAUDE.md L196). An 'acquired' grammar
    concept must have error_rate_drills < 0.10 AND error_rate_production < 0.10
    AND performance_unscaffolded == 'competent'. An 'acquired' vocabulary cluster
    must have error_tracking.error_rate_production < 0.10 (vocab carries no
    error_rate_drills / performance_unscaffolded by schema design).

    Secondary categories (pronunciation, writing, cultural_awareness) are
    intentionally NOT iterated here — their schema templates have no error_rate
    fields, so a numeric check would FAIL on null data. Secondary acquisition is
    tutor judgment (CLAUDE.md SECONDARY bullet) and, for cultural, the
    `assessed_through` field. Broadening this loop to the SECONDARY sections would
    break tests/test_validate_state.py::TestAcquiredConsistencyCoreOnly and must
    first update those schemas to carry the numeric fields.

    check_vocab_error_tracking separately validates the 0.0-1.0 range of every
    vocabulary error_rate_production regardless of status.
    """
    grammar = sm.get("grammar", {})
    acquired = []
    for cid, e in grammar.items():
        if not isinstance(e, dict) or e.get("status") != "acquired": continue
        acquired.append(cid)
        err = e.get("error_rate_production")
        # E-05/P2-j: CLAUDE.md gate is error_rate < 0.10, so a rate >= 0.10 is
        # invalid for 'acquired' (the prior `> 0.10` wrongly permitted exactly 0.10).
        if err is not None and err >= 0.10:
            res.fail(f"Grammar '{cid}': acquired but error_rate_production={err} (>= 0.10)")
        err_drills = e.get("error_rate_drills")
        # ENFORCE-07/P2-j: threshold matches CLAUDE.md acquisition rule (< 0.10).
        if err_drills is not None and err_drills >= 0.10:
            res.fail(f"Grammar '{cid}': acquired but error_rate_drills={err_drills} (>= 0.10)")
        perf = e.get("performance_unscaffolded")
        if perf is not None and perf != "competent":
            res.fail(f"Grammar '{cid}': acquired but performance_unscaffolded='{perf}' (expected 'competent')")
    # P1-2: vocabulary is a CORE category (CLAUDE.md L196) — enforce the same
    # acquired+high-error gate via the nested error_tracking.error_rate_production.
    for cid, e in sm.get("vocabulary", {}).items():
        if not isinstance(e, dict) or e.get("status") != "acquired": continue
        acquired.append(cid)
        et = e.get("error_tracking")
        verr = et.get("error_rate_production") if isinstance(et, dict) else None
        if verr is not None and verr >= 0.10:
            res.fail(f"Vocabulary '{cid}': acquired but error_tracking.error_rate_production={verr} (>= 0.10)")
    if acquired: res.pass_(f"Checked {len(acquired)} acquired concepts for consistency")
    else:        res.pass_("No acquired concepts to check (all unseen/practicing)")


def _schema_enum(schema: dict, *path: str) -> set:
    """Return the `enum` of a nested schema field as a set (YAML null -> None).

    Drives validator enums from schemas/*.yaml so they cannot silently drift
    from the schema (the single source of truth). Raises KeyError loudly if the
    schema path or `enum` key is missing rather than falling back to a stale
    hardcoded copy.
    """
    node = schema
    for key in path:
        node = node[key]
    return set(node["enum"])


def check_performance_enums(sm: dict, res: ValidationResults) -> None:
    valid_perf = _schema_enum(load_schema("skill-map"),
                              "grammar_entry_template", "performance_scaffolded")
    grammar = sm.get("grammar", {})
    for cid, e in grammar.items():
        if not isinstance(e, dict): continue
        for field in ("performance_scaffolded", "performance_unscaffolded"):
            val = e.get(field)
            if val not in valid_perf:
                res.fail(f"Grammar '{cid}': {field}='{val}' is not a valid value (expected: null, struggling, or competent)")
    res.pass_("Performance enum values are valid")


# --- 3b. ENGINE Phase 4 checks -----------------------------------------------

def check_learner_interest_range(sm: dict, res: ValidationResults) -> None:
    """D-02/D-10: learner_interest.score must be 0-3. Missing = OK (default 0).
    Out of range = FAIL."""
    violations = []
    for section in ("grammar", "vocabulary", "cultural_awareness"):
        for cid, e in (sm.get(section) or {}).items():
            if not isinstance(e, dict):
                continue
            li = e.get("learner_interest")
            if li is None:
                continue  # missing = backward-compat default 0
            score = li.get("score")
            if score is None:
                continue
            if not isinstance(score, int) or score < 0 or score > 3:
                violations.append((section, cid, score))
    if violations:
        for section, cid, score in violations:
            res.fail(f"{section} '{cid}': learner_interest.score={score} out of range 0-3 (D-02 cap)")
    else:
        res.pass_("learner_interest scores in range 0-3")


def check_learner_interest_staleness(sm: dict, res: ValidationResults) -> None:
    """D-03/D-10: WARN (not FAIL) when learner_interest.last_inferred > 28 days."""
    from datetime import date
    today = date.today()
    stale = []
    for section in ("grammar", "vocabulary", "cultural_awareness"):
        for cid, e in (sm.get(section) or {}).items():
            if not isinstance(e, dict):
                continue
            li = e.get("learner_interest")
            if not isinstance(li, dict):
                continue
            last = li.get("last_inferred")
            if not last:
                continue
            try:
                inferred_date = date.fromisoformat(str(last))
                days_ago = (today - inferred_date).days
                if days_ago > 28:
                    stale.append((section, cid, days_ago))
            except (ValueError, TypeError):
                continue  # unparseable date — skip, don't FAIL
    if stale:
        for section, cid, days in stale:
            res.warn(f"{section} '{cid}': learner_interest.last_inferred is {days} days old (stale > 28 days)")
    else:
        res.pass_("learner_interest staleness: all entries fresh or absent")


def check_recast_uptake_stats_consistency(sm: dict, res: ValidationResults) -> None:
    """D-07: landed + missed + partial must be <= recasts_given."""
    violations = []
    for cid, e in (sm.get("grammar") or {}).items():
        if not isinstance(e, dict):
            continue
        stats = e.get("recast_uptake_stats")
        if not isinstance(stats, dict):
            continue
        given = stats.get("recasts_given", 0) or 0
        landed = stats.get("landed", 0) or 0
        missed = stats.get("missed", 0) or 0
        partial = stats.get("partial", 0) or 0
        if landed + missed + partial > given:
            violations.append((cid, given, landed, missed, partial))
    if violations:
        for cid, g, l, m, p in violations:
            res.fail(f"Grammar '{cid}': recast_uptake_stats invariant violated "
                     f"(landed={l} + missed={m} + partial={p} > recasts_given={g})")
    else:
        res.pass_("recast_uptake_stats invariants hold")


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
    for item in carryover:
        # Schema shape is a map ({concept_id, sessions_in_carryover, escalation_stage, ...}
        # per schemas/schedule.schema.yaml); tolerate legacy bare-string entries.
        cid = item.get("concept_id") if isinstance(item, dict) else item
        if not cid:
            res.fail("Carryover concept entry missing 'concept_id'")
            continue
        if cid not in grammar:
            res.fail(f"Carryover concept '{cid}' not found in skill-map grammar section")
        else:
            entry = grammar[cid]
            if isinstance(entry, dict):
                status = entry.get("status")
                if status in ("acquired", "automatic"):
                    res.warn(f"Carryover concept '{cid}' has status '{status}' — should be removed from carryover list")
    res.pass_(f"Checked {len(carryover)} carryover concepts")


def check_onboarding_counter_range(sched: dict, res: ValidationResults) -> None:
    """Guard the onboarding progression counter (CLAUDE.md C1 fix).

    While onboarding is in progress (onboarding_complete is false),
    current_onboarding_session must be an int in [1, 10]. A value stuck at 1
    across sessions is the symptom of the never-incremented bug; a value > 10
    or < 1 means the counter advanced past the onboarding arc without
    onboarding_complete being set, or was corrupted. Once onboarding_complete
    is true the counter is unused, so no constraint applies.
    """
    if sched.get("onboarding_complete", False):
        res.pass_("onboarding_complete is true — onboarding counter unconstrained")
        return
    counter = sched.get("current_onboarding_session")
    if counter is None:
        # null is valid only before the first session populates it
        res.pass_("current_onboarding_session is null (pre-first-session)")
        return
    if not isinstance(counter, int) or isinstance(counter, bool):
        res.fail(
            f"schedule.current_onboarding_session must be an integer while "
            f"onboarding is in progress, got {counter!r}"
        )
        return
    if counter < 1 or counter > 10:
        res.fail(
            f"schedule.current_onboarding_session={counter} is out of range "
            f"[1, 10] while onboarding_complete is false (onboarding sessions "
            f"are 1-10; session 10 sets onboarding_complete: true)"
        )
        return
    res.pass_(f"current_onboarding_session={counter} is within onboarding range [1, 10]")


def check_schedule_enums(sched: dict, res: ValidationResults) -> None:
    sched_fields = load_schema("schedule")["fields"]
    valid_phases = _schema_enum(sched_fields, "current_phase")
    phase = sched.get("current_phase", "")
    if phase and phase not in valid_phases:
        res.fail(f"schedule.current_phase='{phase}' is not a valid phase")
    valid_balance = _schema_enum(sched_fields, "fluency_accuracy_balance")
    balance = sched.get("fluency_accuracy_balance", "")
    if balance and balance not in valid_balance:
        res.fail(f"schedule.fluency_accuracy_balance='{balance}' is not valid")
    week = sched.get("current_week", 0)
    if isinstance(week, int) and week < 0:
        res.fail(f"schedule.current_week={week} is negative")
    res.pass_("Schedule enum values are valid")


def check_study_time_budget_consistency(sched: dict, has_sessions: bool,
                                         res: ValidationResults) -> None:
    """LOAD-07 / D-04 / D-06: study_time_budget internal consistency.

    Invariants:
    - null pre-first-session → PASS (valid at init, D-06)
    - null AND has_sessions → FAIL (must be captured at first-session per D-06)
    - must be a dict if not null
    - after first-session: daily_minimum, daily_target, daily_maximum, weekly_goal
      must all be populated (each missing sub-field → one FAIL)
    - daily_minimum <= daily_target <= daily_maximum → FAIL if violated
    - today_stretch >= 0 → FAIL if negative
    """
    stb = sched.get("study_time_budget")
    if stb is None:
        if has_sessions:
            res.fail("schedule.study_time_budget is null but sessions exist "
                     "(required after first-session per D-06)")
        else:
            res.pass_("study_time_budget: null pre-first-session (expected)")
        return
    if not isinstance(stb, dict):
        res.fail(f"schedule.study_time_budget must be a map, got {type(stb).__name__}")
        return
    d_min = stb.get("daily_minimum")
    d_tgt = stb.get("daily_target")
    d_max = stb.get("daily_maximum")
    stretch = stb.get("today_stretch", 0)
    # Required sub-fields once the learner has run any session (D-06).
    missing = [k for k in ("daily_minimum", "daily_target", "daily_maximum", "weekly_goal")
               if stb.get(k) is None]
    if missing and has_sessions:
        for k in missing:
            res.fail(f"study_time_budget.{k} is null — must be populated at first-session (D-06)")
        return
    # Invariant: min <= target <= max
    if None not in (d_min, d_tgt, d_max):
        if not (d_min <= d_tgt <= d_max):
            res.fail(f"study_time_budget invariant violated: "
                     f"daily_minimum({d_min}) <= daily_target({d_tgt}) <= daily_maximum({d_max})")
            return
    # today_stretch must be non-negative
    if stretch is not None and stretch < 0:
        res.fail(f"study_time_budget.today_stretch={stretch} is negative")
        return
    res.pass_("study_time_budget internal consistency OK")


def check_daily_target_tier_drift(sched: dict, session_logs: list,
                                    res: ValidationResults) -> None:
    """LOAD-04 / D-11: detect when 2+ consecutive 'too-much' homework_load_rating
    ratings accumulate in schedule.consecutive_too_much_count but the tutor has
    not yet reduced schedule.study_time_budget.daily_target (i.e. counter pinned
    at >=2 is the "pending reduction" state).

    Semantic (locked by tests/test_validate_state.py::TestDailyTargetTierDrift):

    - If the most recent two session logs both have homework_load_rating='too-much'
      AND schedule['consecutive_too_much_count'] >= 2 → FAIL (the counter reached
      the D-11 threshold; tutor must reduce daily_target by 20% rounded to nearest
      5 min AND reset consecutive_too_much_count to 0 AND append an entry to
      state/system-health.yaml > load_adjustments).
    - If counter == 0 after 2 too-much in logs → PASS (reduction already applied,
      counter reset per the D-11 ladder — the audit trail is in
      state/system-health.yaml > load_adjustments).
    - 0 or 1 'too-much' in recent logs → PASS regardless of counter (below
      threshold; not enough to trigger reduction).

    Does nothing (PASS) if session_logs is empty or schedule has no
    study_time_budget.
    """
    stb = (sched or {}).get("study_time_budget")
    if not isinstance(stb, dict):
        res.pass_("daily_target tier drift: no study_time_budget configured")
        return
    # Scan the most recent 2 logs for 'too-much'.
    recent = [l for l in (session_logs or []) if isinstance(l, dict)][-2:]
    too_much_count = sum(
        1 for l in recent if l.get("homework_load_rating") == "too-much"
    )
    counter = int(sched.get("consecutive_too_much_count") or 0)
    if too_much_count >= 2 and counter >= 2:
        res.fail(
            f"daily_target tier drift: observed {too_much_count} consecutive "
            f"'too-much' ratings in last 2 session logs AND "
            f"consecutive_too_much_count={counter} (>=2) — D-11 requires reducing "
            f"daily_target by 20% (round to nearest 5 min) once the counter "
            f"reaches 2 consecutive 'too-much' ratings and then resetting "
            f"consecutive_too_much_count to 0 with an entry appended to "
            f"state/system-health.yaml > load_adjustments. The pending reduction "
            f"has not been applied."
        )
        return
    res.pass_(
        f"daily_target tier drift check: {too_much_count} recent 'too-much', "
        f"consecutive_too_much_count={counter} (consistent with D-11 ladder)"
    )


def check_just_right_restore_drift(sched: dict, session_logs: list,
                                   res: ValidationResults) -> None:
    """A4 / D-11 (restore side): companion to check_daily_target_tier_drift.

    The D-11 ladder restores daily_target by +10% after 3 consecutive
    'just-right' homework_load_rating ratings (following an earlier reduction).
    check_daily_target_tier_drift guards the *reduction* (too-much) side via
    consecutive_too_much_count; nothing guarded the *restore* side, so if the
    tutor let consecutive_just_right_count reach 3 without applying the restore
    (and resetting the counter), it went unnoticed. This mirrors the too-much
    tripwire for parity.

    Semantic (locked by tests/test_validate_state.py::TestJustRightRestoreDrift):

    - If the most recent three session logs all have
      homework_load_rating='just-right' AND
      schedule['consecutive_just_right_count'] >= 3 → FAIL (the counter reached
      the D-11 restore threshold; the tutor must restore daily_target by +10%
      AND reset consecutive_just_right_count to 0).
    - If counter == 0 after 3 just-right in logs → PASS (restore already applied,
      counter reset per the D-11 ladder).
    - Fewer than 3 'just-right' in recent logs → PASS regardless of counter
      (below threshold; not enough to trigger a restore).

    Does nothing (PASS) if session_logs is empty or schedule has no
    study_time_budget.
    """
    stb = (sched or {}).get("study_time_budget")
    if not isinstance(stb, dict):
        res.pass_("just-right restore drift: no study_time_budget configured")
        return
    # Scan the most recent 3 logs for 'just-right'.
    recent = [l for l in (session_logs or []) if isinstance(l, dict)][-3:]
    just_right_count = sum(
        1 for l in recent if l.get("homework_load_rating") == "just-right"
    )
    counter = int(sched.get("consecutive_just_right_count") or 0)
    if just_right_count >= 3 and counter >= 3:
        res.fail(
            f"just-right restore drift: observed {just_right_count} consecutive "
            f"'just-right' ratings in last 3 session logs AND "
            f"consecutive_just_right_count={counter} (>=3) — D-11 requires "
            f"restoring daily_target by +10% once the counter reaches 3 "
            f"consecutive 'just-right' ratings (after a prior reduction) and then "
            f"resetting consecutive_just_right_count to 0. The pending restore "
            f"has not been applied."
        )
        return
    res.pass_(
        f"just-right restore drift check: {just_right_count} recent 'just-right', "
        f"consecutive_just_right_count={counter} (consistent with D-11 ladder)"
    )


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
    """LOAD-01 / D-02 (P2-k): CORE grammar acquisition requires 3+ separate
    sessions of practice. WARN when an 'acquired' grammar concept has
    practice_count < 3, unless it is placement-exempt (a concept below the
    learner's initial_placement phase, pre-acquired during placement). Vocabulary
    has no practice_count field by schema design, so this floor is grammar-only.
    (Name retained for back-compat; historically checked only practice_count==0.)"""
    grammar = sm.get("grammar", {})
    placement_level = None
    if isinstance(profile, dict):
        placement_level = (profile.get("initial_placement") or {}).get("level") or None
    phase_order = {"A": 0, "B": 1, "C": 2, "D": 3}

    # Extract the phase letter from a placement level string. Documented formats
    # (docs/system-design.md:330): pre-A / early-A / late-A / early-B / mid-B /
    # early-C / mid-C, plus a bare letter ("B") or "B-conversational". Tokenize on
    # "-" and pick the token naming a phase — placement_level[0] would misread
    # "early-B" as phase "E" and "pre-A" as phase "P".
    placement_phase: str | None = None
    if placement_level:
        for token in str(placement_level).split("-"):
            if token.upper() in phase_order:
                placement_phase = token.upper()
                break

    for cid, entry in grammar.items():
        if not isinstance(entry, dict): continue
        if entry.get("status") != "acquired": continue
        pc = entry.get("practice_count") or 0
        if pc >= 3: continue
        # acquired grammar concept with fewer than 3 practice sessions
        concept_phase = cid[0].upper() if cid else None
        if (placement_phase
                and concept_phase in phase_order
                and placement_phase in phase_order
                and phase_order[concept_phase] < phase_order[placement_phase]):
            # Below placement level — placement-exempt from the session count
            res.pass_(f"Grammar '{cid}': acquired with practice_count={pc} (placement-exempt: below {placement_phase}-level placement)")
        else:
            res.warn(f"Grammar '{cid}': acquired with practice_count={pc} (< 3) — CORE acquisition requires 3+ separate sessions unless placement-validated")


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

    rs_schema = load_schema("skill-map")["receptive_skills"]
    valid_listening = _schema_enum(rs_schema, "listening", "children", "current_level")
    valid_reading = _schema_enum(rs_schema, "reading", "children", "current_level")
    valid_quality = _schema_enum(rs_schema, "listening", "children", "comprehension_quality")
    # schema enum omits null; the validator tolerates an absent/null value
    valid_lookup = _schema_enum(rs_schema, "reading", "children", "lookup_frequency") | {None}

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

    rs_schema = load_schema("skill-map")["receptive_skills"]
    valid_listening = _schema_enum(rs_schema, "listening", "children", "current_level")
    valid_reading = _schema_enum(rs_schema, "reading", "children", "current_level")

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
    # Drive per-resource enums from the schema's resources.item_shape (single
    # source of truth) — same pattern as the level enums above. None is tolerated
    # for the two nullable fields (trend/engagement are null until enough data).
    rt_fields = load_schema("resource-tracker")["fields"]
    valid_types = _schema_enum(rt_fields, "resources", "item_shape", "type")
    valid_trends = _schema_enum(rt_fields, "resources", "item_shape", "comprehension_trend") | {None}
    valid_engagement = _schema_enum(rt_fields, "resources", "item_shape", "learner_engagement") | {None}

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

        # Check enum values (top-level scalars)
        for fname, allowed in enum_fields.items():
            val = data.get(fname)
            if val is not None and val not in allowed:
                res.fail(f"Session log {f.name}: {fname}='{val}' is not a valid enum value (expected one of {sorted(str(v) for v in allowed if v is not None)})")

        # Check nested enums in list-of-dict fields (item_shape / item_schema).
        # Covers recasts[].uptake, recasts[].activity_stage,
        # assignments[].dialect_advisory (audit M10 — previously unvalidated).
        for fname, spec in fields_spec.items():
            if not isinstance(spec, dict):
                continue
            item_spec = spec.get("item_shape") or spec.get("item_schema")
            if not isinstance(item_spec, dict):
                continue
            item_enums = {
                k: set(v["enum"])
                for k, v in item_spec.items()
                if isinstance(v, dict) and "enum" in v
            }
            if not item_enums:
                continue
            items = data.get(fname)
            if not isinstance(items, list):
                continue
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                for k, allowed in item_enums.items():
                    val = item.get(k)
                    if val is not None and val not in allowed:
                        res.fail(
                            f"Session log {f.name}: {fname}[{i}].{k}='{val}' "
                            f"is not a valid enum value (expected one of "
                            f"{sorted(str(v) for v in allowed if v is not None)})"
                        )

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
    sched_header = leading_header(sched_path.read_text(encoding="utf-8")) if sched_path.exists() else ""
    atomic_write(sched_path, sched_header + yaml.dump(sched, default_flow_style=False, allow_unicode=True, sort_keys=False))

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
        health_header = leading_header(health_path.read_text(encoding="utf-8"))
        atomic_write(health_path, health_header + yaml.dump(health, default_flow_style=False, allow_unicode=True, sort_keys=False))
    else:
        res.warn("system-health.yaml missing — auto-fix applied to schedule.yaml but not logged to health file")

    res.pass_(
        f"Auto-fixed last_session_date: '{recorded}' → '{most_recent}' "
        f"(logged in system-health.yaml)"
    )


def check_phase_prereqs_acquired(sm: dict, sched: dict,
                                 res: ValidationResults) -> None:
    """P1-3 / LOAD-02 / D-03: a learner whose current_phase is past a transition
    must have that transition's CORE prerequisites at a status that reached
    acquisition — 'acquired' or 'automatic', or 'regressed' (which implies it was
    acquired earlier and later slipped, a path the regression ladder handles). A
    Core prereq still at unseen/introduced/practicing means the phase was advanced
    before the prereq was ever acquired — the guardrail violation. Dormant for
    Phase A (no prior transition), so it can never block a first session.

    Core prereq sets come from scripts/phase_prereqs.py (the single code-side
    source of truth, kept in lockstep with the prose by
    tests/test_phase_transition_parity.py). Values are ID prefixes matched against
    full skill-map keys (e.g. 'A-01' -> 'A-01-present-regular')."""
    phase = (sched or {}).get("current_phase") or ""
    letter = phase[:1].upper()
    prereqs = phase_prereqs.CORE_PREREQS_FOR_ENTRY.get(letter)
    if not prereqs:
        res.pass_(f"Phase prereq gate: current_phase '{phase or '(unset)'}' has no prior transition to check")
        return
    grammar = sm.get("grammar", {})
    reached = {"acquired", "automatic", "regressed"}
    violations = []
    for prefix in sorted(prereqs):
        matches = [e for cid, e in grammar.items()
                   if isinstance(e, dict) and (cid == prefix or cid.startswith(prefix + "-"))]
        if not matches:
            res.warn(f"Phase prereq gate: Core prereq '{prefix}' for phase '{phase}' has no matching skill-map grammar concept")
            continue
        if not any(m.get("status") in reached for m in matches):
            statuses = ", ".join(sorted({str(m.get("status")) for m in matches}))
            violations.append(f"{prefix} (status: {statuses})")
    if violations:
        res.fail(
            f"Phase prereq gate (LOAD-02/D-03): current_phase '{phase}' but these CORE "
            f"prerequisites never reached acquisition: {'; '.join(violations)}. A phase "
            f"must not be advanced until its Core prereqs are acquired."
        )
    else:
        res.pass_(f"Phase prereq gate: all {len(prereqs)} Core prereqs for entry into '{phase}' reached acquisition")


def check_consolidation_cap(sm: dict, sched: dict, session_logs: list,
                            res: ValidationResults) -> None:
    """P1-4 / consolidation guardrail (CLAUDE.md L183): the tutor must not
    introduce a NEW grammar concept while 3+ concepts (4 with carryover) are
    already in 'practicing'. Backstop: if the most recent session log lists a
    newly-introduced grammar concept AND, excluding those new concepts, the cap is
    still met or exceeded across grammar+vocabulary 'practicing' status, WARN — the
    introduction likely violated the cap. WARN (not FAIL) because this is a
    cumulative-state planning heuristic and the decision engine is the primary
    enforcement; aborting the session save would be disproportionate."""
    recent = [l for l in (session_logs or []) if isinstance(l, dict)]
    if not recent:
        res.pass_("Consolidation cap: no session logs to check")
        return
    new_ids = recent[-1].get("new_grammar_concepts_introduced") or []
    if not isinstance(new_ids, list) or not new_ids:
        res.pass_("Consolidation cap: latest session introduced no new grammar concept")
        return
    new_set = set(new_ids)
    carryover = (sched or {}).get("carryover_concepts") or []
    cap = 4 if carryover else 3
    practicing = [
        cid
        for section in ("grammar", "vocabulary")
        for cid, e in (sm.get(section) or {}).items()
        if isinstance(e, dict) and e.get("status") == "practicing" and cid not in new_set
    ]
    if len(practicing) >= cap:
        res.warn(
            f"Consolidation cap (CLAUDE.md L183): latest session introduced new grammar "
            f"{sorted(new_set)} while {len(practicing)} concept(s) are already 'practicing' "
            f"({', '.join(sorted(practicing))}) — cap is {cap} "
            f"({'4 with carryover' if carryover else '3, no carryover'}). Consolidate first."
        )
    else:
        res.pass_(f"Consolidation cap: {len(practicing)} practicing concept(s) (< cap {cap}) when a new concept was introduced")


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

    # CC-3 (C9): media-bank dialect tags must be covered by curriculum/dialects.yaml.
    # Pass dialects through even when None — the check fails loud on a missing
    # taxonomy rather than silently skipping (matches check-session-log.py).
    media_bank = load_yaml(CURRICULUM / "media-bank.yaml")
    dialects = load_yaml(CURRICULUM / "dialects.yaml")
    if media_bank is not None:
        check_media_bank_dialect_coverage(media_bank, dialects, res)
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
    if skill_map is not None:
        check_learner_interest_range(skill_map, res)
        check_learner_interest_staleness(skill_map, res)
        check_recast_uptake_stats_consistency(skill_map, res)
    check_session_filenames(res)
    check_session_logs(res)
    if schedule is not None:
        check_last_session_date(schedule, res, dry_run=args.dry_run)
        check_schedule_enums(schedule, res)
        check_onboarding_counter_range(schedule, res)
        # LOAD-07 / D-04 / D-06: study_time_budget consistency
        check_study_time_budget_consistency(schedule, has_sessions, res)
        # LOAD-04 / D-11: daily_target tier drift detectors — load the last 3
        # session logs by filename (YYYY-MM-DD sorts chronologically) and check
        # whether the consecutive_* counters have been advanced to match observed
        # homework_load_rating ratings. The too-much detector re-slices to the
        # last 2 internally; the just-right restore detector needs all 3.
        session_logs_recent: list = []
        sessions_dir = STATE / "sessions"
        if sessions_dir.exists():
            yaml_files = sorted(
                p for p in sessions_dir.glob("*.yaml") if p.is_file()
            )
            for p in yaml_files[-3:]:
                try:
                    with p.open() as f:
                        d = yaml.safe_load(f) or {}
                    if isinstance(d, dict):
                        session_logs_recent.append(d)
                except (OSError, yaml.YAMLError):
                    continue
        check_daily_target_tier_drift(schedule, session_logs_recent, res)
        check_just_right_restore_drift(schedule, session_logs_recent, res)
        check_placement_validation_consistency(schedule, res)
    if schedule is not None and skill_map is not None:
        check_carryover_concepts(schedule, skill_map, res)
        check_phase_prereqs_acquired(skill_map, schedule, res)
        check_consolidation_cap(skill_map, schedule, session_logs_recent, res)
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
