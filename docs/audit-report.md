# Spanish Fluency Tutor — Comprehensive Audit Report

> **Status: historical snapshot.** This audit was captured on 2026-04-11.
> Many findings have since been resolved in commits `eece2e3..088f8a0`
> (the C1-C3 and H1-H6 punchlist). Read this document as a record of what
> was found, not as a current punchlist.

**Date:** 2026-04-11
**Scope:** Pedagogical methodology, engineering quality, agent reliability, structural consistency
**Status:** All state files empty (no sessions conducted yet)

---

## Executive Summary

Four parallel specialist reviews examined the system across pedagogy/SLA, engineering, AI agent reliability, and structural consistency. The system is remarkably well-designed for its complexity — cross-references between 70+ skill-map entries and curriculum files are 100% clean, the assessment architecture (scaffolded/unscaffolded performance tracking) is genuinely sophisticated, and the decision engine reflects real SLA expertise.

The most critical issues cluster around **agent reliability**: the tutor agent must execute a 15-step post-session protocol, navigate ambiguous routing conditions, and mentally compute a multi-dimensional scoring algorithm — all of which are high-risk for a stateless LLM. Engineering gaps (schema drift, missing validation, duplicate code) are fixable but could cause silent state corruption once sessions begin.

| Severity | Count |
|----------|-------|
| Critical | 6 |
| Major | 35 |
| Minor | 38 |
| Suggestion | 14 |

---

## Implementation Plan — Execution Waves

All findings are fixable before the first session. Waves are grouped by **file ownership** so agents can work in parallel without conflicts. Each wave's agents are independent — launch them simultaneously. Wave 2 depends on Wave 1 schemas. Wave 3 depends on Wave 2 code.

### Wave 1 — Parallel File Edits (no code, all independent)

Launch 7 agents simultaneously. Each owns a non-overlapping set of files.

#### Agent 1: CLAUDE.md Overhaul (~26 findings)

Owns: `CLAUDE.md`

| ID | Fix |
|----|-----|
| A-22 | Delete lines 205-224 (injected gstack skill routing section) |
| A-01 | Routing table: change weekly review condition to "Today's day-of-week matches `weekly_review_day` in `learner-profile.yaml`" |
| A-02 | Add Step 2b or inline 3-line fluency-day determination formula in Step 3 |
| A-07 | Add sub-condition to onboarding row: "If gap >= 3 days, also load `return-session.md` for diagnostic" |
| A-08 | Change fluency row to load BOTH `fluency-activities.md` AND `decision-engine.md` |
| A-04 | Split Step 4 into "Step 4a — Pre-session conditional loads" and "Mid-session triggers" section under Standard Session Flow |
| A-05 | Move Step 1b to after Step 3, or add explicit reconciliation note about partial-session + routing interaction |
| A-09 | Change onboarding row to: "Load `curriculum/onboarding/session-NN.md` where NN = `current_onboarding_session` from `schedule.yaml`" |
| A-21 | Replace `session_status: micro` reference with duration check (`duration_minutes < 15`) |
| A-17 | Reframe repair phrase guardrail: "Highest-priority concept through session 5. If not automatic by session 5, continue as primary focus." |
| A-29 | Add to Conversation Practice section: "During free conversation (Stage 4), follow general rules. Override table applies only during structured Main Lesson activities." |
| P-12 | Change correction rule: "max 3 explicit corrections per segment; recasts unlimited. Scale to length: 2-3 for 5 min, up to 5 for 10 min." |
| P-24 | Language of Instruction table: Phase A from 80/20 to 60/40 English/Spanish |
| A-19 | Correct "~150 lines" claim. Add note about selective skill-map reading as learner progresses. |
| A-06 | Step 1 item 9: change "yesterday" to "most recent journal entry written since last session" |
| A-10 | Document whether maintenance-mode learners still get weekly reviews |
| A-15 | Renumber step 7b as its own step (unrelated to step 7) |
| A-18 | Change guardrail to exact field names: "error_rate_drills < 0.10 AND error_rate_production < 0.10" |
| A-23 | Change cross-ref from `docs/system-design.md` to `decision-engine.md, loaded at startup` |
| A-24 | Add: "Scale proportionally to stated time. Under 25 min: drop Conversation Practice, embed observation into Main Lesson." |
| A-27 | Add: "If logs exist but `last_session_date` null, set from most recent log and log the fix." |
| A-30 | Add "(in `learner-profile.yaml`)" to weekly review routing row |
| A-32 | Move `last_session_date` update from step 3b to after step 7 |
| A-33 | Merge Core Philosophy and Tone into single "Voice & Approach" section |
| A-34 | Remove Return Protocol section (2 lines, duplicates routing table) |
| A-35 | Consolidate Error Correction bullets into table with one-line preamble |

**Verification:** After all edits, count final line count and confirm no internal contradictions in routing table.

#### Agent 2: Tutor Guides (~18 findings)

Owns: all files in `curriculum/tutor-guides/`

