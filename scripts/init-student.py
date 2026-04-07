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

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
_C = sys.stdout.isatty()
green = lambda t: f"\033[32m{t}\033[0m" if _C else t
yellow = lambda t: f"\033[33m{t}\033[0m" if _C else t
red = lambda t: f"\033[31m{t}\033[0m" if _C else t

# Template files keyed by path relative to ROOT. skill-map.yaml is reset
# in-place (too large for inline template) — see reset_skill_map().
TEMPLATES: dict[str, str] = {}

TEMPLATES["state/learner-profile.yaml"] = (
    "# Learner Profile — slow-changing facts about the learner\n"
    "# Updated rarely, typically during first session and at phase transitions.\n"
    "# Schema defined in docs/system-design.md\n\n"
    "schema_version: 1\n\n"
    "name: \"\"\nnative_language: English\ntarget_dialect: \"\"\nstarted: \"\"\n\n"
    "primary_goal: \"\"\ntarget_level: \"\"\nmilestone_goals: []\ngraduation_criteria: \"\"\n\n"
    "typical_weekday_minutes: 0\ntypical_weekend_minutes: 0\n"
    "preferred_session_time: \"\"\nmax_new_concepts_per_week: 2\nweekly_review_day: \"\"\n\n"
    "grammar_preference: \"\"\nerror_correction_preference: \"\"\n"
    "vocabulary_retention_method: \"\"\nmotivation_style: \"\"\nenergy_pattern: \"\"\n\n"
    "calibration:\n  self_report_accuracy: null\n  tendency: \"\"\n  trust_weight: 0.5\n\n"
    "motivation:\n  current_level: \"\"\n  streak_days: 0\n  longest_streak: 0\n"
    "  total_sessions: 0\n  days_since_last_milestone: 0\n  plateau_risk: false\n"
    "  high_motivation_triggers: []\n  low_motivation_triggers: []\n  preferred_recovery: \"\"\n\n"
    "input_hours:\n  listening_total: 0.0\n  reading_total: 0.0\n  last_updated: null\n\n"
    "tools:\n  srs: \"\"\n  pronunciation: \"\"\n  conversation_partner: \"\"\n"
    "  listening_primary: \"\"\n  reading_current: \"\"\n\nnotes: \"\"\n"
)

TEMPLATES["state/schedule.yaml"] = (
    "# Schedule — the tutor's current plan\n"
    "# Updated at the end of each session.\n"
    "# Schema defined in docs/system-design.md\n\n"
    "schema_version: 1\n\n"
    "current_phase: A-foundation\ncurrent_week: 1\n"
    "onboarding_complete: false\nautonomy_level: guided\n\n"
    "active_grammar:\n  primary: \"\"\n  secondary: \"\"\n  maintenance: []\n\n"
    "active_vocabulary:\n  primary: \"\"\n  review: []\n\n"
    "active_pronunciation:\n  focus: \"\"\n\n"
    "active_writing:\n  current_level: \"\"\n  journal_active: false\n\n"
    "weekly_topic:\n  topic: \"\"\n  vocabulary_cluster: \"\"\n"
    "  grammar_reinforcement: \"\"\n  started: \"\"\n\n"
    "fluency_accuracy_balance: accuracy-leaning\n\n"
    "fluency_days_this_week: 0\nlast_fluency_day: null\n\n"
    "grammar_queue: []\nvocabulary_queue: []\n\n"
    "sprint:\n  active: false\n  goal: \"\"\n  target_date: \"\"\n  focus_areas: []\n\n"
    "carryover_concepts: []\n\n"
    "anki_new_cards_per_session: 8\nanki_retirement_threshold_days: 60\n\n"
    "adjustment_log: []\n"
)

TEMPLATES["state/system-health.yaml"] = (
    "# System Health — meta-metrics on tutoring system effectiveness\n"
    "# Updated at end of each session. Reviewed in detail during weekly reviews.\n"
    "# Schema defined in docs/system-design.md\n\n"
    "schema_version: 1\n\n"
    "concepts_requiring_reteach_total: 0\naverage_sessions_to_acquire: 0\n"
    "reteach_rate_30d: 0.0\n\n"
    "homework_completion_rate_30d: 0.0\nhomework_reported_difficulty_avg: 0.0\n"
    "assignment_skip_patterns: []\n\n"
    "days_in_current_phase: 0\nconcepts_acquired_per_month: 0\n"
    "concepts_in_practicing_simultaneously: 0\n\n"
    "average_session_duration_30d: 0\nsession_frequency_30d: 0.0\n"
    "learner_initiated_topics_30d: 0\nsessions_rated_too_easy_30d: 0\n"
    "sessions_rated_too_hard_30d: 0\n\n"
    "anki_estimated_deck_size: 0\nanki_estimated_daily_review_minutes: 0\n\n"
    "last_validation_issues: []\nlast_system_review: null\n"
)

TEMPLATES["state/resource-tracker.yaml"] = (
    "# Resource Tracker — which external resources are in active rotation\n"
    "# Updated when resources are added, swapped, or engagement changes.\n\n"
    "schema_version: 1\n\nactive_resources: []\n\nretired_resources: []\n"
)

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
    integration_tested=False)

ZERO_VOCAB = dict(status="unseen", words_introduced=0, passive_known=0, active_known=0,
    weak_production=[], weak_recognition=[], last_practiced=None)

ZERO_PRONUN = dict(status="unseen", last_practiced=None, external_feedback="")


def reset_skill_map() -> None:
    """Load skill-map.yaml, zero all progress values, and rewrite."""
    path = STATE_DIR / "skill-map.yaml"
    if not path.exists():
        print(red(f"  MISSING: {path.relative_to(ROOT)}")); return
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for entry in (data.get("grammar") or {}).values():
        if isinstance(entry, dict):
            entry.update({k: v for k, v in ZERO_GRAMMAR.items()})
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset all student data to clean templates.")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    if not args.force:
        if input("This will erase all learning progress. Continue? [y/N] ").strip().lower() != "y":
            print("Aborted."); sys.exit(0)

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
    if vault_script.exists():
        r = subprocess.run([sys.executable, str(vault_script), "--full"],
                           cwd=str(ROOT), capture_output=True, text=True)
        print(green(f"  {r.stdout.strip()}") if r.returncode == 0
              else red(f"  Vault generation failed: {r.stderr.strip()}"))
    else:
        print(yellow("  SKIP: generate-vault.py not found"))

    print(f"\n=== Summary ===")
    print(f"  State files reset: {len(TEMPLATES) + 1}")  # +1 for skill-map
    print(f"  Data files removed: {total_removed}")
    print(green("\nStudent data has been reset to a clean state."))


if __name__ == "__main__":
    main()
