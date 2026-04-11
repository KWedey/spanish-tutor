# Spanish Fluency Tutor — Comprehensive Audit Report

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

## Priority-Ordered Implementation Plan

### Tier 1 — Fix Before First Session (Critical + Blocking Major)

1. **Remove injected skill routing section from CLAUDE.md** (A-22) — lines 205-224 are gstack tooling, not tutoring
2. **Resolve Phase B+/C+ fluency contradiction** (A-28/S-02) — system-design.md says C+, everything else says B+
3. **Fix fluency day routing to also load decision engine** (A-08) — routing table prevents decision engine loading on fluency days, contradicting guardrail
4. **Add onboarding + return session handling** (A-07) — learner returning mid-onboarding gets no regression check
5. **Clarify weekly review day and fluency day routing conditions** (A-01, A-02) — agent cannot determine these without undocumented lookups
6. **Fix acquired error threshold: 0.15 → 0.10** (E-05) — validator allows concepts to be "acquired" at 15% error rate when spec says 10%
7. **Add `micro` session status to schema or replace with duration check** (A-21) — CLAUDE.md references undefined status value
8. **Unify `load_yaml` and add error handling** (E-01, E-02) — duplicate definitions, no YAML error handling in shared version
9. **Add session log validation to validate-state.py** (E-03) — session logs are never validated against schema

### Tier 2 — Fix Before Session 10 (Major, Affects Onboarding/Early Sessions)

10. **Create post-session automation script** (A-11) — reduce 15-step manual protocol to ~7 steps by automating vault gen, validation, archival, commit
11. **Add `current_onboarding_session` to schedule.yaml** (A-09) — agent cannot reliably determine which onboarding session to load
12. **Split CLAUDE.md Step 4 into pre-session and runtime triggers** (A-04) — real-world debrief is runtime, not startup
13. **Move Step 1b (partial session check) after Step 3 (routing)** (A-05) — continuity check runs before session type is determined
14. **Add missing L1 interference patterns** (P-21) — personal-a, reflexive omission, ser-in-progressive, question word order
15. **Align schemas with actual state files** (E-10, E-11, E-12) — learner-profile missing `initial_placement`, schedule missing `placement_validation` and `topic_history`, system-health missing 3 map sections
16. **Add `decision_engine_trace` to session-log schema** (E-13/S-03)
17. **Fix test fixtures to match real schemas** (E-15) — test data diverges from production structure
18. **Add tests for untested validator functions** (E-16) — ~50% of check functions have zero coverage
19. **Correct Python version requirement: 3.6+ → 3.10+** (E-32) — code uses PEP 604/585 syntax
20. **Add pytest to dev dependencies** (E-31)

### Tier 3 — Fix Before Session 30 (Major, Affects Post-Onboarding Quality)

21. **Increase comprehensible input in Phase A** (P-01) — input is "supplementary" when SLA research says it should be primary
22. **Address ser/estar delayed introduction risk** (P-05) — 3 sessions of unguided production before instruction, high fossilization risk
23. **Increase error rate sample size for acquisition decisions** (P-09) — rates based on as few as 3-5 observations
24. **Fix max-3-correction rule to differentiate recasts vs explicit** (P-12) — unlimited recasts are fine; 3 explicit corrections is the real cap
25. **Reduce L2 listening minimum hours: 20 → 10-15** (P-15) — current minimum is ~27 weeks at L2
26. **Weight DECAY scoring by concept durability** (P-18) — well-practiced concepts get same decay as fragile ones
27. **Raise cultural competence priority for politeness/register** (P-27) — NEED cap of 5 makes cultural concepts nearly invisible
28. **Move register shifting introduction from Phase D to Phase B** (P-28) — tú/usted pragmatics needed from first real-world interaction
29. **Shift Phase A language ratio from 80/20 to 60/40 English/Spanish** (P-24)
30. **Fix placement pre-population: set `performance_unscaffolded` to null, not "competent"** (P-31)
31. **Add maintenance-mode check to return session guide** (S-14)
32. **Clarify error correction override scope** (A-29) — activity table vs conversation practice phase
33. **Update system-design.md directory tree and conditional load table** (S-01, S-07)
34. **Add atomic write protection for state files** (E-20)
35. **Implement 60-day session log archival script** (E-21/S-17)

### Tier 4 — Improve Over Time (Minor + Suggestions)

Items 36-93 listed in the detailed findings below.

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