| ID | File | Fix |
|----|------|-----|
| P-18 | `decision-engine.md` | Add durability weighting: `DECAY_ADJUSTED = DECAY * (1 - min(practice_count / 20, 0.7))` |
| P-27 | `decision-engine.md` | Remove NEED cap for politeness-formulas and register-shifting. Keep cap for regional-awareness and humor-idioms. |
| P-19 | `decision-engine.md` | Add: if concept interleaved 5+ times but never primary in same period, elevate to primary |
| A-20 | `decision-engine.md` | Add 2-3 worked scoring examples for agents to pattern-match against |
| P-01 | `input-orchestration.md` | Section 1 Step 4: change Phase A from "supplementary" to "required from session 3." Add 3-5 min in-session tutor-speaks-Spanish segment. |
| P-15 | `input-orchestration.md` | Reduce L2 minimum hours from 20 to 10-15. Add note about counting in-session tutor Spanish. |
| P-16 | `input-orchestration.md` | Add passive vocab inference formula: +3-5 words per 10 min comprehended input at level |
| P-34 | `input-orchestration.md` | Add note: when receptive > productive by 1+ level, assign more input homework |
| P-31 | `first-session.md` | Change placement pre-population: set `performance_unscaffolded: null` (untested) instead of "competent" |
| P-05 | `onboarding-guide.md` | Add ser/estar avoidance guidance for sessions 2-4: restrict production to contexts minimizing ser/estar demand |
| A-16 | `onboarding-guide.md` | Add concurrent concept cap (max 3 practicing) explicitly |
| S-14 | `return-session.md` | Add: if `autonomy_level` is `maintenance`, also load `maintenance-mode.md` regression section |
| A-26 | `return-session.md` | Add: if gap 3-5 days AND homework completed AND parking-lot has entries, run standard session with brief check-in |
| S-16 | `return-session.md` | Add: if partial session + 3-day gap, run return diagnostic first, then resume interrupted content if retained |
| P-22 | `l1-interference-protocol.md` | Add awareness-raising phase before intensive drilling for fossilized errors |
| P-13 | `error-correction.md` (in activities/) | Add recast salience techniques: stress corrected element, rising intonation, partial recast |
| P-29 | `emotional-intelligence.md` | Add SDT diagnostic when motivation drops: autonomy, competence, or relatedness deficit? |
| P-32 | `phase-transition-guide.md` | Add brief writing component to B→C (5 min narration) and C→D (8 min opinion piece) |
| P-30 | `weekly-review-guide.md` | Add "just-right streak" counter: 3+ consecutive just-right = preserve calibration |
| P-09 | `decision-engine.md` or `weekly-review-guide.md` | Require min 8-10 observations per context before using error rate for advancement. Below threshold: rely on qualitative + extra session. |
| P-10 | `decision-engine.md` | Don't compute error_trend until 5+ sessions of data. Below: "insufficient data." |
| P-20 | `decision-engine.md` | Add recency weight: 7 days full confidence, 8-30 moderate, 31-60 low + verify |

#### Agent 3: Curriculum Data Files (~10 findings)

Owns: `curriculum/l1-interference.yaml`, `curriculum/listening-progression.yaml`, `curriculum/reading-progression.yaml`, `curriculum/onboarding/session-*.md`, `curriculum/grammar/` concept files, `curriculum/cultural/`

| ID | File | Fix |
|----|------|-----|
| P-21 | `l1-interference.yaml` | Add 4 entries: personal-a omission (preempt A-04), reflexive pronoun omission (preempt B-05), ser-in-progressive (preempt B-08), question word order (preempt A-05) |
| S-09 | `l1-interference.yaml` | Fix `preempt_at: vocabulary-introduction` and `tier2-weather-seasons` — either map to real concept IDs or add comment explaining convention |
| P-15 | `listening-progression.yaml` | Reduce L2 minimum hours from 20 to 10-15 |
| P-28 | `curriculum/cultural/register-shifting.md` + `state/skill-map.yaml` cultural section | Move `introduced_at_phase` from D to B for register_shifting. Add progression notes: basic tú/usted at B, softeners at C, full control at D. |
| P-33 | `curriculum/onboarding/session-01-discovery.md` | Extend pronunciation check-in from 2-3 min to 4-5 min |
| P-33 | `curriculum/onboarding/session-02.md` through `session-05.md` | Add recurring 2-min pronunciation warmup segment |
| P-05 | `curriculum/onboarding/session-02.md` through `session-04.md` | Add explicit ser/estar avoidance notes: restrict activities to action verbs and routines |
| P-03 | Sample grammar concept files | Add optional comprehension-check micro-step between Stage 1 and Stage 2 |
| P-08 | `curriculum/grammar/C-intermediate/01-present-subjunctive.md` | Add B-04 as soft prerequisite with note |
| P-06 | `curriculum/grammar/B-conversational/` | Add note about Phase B being densest phase — set expectations |

#### Agent 4: Schema Files (~8 findings)

Owns: all files in `schemas/`

| ID | File | Fix |
|----|------|-----|
| E-10 | `schemas/learner-profile.schema.yaml` | Add `initial_placement` map with 8 children (level, date, self_report, grammar_result, vocabulary_observation, reading_result, confidence, evidence_summary) |
| E-11 | `schemas/schedule.schema.yaml` | Add `placement_validation` map, `topic_history` list, `session_number` field |
| E-12 | `schemas/system-health.schema.yaml` | Add `placement_validation_metrics`, `goal_tracking`, `session_difficulty_tracking` maps |
| E-13/S-03 | `schemas/session-log.schema.yaml` | Add `decision_engine_trace` field |
| S-05 | `schemas/skill-map.schema.yaml` | Add `schema_version` field |
| E-14 | `schemas/skill-map.schema.yaml` | Add `fields` wrapper or document the different structure convention |
| A-21 | `schemas/session-log.schema.yaml` | Either add `micro` as valid `session_status` enum value, or remove if CLAUDE.md switches to duration check |

#### Agent 5: Documentation (~10 findings)

Owns: `docs/system-design.md`, `docs/session-log-example.yaml`, `docs/progress-report-template.md`, `STUDENT-GUIDE.md`, `SETUP.md`, `requirements.txt`

| ID | File | Fix |
|----|------|-----|
| S-01 | `docs/system-design.md` | Add `schemas/`, `transcripts/`, `tests/`, undocumented files to directory tree |
| S-02/A-28 | `docs/system-design.md` | Change line 219 from "Phase C+" to "Phase B+" |
| S-06 | `docs/system-design.md` | Add A-08 and A-09 to directory tree |
| S-07 | `docs/system-design.md` | Add `input-orchestration.md`, `session-variety.md`, `phase-transition-guide.md` to conditional load table |
| S-24 | `docs/system-design.md` | Add `pronunciation-practice.md` to activities tree |
| A-19 | `docs/system-design.md` | Correct "~150 lines" to actual count |
| P-09 | `docs/system-design.md` | Add minimum observation count requirement to assessment section |
| P-20 | `docs/system-design.md` | Add error rate recency weighting description |
| S-04 | `docs/session-log-example.yaml` | Add `input_reviewed`, `interleaved_concepts`, `session_difficulty_rating`, `decision_engine_trace`, assignment-level `retrieval_target`/`input_minutes` |
| S-20 | `STUDENT-GUIDE.md` | Change "Starting around Phase B" to "Starting after onboarding (around session 11+)" for journaling |
| P-25 | `STUDENT-GUIDE.md` | Add recommendation for learner to set calendar reminders for maintenance sessions |
| E-32 | `SETUP.md` | Change Python 3.6+ to Python 3.10+ |
| E-31 | Create `requirements-dev.txt` | Add `pytest>=7.0` |

