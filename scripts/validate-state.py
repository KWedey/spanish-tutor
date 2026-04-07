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


# --- Main ---------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Validate tutoring system state files")
    ap.add_argument("--verbose", action="store_true", help="Show PASS results in addition to WARN/FAIL")
    args = ap.parse_args()

    profile    = load_yaml(STATE / "learner-profile.yaml")
    skill_map  = load_yaml(STATE / "skill-map.yaml")
    schedule   = load_yaml(STATE / "schedule.yaml")
    health     = load_yaml(STATE / "system-health.yaml")

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
    check_session_filenames()

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