#### Agent 6: Vault & Obsidian Config (~5 findings)

Owns: `vault/`, `.obsidianignore`

| ID | File | Fix |
|----|------|-----|
| S-11 | `vault/Home.md` | Fix broken `[[Parking Lot]]` wiki-link — change to `[[parking-lot|Parking Lot]]` |
| S-13 | `vault/Getting Started.md` | Upgrade Templater from "recommended" to "required", or add manual date fallback |
| S-21 | Create `.obsidianignore` | Hide system dirs from learner: `state/`, `scripts/`, `schemas/`, `docs/`, `tests/`, `curriculum/`, `.claude/`, `.git/` |
| P-02 | `vault/` or tutor guide | Add typed-fluency metric note (response latency vs oral benchmarks) |

#### Agent 7: State Files (~3 findings)

Owns: `state/schedule.yaml`, `state/skill-map.yaml`

| ID | File | Fix |
|----|------|-----|
| A-09 | `state/schedule.yaml` | Add `current_onboarding_session: 1` field |
| P-28 | `state/skill-map.yaml` | Update register_shifting `introduced_at_phase` from D to B |
| E-22 | `state/schedule.yaml` | Add `session_number: 0` if it should be the single source of truth |

---

### Wave 2 — Script Changes (after Wave 1 schemas are final)

Launch 5 agents simultaneously.

#### Agent 8: validate-state.py + shared.py (~10 findings)

Owns: `scripts/validate-state.py`, `scripts/shared.py`

| ID | Fix |
|----|-----|
| E-01 | Unify `load_yaml` into single version in `shared.py` that handles missing files (return `None`). Remove duplicate in validate-state.py. |
| E-02 | Add `try/except yaml.YAMLError` to `shared.load_yaml` |
| E-03 | Add `check_session_log()` function: load each session file, check against schema, validate required fields and enum values |
| E-04 | Add `check_required_fields(data, "resource-tracker", "resource-tracker")` to resource-tracker validation |
| E-05 | Change acquired error threshold from > 0.15 to > 0.10 |
| E-06 | Refactor `results` from module-level global to parameter or class |
| E-29 | Extend `check_schedule_refs` to validate secondary, maintenance, vocabulary, pronunciation refs |
| E-30 | Add cross-validation between resource-tracker and skill-map for receptive skill levels |
| S-18 | Add pronunciation cross-reference validation to `check_curriculum_cross_refs` |

#### Agent 9: generate-vault.py (~5 findings)

Owns: `scripts/generate-vault.py`

| ID | Fix |
|----|-----|
| E-07 | Add nested dict handling to `yaml_frontmatter()` or guard against nested values |
| E-09 | Add format validation to ID-to-title functions with meaningful error on unexpected format |
| E-24 | Preserve original frontmatter field order or sort deterministically to minimize git diffs |
| E-27 | Add YAML error handling for schedule file load |
| S-12/S-22 | Add `vault/Progress/` file generation (Grammar Progress, Vocabulary Progress, Weekly Reports, Milestones) to `--full` mode |

#### Agent 10: init-student.py + migrate-state.py (~3 findings)

Owns: `scripts/init-student.py`, `scripts/migrate-state.py`

| ID | Fix |
|----|-----|
| E-08 | Add `isinstance(entry, dict)` guard for cultural_awareness entries in `reset_skill_map` |
| E-25 | Extend migration entry format to support callable transforms alongside additive entries |
| E-26 | Fix header preservation to handle blank lines between comments and YAML body |

#### Agent 11: New Scripts — post-session.sh + archive-sessions.py (~3 findings)

Owns: new files `scripts/post-session.sh`, `scripts/archive-sessions.py`

| ID | Fix |
|----|-----|
| A-11 | Create `scripts/post-session.sh` that automates: vault generation, 60-day archival, state validation, session log verification, and git commit. Reduce agent's post-session protocol from 15 steps to ~7. |
| E-21/S-17 | Create `scripts/archive-sessions.py` (or integrate as `--archive` flag): move session logs older than 60 days to `state/sessions/archive/` |
| E-20 | Add atomic write helper to `shared.py`: write to temp file, then `os.rename()`. Update all state-writing scripts to use it. |

#### Agent 12: test-error-recovery.py (~1 finding)

Owns: `scripts/test-error-recovery.py`

| ID | Fix |
|----|-----|
| E-28 | Copy state directory to temp location before mutating. Run validator against temp path. (Requires making validator's STATE path configurable via flag or env var — coordinate with Agent 8.) |

---

### Wave 3 — Tests (after Wave 2 code is final)

Launch 2 agents simultaneously.

#### Agent 13: Test Fixture Alignment + New Validator Tests

Owns: `tests/conftest.py`, `tests/test_validate_state.py`

| ID | Fix |
|----|-----|
| E-15 | Align `MINIMAL_LEARNER_PROFILE`, `MINIMAL_SYSTEM_HEALTH`, and other fixtures with actual schema required fields |
| E-16 | Add tests for: `check_required_fields`, `check_learner_profile`, `check_schedule`, `check_system_health`, `check_curriculum_cross_refs`, `check_schedule_refs`, `check_carryover_concepts`, `check_integration_tested_with`, `check_session_filenames`, `check_placement_validation_consistency` |
| E-19 | Add `MINIMAL_SESSION_LOG` fixture |
| E-03 | Add tests for new `check_session_log` function |

#### Agent 14: Other Test Fixes

Owns: `tests/test_generate_vault.py`, `tests/test_migrate_state.py`

| ID | Fix |
|----|-----|
| E-17 | Replace real skill-map dependency with synthetic fixture in `test_generates_expected_file_count` |
| E-18 | Add integration test that calls `migrate_mod.main()` end-to-end with monkeypatched args |

---

### Wave 4 — Final Verification

Single agent. After all waves complete:

1. Run `python3 scripts/validate-state.py` — all checks pass
2. Run `python3 -m pytest tests/ -v` — all tests pass (including new ones)
3. Run `python3 scripts/generate-vault.py --full` — vault generates cleanly
4. Verify CLAUDE.md has no internal contradictions (routing table consistent with guardrails)
5. Verify all schema files match their corresponding state files
6. Commit all changes with descriptive message

---

### Agent Count Summary

| Wave | Agents | Parallel? | Depends On |
|------|--------|-----------|------------|
| Wave 1 | 7 | Yes, all parallel | Nothing |
| Wave 2 | 5 | Yes, all parallel | Wave 1 (schemas) |
| Wave 3 | 2 | Yes, both parallel | Wave 2 (code) |
| Wave 4 | 1 | Sequential | Waves 1-3 |
| **Total** | **15 agents** | | |

---

## Detailed Findings

### 1. Agent Reliability

#### Critical

**A-01 | Routing: weekly review day lookup unspecified**
- File: `CLAUDE.md:57`
- The routing condition "Today is the weekly review day" doesn't specify which file contains `weekly_review_day` or how to compare a day-of-week string to today's date.
- **Fix:** Change condition to: "Today's day-of-week matches `weekly_review_day` in `learner-profile.yaml`". Add note that the agent determines today's date from the system.

**A-02 | Routing: fluency day algorithm not accessible**
- File: `CLAUDE.md:59`
- "Today is a fluency day" requires a multi-step algorithm defined only in `docs/system-design.md` comments, not in CLAUDE.md or any loaded guide. The algorithm checks `fluency_days_this_week`, `last_fluency_day`, current phase, and remaining days.
- **Fix:** Inline a 3-line fluency-day determination formula in CLAUDE.md Step 3, or add a Step 2b referencing the algorithm location.

**A-07 | Routing: onboarding + return session conflict**
- File: `CLAUDE.md:51-60`
- If `onboarding_complete` is false AND gap >= 3 days, onboarding fires first (higher in table). A learner returning mid-onboarding gets no regression check — the return-session guide's diagnostic logic is skipped entirely.
- **Fix:** Add: "If `onboarding_complete` is false AND gap >= 3 days, load BOTH `onboarding-guide.md` AND `return-session.md`. Run regression diagnostic for concepts covered so far, then resume onboarding."

**A-19 | Cognitive load: ~25-30K tokens before first greeting**
- Files: `CLAUDE.md`, all state files, tutor guides
- system-design.md claims CLAUDE.md is "~150 lines" — it's 224 lines / ~17KB. Total startup read for a standard session: ~25-30K tokens (CLAUDE.md + state files + decision engine + input orchestration + l1-interference protocol). Manageable but should be documented accurately.
- **Fix:** Correct the "~150 lines" claim. Consider reading only active/practicing/regressed concepts from skill-map rather than the full file. Add offset/limit guidance for large state files.

**A-22 | Injected gstack skill routing in CLAUDE.md**
- File: `CLAUDE.md:205-224`
- Lines 205-224 contain software development skill routing (ship, deploy, QA, code review, etc.) from gstack tooling. Completely unrelated to Spanish tutoring. Could cause the agent to invoke development tools if the learner says something that pattern-matches (e.g., "let's review what we've learned").
- **Fix:** Delete lines 205-224 from CLAUDE.md.

**A-28 | Fluency phase contradiction: B+ vs C+**
- Files: `CLAUDE.md:59`, `docs/system-design.md:219`, `curriculum/tutor-guides/fluency-activities.md:3`, `decision-engine.md:127`
- system-design.md says "Phase C+" for fluency activities. CLAUDE.md, fluency-activities.md, and the decision engine all say "Phase B+". Decision engine specifies frequency: 1x/week Phase B, 2x/week Phase C, every session Phase D.
- **Fix:** Change system-design.md line 219 from "Phase C+" to "Phase B+".

#### Major

**A-03 | Startup: no guidance for empty session directory**
- File: `CLAUDE.md:19-29`
- "Read 3 most recent files in `state/sessions/`" — no guidance when directory is empty or has < 3 files. Agent might count `.gitkeep` or `archive/` subdirectory.
- **Fix:** Add: "List only `.yaml` files in `state/sessions/` (excluding `archive/` and dotfiles). If fewer than 3 exist, read all. If none, this is the first session."

**A-04 | Step 4 mixes pre-session and runtime triggers**
- File: `CLAUDE.md:66-75`
- "Learner mentions a real-world encounter? Switch to real-world-debrief.md" is a runtime trigger, not a startup check. Grouped with genuine pre-session conditions.
- **Fix:** Split into "Step 4a — Pre-session conditional loads" and a separate "Mid-session triggers" section under Standard Session Flow.

**A-05 | Step 1b runs before session routing**
- File: `CLAUDE.md:31-37`
- Partial-session continuity check executes before the agent knows what session type to run. If a partial session was a weekly review, the agent must hold those instructions while completing Steps 2-4.
- **Fix:** Move Step 1b after Step 3, or add: "Step 1b determines continuity. Step 3 routing should incorporate: if prior session was partial, match that type unless a higher-priority condition applies (e.g., return session overrides partial resumption)."

**A-08 | Fluency routing prevents decision engine loading**
- File: `CLAUDE.md:59`
- Routing table's "first match wins" means fluency day loads `fluency-activities.md` INSTEAD of standard session. But the guardrail (line 197) says "On fluency days, still run decision engine for concept selection." The routing table contradicts the guardrail.
- **Fix:** Change fluency row to load both `fluency-activities.md` + `decision-engine.md`, or make fluency a modifier of standard sessions rather than a separate route.

**A-09 | Onboarding session number not tracked**
- File: `CLAUDE.md:54`
- "Load today's `curriculum/onboarding/session-NN.md`" — agent must compute NN from session log count. Breaks if consolidation sessions were inserted, sessions were partial, or learner placed mid-onboarding.
- **Fix:** Add `current_onboarding_session: 1` to `schedule.yaml`. Agent reads this directly. Increment at end of each onboarding session.

**A-11 | Post-session protocol: 15+ steps, high failure risk**
- File: `CLAUDE.md:147-174`
- 15 numbered steps (~22 discrete operations) must execute silently after every session. Steps 8-15 involve Python scripts, vault generation, archival, validation, transcripts, and git commits. By this point the agent has consumed significant context on the lesson. Later steps are most likely to be skipped or botched.
- **Fix:** Create `scripts/post-session.sh` that automates steps 8, 10, 11-15 (vault generation, archiving, validation, transcript, commit). Reduce agent responsibility to: (1) write state files, (2) run script, (3) verify output.

**A-12 | Session log schema not loaded for all session types**
- File: `CLAUDE.md:147-148`
- Step 1 says "Write session log (use schema from `docs/system-design.md`)" but the agent only reads system-design.md for standard sessions. First session and onboarding sessions never load it.
- **Fix:** Add: "Before writing session log, re-read the session log schema from `docs/system-design.md` (Session Logs section)." Or extract to a standalone reference file.

**A-13 | Vault generation: mixed script + manual steps**
- File: `CLAUDE.md:164`
- Step 8 says "run generate-vault.py" then "manually write" daily notes, weekly reports, milestones. The split between automated and manual is unclear.
- **Fix:** Either have the script handle everything, or clearly separate: "Step 8a: Run script (handles frontmatter + Roadmap). Step 8b: Manually write these files (the script does NOT create them): [explicit list]."

**A-14 | State update cross-references require re-reading guides**
- File: `CLAUDE.md:149-157`
- Steps 2b-2f require input-orchestration.md Section 4 for level changes, but input-orchestration.md may not have been loaded (not loaded for onboarding or return sessions).
- **Fix:** Include actual rules inline for each sub-step rather than cross-referencing. Or create a "state update reference" doc loaded specifically during updates.

**A-16 | Concurrent concept cap not enforced during onboarding**
- File: `CLAUDE.md:179`
- "Never advance if 3+ concepts in practicing" is in CLAUDE.md guardrails and decision engine, but the decision engine isn't loaded during onboarding. The onboarding guide doesn't reference this cap.
- **Fix:** Add the cap to the onboarding guide explicitly.

**A-17 | Communication repair guardrail is outcome-based, not actionable**
- File: `CLAUDE.md:189`
- "Must be automatic by session 5" — agent can't enforce an outcome. No fallback if session 5 arrives and phrases aren't automatic.
- **Fix:** Reframe: "Communication repair phrases are highest-priority through session 5. If not automatic by session 5, continue as primary focus until achieved before introducing new grammar."

**A-20 | Decision engine scoring too complex for reliable mental execution**
- File: `curriculum/tutor-guides/decision-engine.md`
- 5-dimension formula with table lookups, modifiers, and variety penalties. ~15 data points per candidate. Phase B learner has 10+ candidates. High cognitive load mid-session.
- **Fix:** Consider whether a simpler heuristic ("pick highest-NEED concept not practiced in 3+ days") would be more reliably executed. Or provide worked examples the agent can pattern-match against.

**A-25 | Transcript saving relies on agent memory reconstruction**
- File: `CLAUDE.md:174`
- "Save full session conversation to transcripts/" — agent must reconstruct from memory after a full session. Likely to produce incomplete/paraphrased output.
- **Fix:** Implement via Claude Code hook or wrapper that captures conversation externally. If approximate is acceptable, state: "Write a detailed session narrative, not a verbatim transcript."

**A-26 | Return session: no shortcut for short gaps with continued study**
- File: `CLAUDE.md:55`, `curriculum/tutor-guides/return-session.md`
- A 3-day gap where the learner did homework daily still triggers full return protocol with regression diagnostic.
- **Fix:** Add: "If gap is 3-5 days AND most recent session log shows homework completed AND parking-lot has new entries, run standard session with brief check-in instead of full return protocol."

**A-29 | Error correction: activity override scope unclear**
- File: `CLAUDE.md:102-103, 129-143`
- "Do NOT interrupt" in Conversation Practice vs "Recast, immediate" in Stage 3 guided production. If conversation overlaps guided production, instructions conflict. Override table says it overrides but Conversation Practice doesn't reference the table.
- **Fix:** Add to Conversation Practice: "During free conversation (Stage 4), follow general error correction rules. The activity-specific override table applies only during structured activities in Main Lesson."

**A-31 | State update ordering: no error handling between steps**
- File: `CLAUDE.md:147-174`
- Step 8 (vault generation) depends on step 1 (session log). If step 1 fails silently, step 8 produces incorrect output. No checkpoints between steps.
- **Fix:** Add: "After step 7: verify all state files parse correctly before proceeding to vault generation. If any write failed, stop and report."

#### Minor

**A-06 | Journal: "yesterday" vs "most recent since last session"**
- File: `CLAUDE.md:29`
- "Read journal entry for yesterday" — misses entries from 2+ days ago if there was a gap.
- **Fix:** Change to "Read the most recent journal entry written since the last session."

**A-10 | Maintenance-mode learners: no weekly review**
- File: `CLAUDE.md:56-58`
- Maintenance mode (row 5) fires before weekly review (row 6). Not documented whether this is intentional.
- **Fix:** Document explicitly whether maintenance learners still get weekly reviews.

**A-15 | Step 7 and 7b are unrelated operations**
- File: `CLAUDE.md:162`
- Step 7 (partial flag) and 7b (weekly summary) grouped under same number.
- **Fix:** Give weekly-review-specific steps their own block or renumber.

**A-18 | Acquisition guardrail phrasing could be more precise**
- File: `CLAUDE.md:192`
- "error rates < 10% (both drill and production)" — parenthetical easy to miss.
- **Fix:** Use exact field names: "error_rate_drills < 0.10 AND error_rate_production < 0.10".

**A-23 | Wrong cross-reference for decision engine**
- File: `CLAUDE.md:94`
- Points to `docs/system-design.md` but the actual protocol is in `curriculum/tutor-guides/decision-engine.md`.
- **Fix:** Change to "see `decision-engine.md`, loaded at startup."

**A-24 | Session time scaling not addressed**
- File: `CLAUDE.md:85-114`
- Time estimates total 28-48 min but sessions can be 20-60 min. No scaling guidance.
- **Fix:** Add: "Scale proportionally to stated available time. For sessions under 25 min, drop Conversation Practice and embed error observation into Main Lesson."

**A-27 | Gap detection edge case: null date + no logs**
- File: `CLAUDE.md:62`
- First session handles this via routing priority, but if logs exist without `last_session_date`, fallback logic could produce unexpected results.
- **Fix:** Add: "If session logs exist but `last_session_date` is null, set from most recent log and log the fix."

**A-30 | Weekly review day source file not specified in routing table**
- File: `CLAUDE.md:57`
- Routing table doesn't say `weekly_review_day` is in `learner-profile.yaml`.
- **Fix:** Add "(in `learner-profile.yaml`)" to the routing table row.

**A-32 | `last_session_date` updated too early in protocol**
- File: `CLAUDE.md:156`
- Step 3b updates the date before session log is written. If interrupted, next session calculates 0-day gap despite incomplete session.
- **Fix:** Move to after step 7 or immediately before commit.

#### Suggestions

**A-33** — Core Philosophy and Tone sections overlap. Merge into single "Voice & Approach" section.
**A-34** — Return Protocol section (2 lines) adds nothing beyond routing table. Remove.
**A-35** — Error Correction bullets and activity override table overlap. Consolidate into table with one-line preamble.

---

### 2. Pedagogy & SLA

#### Major

**P-01 | Comprehensible input underweighted in Phase A-B**
- Files: `CLAUDE.md`, `curriculum/tutor-guides/input-orchestration.md`
- Session allocates 15-25 min to grammar/drills, 5-10 min to conversation. Input homework is "supplementary" in Phase A. SLA research (Krashen) positions comprehensible input as the primary acquisition driver.
- **Fix:** Add 3-5 min in-session "tutor speaks Spanish" segment in Phase A (narration with context support). Make input homework required from session 3. Rebalance input-orchestration.md Step 4 Phase A description.

**P-05 | Ser/estar delayed to session 5 despite high fossilization risk**
- Files: `curriculum/onboarding/`, `curriculum/l1-interference.yaml`
- Sessions 2-4 require "to be" constantly but learner has no instruction. L1 interference map rates this "severity: high" with "Can fossilize permanently if not caught early." Three sessions of gentle recasting may not suffice.
- **Fix:** Either move ser/estar to session 3, or restrict sessions 2-4 production to contexts minimizing ser/estar demand (action verbs, routine descriptions). Add explicit avoidance guidance to session-02 through session-04.

**P-09 | Error rate sample size too small for acquisition decisions**
- File: `docs/system-design.md:329-372`
- Rates are rolling averages over last 5 practice instances. With 3 sessions, rates can be based on 3-5 observations per context. One lucky session can swing rate from 20% to 5%.
- **Fix:** Require minimum 8-10 observations per context (drill, production) before using rate for advancement. Below threshold, rely on qualitative assessment (performance_scaffolded/unscaffolded) and require an additional session.

**P-12 | Max-3-correction rule conflates recasts and explicit corrections**
- File: `CLAUDE.md:129-143`
- Three recasts (low cognitive load, often unnoticed) vs three explicit corrections (overwhelming) are capped identically. Research (Lyster & Ranta) shows effectiveness depends on type, not count.
- **Fix:** Change to "max 3 explicit corrections per conversation segment; recasts unlimited." Scale to conversation length: 2-3 for 5 min, up to 5 for 10 min.

**P-15 | L2 listening minimum hours too conservative**
- File: `curriculum/listening-progression.yaml`
- 20-hour minimum at L2 = ~27 weeks at typical homework pace. Dreaming Spanish recommends ~50 hours total across Super Beginner + Beginner combined.
- **Fix:** Reduce L2 minimum to 10-15 hours. The two-consecutive-weeks criterion + comprehension quality checks are the real gates. Consider counting in-session tutor Spanish toward hours.

**P-18 | DECAY scoring ignores concept durability**
- File: `curriculum/tutor-guides/decision-engine.md`
- Linear decay curve treats all concepts equally. A concept practiced 20 times is far more durable than one practiced 3 times, but both get same DECAY score at same days-since-last-practiced.
- **Fix:** Weight by practice count: `DECAY_ADJUSTED = DECAY * (1 - min(practice_count / 20, 0.7))`. Concept practiced 20+ times gets 30% of raw decay score.

**P-21 | L1 interference map missing 4 significant patterns**
- File: `curriculum/l1-interference.yaml`
- Missing: personal-a omission (preempt at A-04), reflexive pronoun omission (preempt at B-05), ser-in-progressive (preempt at B-08), question word order (preempt at A-05).
- **Fix:** Add these four entries with common_errors, severity, and preempt_at fields.

**P-24 | Phase A language ratio too English-heavy**
- File: `CLAUDE.md` Language of Instruction table
- 80% English / 20% Spanish in Phase A provides minimal target-language input during sessions.
- **Fix:** Shift to 60% English / 40% Spanish from Phase A start. Use Spanish for greetings, praise, simple instructions ("muy bien", "otra vez", "escucha", "repite"). Reserve 80/20 only for explicit grammar explanation segments.

**P-27 | Cultural competence systematically deprioritized**
- Files: `CLAUDE.md:74`, `curriculum/tutor-guides/decision-engine.md`
- NEED capped at 5 + "never the primary focus" means cultural concepts rarely surface when any grammar concept is active.
- **Fix:** Remove cap for politeness formulas and register shifting (functionally equivalent to grammar for communication success). Keep cap for regional awareness and humor/idioms. Integrate cultural objectives into grammar concept files (e.g., imperatives B-09 should include register-appropriate softeners).

**P-31 | Placement pre-populates unobserved performance as "competent"**
- File: `curriculum/tutor-guides/first-session.md`
- All concepts below placement level get `performance_unscaffolded: "competent"` without observation. A mid-B placement marks ~17 concepts as competent. Validation only checks ~9.
- **Fix:** Set status to "acquired" but `performance_unscaffolded: null` (untested). Spot-checks during maintenance and weekly reviews gradually verify over time.

#### Minor

**P-02** — Typed fluency metrics use oral benchmarks. Create separate typed-fluency scale (e.g., response latency).
**P-06** — Phase B is densest (11 concepts). Add duration expectations to progress reports and A→B transition messaging.
**P-08** — C-01 (subjunctive) lists only A-01/A-07 as prerequisites; should soft-reference B-04 (aspect).
**P-10** — Error trend computed with < 6 sessions of data is noise. Don't compute until 5+ sessions.
**P-13** — Recast salience techniques missing. Add: stress corrected element, rising intonation, partial recast.
**P-16** — Learner-reported vocabulary undercounts passive gains. Infer gains from comprehension quality.
**P-19** — Track interleaving quality: if concept only practiced as secondary 5+ times, elevate to primary.
**P-20** — Error rate recency: full confidence within 7 days, moderate 8-30, low 31-60.
**P-22** — Fossilization drilling can increase resistance. Add awareness-raising phase before intensive drilling.
**P-25** — Maintenance mode is passive post-graduation. Suggest calendar reminders in STUDENT-GUIDE.md.
**P-28** — Register shifting at Phase D is too late. Move tú/usted pragmatics to Phase B, deepen in C, master in D.
**P-29** — When motivation drops, diagnose which SDT need is underserved (autonomy, competence, relatedness).
**P-30** — Add "just-right streak" counter. 3+ consecutive "just-right" ratings = preserve current calibration.
**P-32** — Phase transitions don't assess writing. Add brief writing component to B→C and C→D assessments.
**P-33** — Pronunciation check-in in session 1 too brief. Extend to 4-5 min; make recurring 2-min warmup in sessions 2-5.

#### Suggestions

**P-03** — Add comprehension-check micro-step between noticing and controlled practice.
**P-34** — When receptive skills exceed productive skills by 1+ levels, assign more input homework.

---

### 3. Engineering

#### Critical

**E-03 | Session logs never validated against schema**
- File: `scripts/validate-state.py`
- Despite having `schemas/session-log.schema.yaml`, no function validates session log content. Only filename patterns are checked. CLAUDE.md step 12 says "verify well-formed" but the validator doesn't do this.
- **Fix:** Add `check_session_log()` that loads each session file, checks against schema, validates required fields and enum values.

#### Major

**E-01 | `load_yaml` defined twice with different behavior**
- Files: `scripts/shared.py:41`, `scripts/validate-state.py:17`
- `shared.py` version raises unhandled `FileNotFoundError` on missing files. `validate-state.py` defines a local version returning `None`. Callers of `shared.load_yaml` (including `generate-vault.py`) get crashes instead of graceful handling.
- **Fix:** Unify into single `load_yaml` in `shared.py` that handles missing files gracefully. Remove duplicate.

**E-02 | `shared.load_yaml` doesn't catch YAML parse errors**
- File: `scripts/shared.py:41-44`
- Malformed YAML propagates uncaught exception to all callers (generate-vault.py, etc.).
- **Fix:** Add `try/except yaml.YAMLError` block.

**E-04 | Resource-tracker required fields not validated**
- File: `scripts/validate-state.py`
- `check_resource_tracker` never calls `check_required_fields`. Top-level `schema_version` marked required in schema but not checked.
- **Fix:** Add `check_required_fields(data, "resource-tracker", "resource-tracker")`.

**E-05 | Acquired error threshold: 0.15 in validator vs 0.10 in spec**
- File: `scripts/validate-state.py:138`
- Validator uses > 0.15 as threshold. CLAUDE.md says < 10% (0.10). Gap allows concepts at 10-15% error to pass as acquired.
- **Fix:** Change threshold to > 0.10.

**E-10 | Schema missing `initial_placement`**
- Files: `schemas/learner-profile.schema.yaml`, `state/learner-profile.yaml`
- State file has 8-field `initial_placement` section entirely absent from schema.
- **Fix:** Add `initial_placement` map with children to schema.

**E-11 | Schema missing `placement_validation`, `topic_history`, `session_number`**
- Files: `schemas/schedule.schema.yaml`, `state/schedule.yaml`
- Three fields in state file not in schema. `placement_validation` drives validation logic.
- **Fix:** Add all three to schema.

**E-12 | Schema missing 3 map sections in system-health**
- Files: `schemas/system-health.schema.yaml`, `state/system-health.yaml`
- `placement_validation_metrics`, `goal_tracking`, `session_difficulty_tracking` not in schema.
- **Fix:** Add all three with children.

**E-15 | Test fixtures diverge from real schemas**
- File: `tests/conftest.py:113-129`
- Fixtures include fields not in schemas (`goals`) and use wrong field names. `MINIMAL_SYSTEM_HEALTH` has none of the 15 required fields from actual schema.
- **Fix:** Align fixtures with actual schema required fields.

**E-16 | ~50% of validator check functions have zero test coverage**
- File: `tests/test_validate_state.py`
- No tests for: `check_required_fields`, `check_learner_profile`, `check_schedule`, `check_system_health`, `check_curriculum_cross_refs`, `check_schedule_refs`, `check_carryover_concepts`, `check_integration_tested_with`, `check_session_filenames`, `check_placement_validation_consistency`.
- **Fix:** Add test cases for each, particularly cross-reference checks.

**E-20 | No atomicity protection for state writes**
- Files: all state files, all scripts
- Multiple files written sequentially. Interruption mid-write leaves inconsistent state.
- **Fix:** Write to temp file, then rename (atomic on POSIX). Or write manifest/checksum after all updates complete.

**E-25 | Migration only supports additive field additions**
- File: `scripts/migrate-state.py`
- Cannot rename fields, change types, restructure nested data, remove deprecated fields, or transform values. Any non-trivial evolution requires extending the framework.
- **Fix:** Extend migration entry format to support callable transforms alongside additive entries.

**E-31 | pytest not in dependencies**
- File: `requirements.txt`
- Only `pyyaml>=5.4`. Test suite requires pytest but it's not listed.
- **Fix:** Add `requirements-dev.txt` with `pytest>=7.0`.

**E-32 | Python version claim: 3.6+ but code requires 3.10+**
- File: `SETUP.md:5`
- Code uses `dict | None` (PEP 604), `list[tuple]` (PEP 585). Python 3.6-3.9 will `SyntaxError`.
- **Fix:** Change to Python 3.10+.

#### Minor

**E-06** — `results` list is module-level global mutable. Refactor to parameter or class.
**E-07** — `yaml_frontmatter()` doesn't handle nested dicts. Add guard or support.
**E-08** — `init-student.py` cultural_awareness iteration lacks `isinstance(entry, dict)` guard.
**E-09** — ID-to-title functions use fragile string-index parsing. Add format validation.
**E-13** — `decision_engine_trace` missing from session-log schema. (Duplicate of S-03.)
**E-14** — Skill-map schema uses different structure than other schemas (`grammar_entry_template` vs `fields`).
**E-17** — `test_generates_expected_file_count` depends on real skill-map on disk. Use synthetic fixture.
**E-18** — No integration test for migrate-state.py `main()`.
**E-21** — 60-day archival not implemented in any script. (Duplicate of S-17.)
**E-22** — `session_number` has no single source of truth across state files.
**E-23** — Vault rebuilds 70+ files per session. Fine for now, monitor if slow.
**E-24** — Frontmatter rewrite doesn't preserve field order. Creates unnecessary git diffs.
**E-26** — Migration header preservation breaks on blank lines between comments and YAML body.
**E-27** — Malformed schedule.yaml crashes vault generation (no YAML error handling).
**E-28** — Error recovery test script mutates live state files instead of temp copies.
**E-29** — Schedule cross-ref validation only checks `active_grammar.primary`, misses secondary/maintenance/vocabulary.
**E-30** — No cross-validation between resource-tracker and skill-map for receptive skill levels.

#### Suggestions

**E-19** — No test fixtures for session log data.

---

### 4. Structural Consistency

#### Major

**S-01 | system-design.md directory tree outdated**
- File: `docs/system-design.md`
- Missing: `schemas/` (6 files), `transcripts/`, `tests/`, `docs/session-log-example.yaml`, `docs/progress-report-template.md`, `curriculum/listening-progression.yaml`, `curriculum/reading-progression.yaml`.
- **Fix:** Add all to the documented tree.

**S-11 | Broken `[[Parking Lot]]` wiki-link in vault**
- File: `vault/Home.md:42`
- Links to `Parking Lot` (Title Case) but actual file is `parking-lot.md` (kebab-case) at project root.
- **Fix:** Change to `[[parking-lot|Parking Lot]]` or create alias.

**S-14 | Maintenance-mode learner returning: wrong protocol**
- File: `CLAUDE.md` routing, `curriculum/tutor-guides/maintenance-mode.md`
- Return session fires before maintenance mode for a 3+ day gap. Maintenance guide has its own extended-absence handling that differs from return guide. Maintenance learner gets generic protocol instead.
- **Fix:** Add maintenance check to return-session.md: if `autonomy_level` is `maintenance`, also load `maintenance-mode.md` regression section.

**S-17 | 60-day archival not implemented**
- Files: `CLAUDE.md:170`, scripts
- Delegated entirely to LLM agent during weekly review. No script support.
- **Fix:** Create `scripts/archive-sessions.py` or add `--archive` flag to existing script.

#### Minor

**S-04** — Session-log example missing `input_reviewed`, `interleaved_concepts`, `session_difficulty_rating`, assignment-level `retrieval_target`/`input_minutes`.
**S-05** — Skill-map schema missing `schema_version` field (present in state file and all other schemas).
**S-06** — A-08 and A-09 not shown in system-design.md directory tree.
**S-07** — Conditional load table in system-design.md doesn't include `input-orchestration.md` or `session-variety.md`.
**S-09** — Two `preempt_at` values in l1-interference.yaml are not valid concept IDs (`vocabulary-introduction`, `tier2-weather-seasons`).
**S-12** — `vault/Progress/` files not generated by generate-vault.py. Must be manually created.
**S-13** — Daily Note template uses Templater `{{date}}` syntax but Templater listed as optional.
**S-16** — Partial session + 3-day gap: unclear which takes priority.
**S-18** — Pronunciation entries not cross-referenced in validate-state.py.
**S-20** — STUDENT-GUIDE.md says journaling starts "around Phase B" but actual trigger is a schedule.yaml flag.
**S-22** — `vault/Progress/` files not created by init-student.py or generate-vault.py.

#### Suggestions

**S-19** — 3 most recent session logs may lose long-term patterns. Consider 5 logs or checking system-health carryover counts.
**S-21** — Obsidian vault exposes system directories to learner. Add `.obsidianignore` for `state/`, `scripts/`, `schemas/`, etc.
**S-24** — `pronunciation-practice.md` exists in `curriculum/activities/` but not in system-design.md tree.

---

## Positive Findings (Preserve These)

These design choices are genuinely excellent and should not be changed:

1. **Scaffolded/unscaffolded performance distinction** — reflects real SLA insight about monitored vs spontaneous performance
2. **Error classification system** — developmental, L1 interference, fossilized, slip — correct taxonomy with appropriate treatment per type
3. **Carryover escalation ladder** — changes approach at each stage, not just intensity
4. **Concurrent concept gate** (max 3 practicing) — prevents spreading attention too thin
5. **Pre-instruction recast pattern** — models correct forms before formal instruction
6. **Learner self-assessment override** — "defer to the learner" guardrail is rare and pedagogically wise
7. **Interaction Hypothesis implementation** — conversation practice, role-play, and repair phrases create genuine negotiation-of-meaning
8. **Schema-driven design** — `load_schema` + `get_required_fields` pattern is clean and extensible
9. **Vault file protection** — `generated: true` frontmatter guard prevents overwriting hand-edited notes
10. **Cross-reference integrity** — 70+ skill-map IDs all resolve to existing curriculum files (100% clean)
11. **Interleaving system** — embedding prior concepts into primary practice matches current research
12. **Reading progression** — well-calibrated R1-R5, clean CEFR mapping, good level-up criteria
13. **Error recovery testing** — mutation-testing approach in `test-error-recovery.py`
14. **Migration dry-run support** — `--dry-run` flag essential for state-critical system
