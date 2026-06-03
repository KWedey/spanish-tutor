# Pre-First-Session Audit — 2026-06-03

> **⚠️ Read the Quality-Review Addendum at the bottom first.** A second adversarial pass
> recalibrated several severities below, dropped one false positive, and added a new tier of
> findings (dead pedagogy counters, security/leak gaps, router crashes, no CI) that the first
> 7 auditors missed. The Addendum is the authoritative priority list.

**Scope:** Full system audit before the first real tutoring session (the v1.1 canary).
**Method:** 7 parallel specialist auditors (CLAUDE.md execution integrity, Python scripts, curriculum content, seed-state/first-session readiness, tutor-guides cross-consistency, schema↔usage↔vault, and a cold end-to-end first-session dry-run), followed by direct verification of every CRITICAL/HIGH claim.

**Baseline (all green, none of the below is caught by it):**
- `pytest` — 535 passed / 0 failed
- `validate-state.py` — 33 passed / 0 warnings / 0 failures
- `route_session.py state/` → `first-session` (correct)

**Headline:** The very first session (routing → `first-session`) will run and pass its infra checks. **The system cannot correctly reach a working session 2.** Every defect clusters at the *seams* — where the natural-language contract in `CLAUDE.md` has drifted from the scripts/schemas that were fixed in later phases — and on *never-exercised paths* (session 2+, failure/rollback, `--full` regeneration). Green tests mask all of it.

Severity key: **CRITICAL** = breaks correct progression or corrupts state · **HIGH** = wrong behavior, surfaces early · **MEDIUM** = inconsistency/ambiguity · **LOW** = polish/by-design. ✅ = verified directly this session. ⊕N = independently flagged by N auditors.

---

## CRITICAL — fix before session 2 (session 1 will *look* fine and hide these)

### C1 ✅ `current_onboarding_session` is never incremented → onboarding stalls forever
- **Where:** `CLAUDE.md:63` reads `NN = current_onboarding_session` to load the onboarding session; `onboarding-guide.md:119` says it "does not advance until the planned concept is delivered" (implying it *should* advance after) — but **no step in CLAUDE.md State Updates (0-19) or the onboarding guide ever increments it.** Intent is recorded only in `docs/audit-report.md:349` ("Increment at end of each onboarding session"), never wired in. (A prior audit already flagged the unbounded counter: `.omc/audit/wave-c-routing-truth-table.md` L-1.)
- **Effect:** With `current_onboarding_session: 1` fixed forever, sessions 2,3,4… all re-serve `session-01`. No error — it silently re-teaches the same session and poisons practice-counts/decision-engine baselines. **Most likely thing to silently corrupt state.**
- **Fix:** Add an explicit State-Updates step: "If `session_type` is onboarding and the planned concept was delivered, increment `current_onboarding_session` in `schedule.yaml`." Mirror in `onboarding-guide.md`. Optionally add `validate-state.py check_onboarding_counter_range` (FAIL if `<1` or `>10` while `onboarding_complete=false`).

### C2 ✅ Onboarding filename pattern doesn't match the files on disk
- **Where:** `CLAUDE.md:63` loads `curriculum/onboarding/session-NN.md`. Actual files are `session-01-discovery.md` … `session-10-consolidation-final.md`. `session-01.md` does not exist.
- **Effect:** A literal file read on session 2 fails; resolution requires the tutor to *guess* a glob. Non-deterministic at exactly the wrong moment.
- **Fix:** Change CLAUDE.md (and the onboarding guide's `session-NN.md` shorthand) to `session-NN-*.md` (NN zero-padded, one match per number), and state the convention once.

### C-design ⊕2 Off-by-one ambiguity: does session 1 = discovery only, or discovery + onboarding-01?
- **Where:** Routing row 1 (no logs) loads only `first-session.md`; `session-01-discovery.md` *also* contains the discovery protocol AND A-00 repair phrases. The numbering model is never stated.
- **Effect:** Depending on interpretation, A-00 repair phrases (the highest-priority concept through session 5 per a CLAUDE.md guardrail) get double-covered or skipped. Resolving C1's increment requires deciding this first.
- **Fix:** Decide and document the model, then set the initial `current_onboarding_session` and the increment point to match.

---

## HIGH — wrong behavior, surfaces in the first weeks

### H1 ✅ ⊕2 Carryover escalation state written to the wrong file
- `CLAUDE.md:157` (State Updates §5) tells the tutor to write `sessions_in_carryover` and `escalation_stage` into `resource-tracker.yaml`. The decision engine **reads** them from `schedule.yaml > carryover_concepts` (`decision-engine.md:7,33`), and the resource-tracker schema has **no such fields**. Escalation state is written where it's never read → the carryover/regression escalation ladder silently never fires.
- **Fix:** In CLAUDE.md §5, move `sessions_in_carryover`/`escalation_stage` to the `schedule.yaml > carryover_concepts` update (§4); keep only `hours_logged`/`sessions_completed`/`comprehension_trend`/`learner_engagement` in resource-tracker.

### H2 ✅ ⊕2 `fluency_days_per_week` is a dangling field
- `CLAUDE.md:51` counts fluency days "vs `fluency_days_per_week` target from `schedule.yaml`." No such field exists (schedule has only `fluency_days_this_week` + `last_fluency_day`). `route_session.py` was already fixed (audit C-1/C-2) to derive a per-phase target internally; CLAUDE.md was never updated to match.
- **Fix:** Reword CLAUDE.md L51 to "count `fluency_days_this_week` vs the phase target (B=1, C=2, D=3)," or add `route_session.py state/` as the authoritative fluency-day decision.

### H3 Phase D "every session" fluency contradicts the weekly cap + non-consecutive routing
- `fluency-activities.md:17` / `decision-engine.md:201` promise fluency *every* Phase-D session; `route_session.py` caps Phase D at 3/week and forbids back-to-back days. Both cannot be right.
- **Fix:** Decide intended behavior — either drop the cap/non-consecutive guard for Phase D, or reword the guides so fluency is an *embedded component* of every Phase-D standard session (not a separately-routed type) and reconcile both sides.

### H4 ✅ `generate-vault.py --full` destroys appended Weekly Reports & Milestones
- `run_full()` writes `generate_weekly_reports()` and `generate_milestones()` with `force=True` (`generate-vault.py:855-858`), and both emit placeholder bodies carrying `generated: true`. CLAUDE.md steps 12b/12c tell the tutor to *append* real history into those same files. The next `--full` (which Getting Started tells the learner to run) wipes all accumulated history back to the placeholder.
- **Fix:** Make these two files append-safe — drop `generated: true` from their frontmatter (treat as hand-edited), or have `run_full` write them with `force=False` when non-placeholder content exists.

### H5 `post-session.sh` promises rollback it never performs, and mutates before validating
- The header/comments promise snapshot-rollback, but there is **no `snapshot-state.py rollback` call** anywhere. Worse, ordering is generate-vault (Step 1) → archive-sessions (Step 2) → **then** validate (Step 3). With `set -e`, a validation/protocol failure exits leaving the vault regenerated and logs already moved to `archive/`, with no automatic restore.
- **Fix:** Add an `ERR` trap that runs `snapshot-state.py rollback` (when not `--dry-run`), **and/or** reorder so validation + session-log checks run before the irreversible vault/archive steps.

### H6 ✅ Canary doc uses the wrong `check-session-log.py` invocation
- `docs/canary-first-session.md:132,213` call `check-session-log.py state/sessions/$(date).yaml`. The script takes a **date**, not a path, and builds the path itself → it looks for `state/sessions/state/sessions/<date>.yaml.yaml` → false FAIL on the operator's own verification step. (`first-session-dryrun.md` and `post-session.sh` use the correct date form.)
- **Fix:** `python3 scripts/check-session-log.py $(date -u +%Y-%m-%d)`.

### H7 ✅ `generate-vault.py --session` does not create the daily note the canary asserts
- Canary Post-session step 3 expects `vault/Daily/<today>.md` after `--session`. The script never writes daily notes (CLAUDE.md step 12a says the tutor writes them manually). The canary's expectation is wrong and a tutor relying on the script will silently never produce a daily note.
- **Fix:** Correct the canary doc to mark the daily note a manual write, **or** extend `--session` to emit the daily-note stub with `generated: true`.

### H8 ✅ Three L1-interference IDs referenced by grammar files are missing from `l1-interference.yaml`
- `A-08` references `tener-for-age` (yaml has it as `age-with-ser`); `D-02` references `conditional-in-si-clause` (absent); `D-04` references `passive-overuse` (absent). CLAUDE.md guardrail "Always check `l1-interference.yaml` when introducing a new concept" then finds nothing for these three.
- **Fix:** Reconcile the A-08 id, and add the two missing entries (content can be lifted from the grammar files).

### H9 First-session log shape is unspecified → may abort post-session
- `check-session-log.py` requires `session_type: "first-session"` + a populated `assessment` block + `learner_observations.mood/engagement`. `first-session.md` never tells the tutor to emit these, and the only example log is `session_type: standard` with no `assessment`. A wrong/missing field trips `post-session.sh` Step 5 → `exit 1` mid-run.
- **Fix:** Add a first-session-log skeleton (in `first-session.md` or `docs/first-session-log-example.yaml`) showing `session_type: first-session`, `session_number: 1`, and the `assessment` block.

### H10 ✅ `validate-state.py check_daily_target_tier_drift` is written as an unrunnable command
- `CLAUDE.md:123` tells the tutor to "run `scripts/validate-state.py check_daily_target_tier_drift`." The script takes no positional args; that literal command errors. The check runs *internally* via plain `validate-state.py`.
- **Fix:** Reword to "`validate-state.py` runs the `check_daily_target_tier_drift` check internally and FAILs if the tiered reduction is ignored."

---

## MEDIUM — inconsistencies & validation gaps

- **M1** `curriculum/cultural/register-shifting.md` is an **orphan** — `CLAUDE.md:82` lists only 4 of 5 cultural files, but `register_shifting` is a real, *functional* (uncapped-NEED) cultural concept that can be selected. Add `register-shifting @ Phase B` to the load list.
- **M2** `decision-engine.md:214-231` (Step 5b) selects "concepts at **Stage 3+**," but "Stage" is an ephemeral error-rate-derived in-session artifact, **not a persisted skill-map field** — a fresh agent can't query it. Restate in terms of fields that exist (status/`performance_unscaffolded`), or persist `last_activity_stage`.
- **M3** `check-session-log.py:285` — `int(estimated_minutes)` (and budget fields L320-322) raise an uncaught `ValueError` on non-numeric tutor input (e.g. `"15 min"`), surfacing as a misleading commit-blocking "missing fields" error. Wrap coercion in try/except.
- **M4** `post-session.sh` Steps 5b/5c rewrite skill-map.yaml & schedule.yaml via `yaml.safe_dump`, **silently dropping the comment headers** that `init-student.py`/`migrate-state.py` wrote (and which `migrate-state.py` deliberately preserves). Preserve headers; use `shared.atomic_write`.
- **M5** ✅ `load_adjustments` (CLAUDE.md tells the tutor to write it to system-health) is absent from `system-health.schema.yaml` and seed state — created only at runtime by `check-session-log.py`. Add it to the schema so the contract is discoverable/enforceable.
- **M6** `carryover_concepts` is a bare untyped list in `schedule.schema.yaml`; the per-item fields the engine reads (`is_prerequisite`, `sessions_in_carryover`, `escalation_stage`, `current_approach`) live only as comments in `system-design.md` → unvalidated. Define the item shape in the schema.
- **M7** Onboarding Spanish errors: `session-08-gustar-type.md` has ~12 missing-accent errors on the exact words being taught ("el cafe"×6 → café, "musica" → música, "A mi me" → A mí me, "A el le" → A él le, "ningun" → ningún); `session-03:41` "el dia" → "el día". The parallel grammar file A-06 spells all of these correctly. Fix the onboarding files.
- **M8** ✅ `system-design.md:753` session_type comment lists 5 of the 13 schema enum values. Update or point to the schema as source of truth.
- **M9** `docs/session-log-example.yaml` (the template tutors copy) omits `INTEREST` from `decision_engine_trace` (docs say "always"), omits the conditionally-**required** `homework_load_rating` (a copy would FAIL `check-session-log.py`), and uses `next_session.session_type: normal` — **not a valid enum value** (should be `standard`). Fix the example.
- **M10** `validate-state.py` enum validation only walks **top-level** scalars — nested enums (`recasts[].uptake`, `recasts[].activity_stage`, `assignments[].dialect_advisory`) are unenforced (`uptake: yes` passes). Extend the validator to descend into item schemas.
- **M11** `input_reviewed` has no item schema; the example uses `comprehension_assessment` while `receptive_skills` uses `comprehension_quality` — these feed each other (CLAUDE.md step 3) and will drift. Add an item shape and align the field name.
- **M12** `maintenance-mode.md:56,79` writes summaries **monthly**; `CLAUDE.md:162` step 10 says write a summary on **every** weekly_review_day. Add a maintenance carve-out to step 10.
- **M13** ✅ `route_session.py:233` reads `autonomy_level` from `learner-profile` (the `profile` dict), but the field lives in `schedule.yaml` per schema. A maintenance learner misroutes to `standard`. (Dormant until a maintenance learner exists, but a real bug.) Read `schedule.get("autonomy_level")`; add a regression test.
- **M14** `vault/Progress/Assessment Methodology.md` carries `generated: true` but **no generator function produces it** → stale and never refreshed, yet flagged auto-maintained. Add a generator or drop the flag.

---

## LOW — polish / naming / by-design

- Cultural concept names: CLAUDE.md uses hyphens (`politeness-formulas`) vs skill-map underscores (`politeness_formulas`); `register_shifting` (cultural) collides with grammar `D-05-register-shifting`. Align keys; disambiguate.
- `input-orchestration.md:139` cryptic "07-01" reference → replace with `media-bank.yaml > prescriptive_episodes.reading`.
- Three uncoordinated escalation ladders (L1-interference 3/5, error-correction 3/5/8, decision-engine regression 1-5) with no stated precedence — add a cross-link naming error-correction as canonical.
- `decision-engine.md:201` fluency-frequency list omits "Phase A: none."
- Vault: `[[Register Shifting]]` wiki-link is ambiguous (Grammar + Cultural notes share the title).
- `prescriptive_episodes` use scalar `level:` while `input-orchestration.md` says `level_range` — clarify or align.
- A-00 communication-repair omits the L1-Interference & Dialect-Notes sections every other grammar file has (defensible — add a one-line N/A note like C-02/C-03).
- `route_session.py` docstring still lists `fluency_days_per_week` (never read); `system-design.md` assignments block omits `dialect_advisory`; `assignments.item_schema` documented but not loader-enforced (deferred to v1.2).
- `post-session.sh:197-217` null `session_number` coerces to `"None"` and skips the transcript gate — coerce `data.get('session_number') or 1`.
- Uncommitted in-flight fix `01-present-subjunctive.md` (prerequisite-ID drift A-07 rename) — commit it; consider a structural test that every `[A-D]-NN-name` cross-reference resolves to a real file.

### Accepted / by-design (no action)
- `validate-state.py` doesn't enforce populated identity fields pre-first-session — intentional template tolerance; first session populates the profile.
- Gitignored state means `post-session.sh` commit is a no-op — expected on the shared setup (CLAUDE.md step 19 already says skip).

---

## Recommended fix order

1. **Unblock session 2** (C1, C2, C-design) — the program literally cannot progress without these.
2. **Reconnect CLAUDE.md to reality** (H1, H2, H10, M5, M12, M13) — the contract-vs-scripts drift class.
3. **Harden the post-session failure path** (H5, M3, M4) — the only place that can corrupt state.
4. **Fix the canary protocol doc** (H6, H7, H9) — so the operator's own verification doesn't false-fail.
5. **Vault history protection** (H4, M14).
6. **Content correctness** (H8, M7) and **schema/example tightening** (M8-M11, M6).
7. **LOW polish** as a final sweep.

Root cause to internalize: later phases fixed the *scripts and schemas*; `CLAUDE.md` and the *guides/example/canary docs* were not always updated in lockstep. The fix work is mostly re-aligning the natural-language contract with the code that already exists.

---
---

# Quality-Review Addendum — 2026-06-03 (adversarial second pass)

Three independent reviewers pressure-tested the findings above: a **critic** (re-verified every CRITICAL/HIGH, calibrated severity, stress-tested fixes), a **blind-spot hunter** (security/leak, pre-commit hook, user docs, journal/feedback/transcript mechanics, migrate-state), and a **reconciler** (checked the new audit against the prior `docs/audit-report.md`, the v1.1 milestone audit, and the recent in-progress `.omc/audit/` wave). All new severe claims re-verified directly. Severity key unchanged. ✅ = verified this pass.

## Part 1 — Corrections to the findings above

- **DROP (false positive):** M9's sub-claim that `next_session.session_type: normal` is an invalid enum. ✅ `next_session.session_type` is a free-text `string` field (distinct from the top-level `session_type` enum) and "normal" is literally listed in its schema description (`session-log.schema.yaml:295-299`). The *other* M9 sub-claims stand (missing `INTEREST`, missing conditionally-required `homework_load_rating`, `session_number: 14`/`session_type: standard` not a usable first-session template).
- **MERGE:** C-design folds into **C1** — same root cause. ✅ The numbering model *is* determinable: `session-01-discovery.md:7` shows session 1 = discovery + session-01 (A-00), so `current_onboarding_session: 1` is the correct seed; the only defect is that nothing increments it. The fix (add the increment) does **not** conflict with the A-00 "highest-priority through session 5" guardrail — session-02 re-drills A-00, so a working counter *serves* the guardrail.
- **C1 fix constraint:** must ADD an increment step (to CLAUDE.md State Updates **and** onboarding-guide "Each Onboarding Session") **without** deleting `onboarding-guide.md:119`'s "same `current_onboarding_session`" phrase, which is pinned by `tests/test_onboarding_guide_doc.py:43-44`.
- **DOWNGRADE C2 → HIGH:** ✅ produces a *loud* file-not-found that an LLM tutor reflexively self-heals by listing the dir. Real, cheap to fix, but not the silent stall C1 is.
- **DOWNGRADE H3 → MEDIUM:** Phase D is the terminal phase, years away on a 0-session system; doc-only reconciliation, no state risk.
- **DOWNGRADE H5 → MEDIUM:** ✅ overstated. A Step 0 snapshot *is* taken and `snapshot-state.py rollback` *works* (`snapshot-state.py:158`); what's missing is an automatic ERR-trap and correct ordering (vault/archive run before validate). Recoverable via one manual command. *(But see QR-S3 — the rollback has its own data-loss bug.)*
- **DOWNGRADE H10 → LOW:** loud argparse error, obvious self-heal (re-run plain `validate-state.py`).
- **Fix change H4:** prefer **dropping `generated: true`** from Weekly Reports & Milestones frontmatter (lets the existing marker-guard protect them) over the fragile `force=False`-content-sniff option.
- **Fix sequencing H1:** ✅ pair with **M6** — moving carryover fields to `schedule.yaml` is inert for validation until the `carryover_concepts` item shape is defined (currently a bare `type: list` at `schedule.schema.yaml:204`).

## Part 2 — NEW findings the first 7 auditors missed

### NEW CRITICAL — inert pedagogy (the calibration loops don't actually run)

- **QR-P1 ✅ Dead system-health counters — calibration logic is theatrical** | `schemas/system-health.schema.yaml:13,85` (+ others) | `concepts_requiring_reteach_total`, `sessions_rated_too_easy_30d` (and siblings) are `required: true`, seeded to 0, and have **zero writers anywhere in `scripts/`** (verified by grep). The CLAUDE.md calibration promises ("two consecutive too-easy → increase challenge", reteach tracking) read counters that never move. | Add a `recompute-system-health.py` invoked by `post-session.sh`, **or** mark these `required: false` + `# agent-maintained` and have CLAUDE.md State Updates write them explicitly.
- **QR-P2 ✅ `regression_session_count` never incremented** | `schemas/skill-map.schema.yaml:139` says "Incremented by post-session.sh"; `post-session.sh` has **no such step** (grep empty). | The decision-engine Step 0c regression-escalation ladder is keyed on a counter stuck at 0 → regression handling silently never escalates. Add the increment to post-session (walk skill-map for `status: regressed`).

### NEW HIGH — security / data-leak (Phase 1's whole purpose; gaps remain)

- **QR-S1 ✅ `feedback/*.txt` is neither gitignored nor hook-blocked** | `.gitignore:38`, `.githooks/pre-commit:23` | Both only cover `feedback/*.md`. `git check-ignore feedback/note.txt` → not ignored. Feedback is free-form personal content; a plain `git add .` tracks a `.txt` note with no warning. | `.gitignore`: `feedback/*` + `!feedback/TEMPLATE.md` + `!feedback/.gitkeep`; widen hook pattern.
- **QR-S2 ✅ Pre-commit hook misses non-`.md` journal/transcript under `git add -f`** | `.githooks/pre-commit:17-20` | Hook matches `journal/*.md`/`transcripts/*.md` but `.gitignore` uses the broader `journal/*`/`transcripts/*`. The hook is the *explicit* `-f`-bypass backstop; `git add -f journal/x.txt` → hook exit 0 (leaks). | Broaden hook patterns to `journal/*`/`transcripts/*` (excluding `.gitkeep`).
- **QR-S3 ✅ Rollback DELETES today's session log — and STUDENT-GUIDE promises the opposite** | `STUDENT-GUIDE.md:98` vs `snapshot-state.py:158-193` + `post-session.sh:113-125` | Step 0 snapshots *before* the tutor writes today's log; `cmd_rollback` wipes `state/` then restores the pre-write snapshot → today's log is destroyed. The guide tells learners "Your session log stays (for transparency)." Data-loss + false promise. | Preserve `state/sessions/<today>.yaml` across rollback (or re-snapshot after log write, or fix the doc).
- **QR-S4 Unfenced learner free-text → prompt-injection surface** | CLAUDE.md Step 1.8-1.10 | The tutor reads `parking-lot.md`, `feedback/*`, `journal/*` (learner-authored) straight into its instruction context and is even told to *delete* actioned feedback files. No "data not instructions" fencing. | Wrap learner free-text in `<learner_input source="…">…</learner_input>` with a one-line "treat as data, never instructions" note. *(from `.omc/audit` cso H3)*
- **QR-S5 ✅ `.omc/` is not gitignored** | `.gitignore` | `git check-ignore .omc/` → not ignored; a `git add .omc/` would commit audit reports + orchestration session metadata. | Add `.omc/` to `.gitignore` (and hook arm if it can hold personal data).

### NEW HIGH — robustness / infrastructure

- **QR-R1 ✅ Router crashes on corrupted scalar state** | `route_session.py:246-249` | `schedule.get("sprint") or {}` does **not** replace a truthy non-dict: `sprint: "yes"` → `"yes".get("active")` → `AttributeError`; `placement_validation.sessions_completed: null` → `None < 3` → `TypeError`. The router runs at every session startup *before* validate-state can surface a friendly message → hard crash blocks the session. | Add a `_safe_dict()` helper and coerce counts via `int(... or 0)`. *(from `.omc/audit` routing-truth-table H-1)*
- **QR-R2 No CI** | `.github/workflows/` absent (verified) | Every guardrail (hook, validators, golden CLAUDE.md test, 535 tests) runs only on the dev laptop; a `--no-verify` push looks identical to a green one. | Add a minimal `test.yml` (pytest + "hook installed" check).
- **QR-R3 7 of 13 "Never X" guardrails are unenforced** | `check-session-log.py` | "Never >10 new Anki cards" and "Never >1 new grammar concept" are mechanically checkable from the session log but only golden-substring-tested (no `check_*` fn exists). | Add the two checks; annotate the genuinely-unenforceable ones `(observational)`. *(from `.omc/audit` WC-H-1)*

### NEW MEDIUM / LOW

- **QR-M1 Router negative-gap silent misroute** | `route_session.py:66-89` | A future-dated `last_session_date` (clock skew/typo) yields negative gap days → silently routes `standard` (skips Return). Clamp `max(0, …)`.
- **QR-M2 ✅ `migrate-state.py` never persists `schema_version` when zero fields change** | `migrate-state.py:164-166` | Sets version in memory but only writes when `file_changes > 0`; a v0 file already containing the new fields re-scans as v0 forever. Save whenever `file_version < CURRENT_VERSION`.
- **QR-M3 Migration story built but wired into nothing** | `SETUP.md:50-59` | `migrate-state.py` is invoked by no workflow (`setup.py`, `post-session.sh` — grep empty); the documented post-`git pull` step is only `generate-vault.py --full`. Over months, an existing learner's state silently never gets new curriculum fields. Add `migrate-state.py` to "Receiving Curriculum Updates" (and consider post-session Step 0).
- **QR-M4 `migrate-state.py` save bypasses `shared.atomic_write`** | `migrate-state.py:83-108` | Non-atomic `write_text` (crash mid-write truncates state, and migrate runs *outside* post-session's snapshot) + re-dumps/normalizes the whole YAML. Use `shared.atomic_write`.
- **QR-L1 ✅ `.planning/` files are tracked** despite gitignore + the global "never commit `.planning/`" rule | `git ls-files .planning/` → 8 SUMMARY files | gitignore only affects untracked files. `git rm --cached -r .planning/`.
- **QR-L2 ✅ Dead `vault/**/*.md` hook line** | `.githooks/pre-commit:42-43` | POSIX `case` `**` isn't recursive; `vault/*.md` (L42) already matches all depths. Harmless but misleading. Collapse + comment.
- **QR-L3 `route_session._load_yaml` swallows all exceptions** | `route_session.py:62` | `except Exception: return {}` — a `PermissionError` silently disables weekly review forever. Narrow to `(OSError, yaml.YAMLError)`.
- **QR-L4 Stale traceability/progress tables** | `.planning/REQUIREMENTS.md:191-199`, `.planning/ROADMAP.md:216-217` | ROUTE-01..07/CURR-01..02 shown "Pending" and Phase 6/7 shown in-progress though all checkboxes are `[x]`, code is on disk, STATE.md says 100%. Refresh the tables.
- **QR-L5 Wave-B H-3 dialect lookup never fixed** | dialect advisory only searches `prescriptive_episodes`, not podcasts/tv/audiobooks | advisory under-fires on a minority of real assignments. (Partial-propagation residue.)

## Part 3 — Meta-finding (the most important takeaway)

The recent **`.omc/audit/` wave (2026-05-14) was the most thorough prior pass — 2 CRITICALs + ~10 HIGHs — and only ~7 of its findings ever got followup commits.** Its open list (dead counters, crashable router, no CI, prompt-injection, `.omc` leak) was never reconciled into STATE.md or this audit's first pass. The dominant anti-pattern across all four audit lanes is **"defined + unit-tested in isolation ≠ wired in"**: a requirement reads "done" at the file level while its runtime effect is null. STATE.md's "100% complete, ready for canary" is **directionally honest but overstated at the seams** — the 535 tests genuinely pass and headline fixes are real, but "done" here means "the function/schema/test exists," not "the behavior works end-to-end on real state." Treat `.omc/audit/wave-d-learnings.md`'s open-debt table as authoritative and reconcile it before shipping.

## Part 4 — Final consolidated priority

**MUST-FIX before the first real session (first-run correctness + data safety):**
1. **C1** (onboarding never advances — *the* blocker) + decide/encode the numbering model.
2. **QR-S3** (rollback deletes the session log — data loss on the exact recovery path the canary leans on).
3. **QR-R1** (router crash on bad scalar — hard-blocks session startup).
4. **H9 / H6 / H7** (first-session log template; canary doc's own verification commands false-fail).
5. **QR-S1 / QR-S2 / QR-S5 / QR-L1** (close the leak boundary — cheap, and the whole point of Phase 1).
6. **H4** (vault history wipe — cheap, prevents silent data loss).

**FIX SOON (wrong behavior within weeks, but not session-1/2 blocking):**
- QR-P1, QR-P2 (inert calibration/regression — the pedagogy is partly fake until wired).
- H1 (+M6), H2, C2, QR-R2, QR-R3, QR-M2/M3/M4, M3, M4, M5, M13, H8(A-08).
- Content: M7 (onboarding accents), H8 (D-phase L1 entries).

**POLISH / by-design:** H3, H5(ordering+ERR-trap), H10, M1/M2/M8–M12/M14, QR-M1, QR-L2–L5, and the LOW/accepted set in the main report.

**Root cause to internalize:** later phases fixed *code*; the *prose* (CLAUDE.md, guides, example log, canary doc, STUDENT-GUIDE) and the *runtime wiring* (counters, increments, migration) didn't always follow. Most of the work is re-aligning the contract and finishing the wiring for code that already exists.

---
---

# Resolution Log — 2026-06-03 (all gaps closed)

Fixed on branch `audit-fixes-2026-06-03` (14 commits). Final state: **565 tests pass**
(was 535; +30), **validate-state 34/34** (was 33; +1 guard), router → `first-session`,
golden CLAUDE.md test green, working tree clean.

| Commit | Findings closed |
|--------|-----------------|
| `fix(onboarding)` | C1, C2, C-design — onboarding progression wired (counter increment + glob + numbering model + range validator) |
| `fix(drift)` | H1, H2, H10, M5, M6, M12, M13 — CLAUDE.md/schema/router realigned with code |
| `fix(leak)` | QR-S1, QR-S2, QR-S5, QR-L1, QR-L2 — hook/.gitignore broadened, .omc ignored, .planning untracked, deletions allowed |
| `fix(router)` | QR-R1, QR-M1, QR-L3 — crash-proofing, gap clamp, narrowed except |
| `fix(post-session)` | H5, QR-S3, M3, M4 — auto-rollback trap, session-log preservation, int coercion, header/atomic writes |
| `fix(canary)` | H6, H7, H9 + restore→rollback doc bug — first-run protocol corrected, first-session log template added |
| `fix(vault)` | H4, M14 — append-targets protected from --full, orphan flag fixed |
| `fix(pedagogy)` | QR-P1, QR-P2 — dead calibration counters wired (recompute-metrics.py + post-session Step 5d) |
| `fix(content)` | M7, H8 — onboarding accents, 3 L1-interference ids reconciled |
| `chore(ci)` | QR-R2 — GitHub Actions running pytest + validate-state |
| `fix(migrate)` | QR-M2, QR-M3, QR-M4 — version-stamp persist, atomic write, wired into SETUP |
| `fix(schema-docs)` | M1, M2, M8, M9, M10, M11, H3 + polish — schema/example/guide tightening, nested-enum validation |
| `fix(polish)` | QR-S4 + LOWs — prompt-injection fencing, escalation cross-links, doc notes |

### Deferred (documented, with rationale — not silently dropped)
- **QR-R3** (enforce ≤10 Anki cards / ≤1 new grammar concept per session): the session
  log has no structured field for these counts; enforcing it cleanly needs a schema
  addition, not speculative field-invention. → v1.2.
- **QR-L5** (dialect advisory searches only `prescriptive_episodes`, not podcasts/tv/
  audiobooks): low impact; the code already flags the future taxonomy refactor (CC-3). → v1.2.
- **QR-L4** (stale REQUIREMENTS.md / ROADMAP.md progress tables): these live in
  `.planning/`, which is now correctly gitignored and untracked — internal planning
  artifacts that don't affect the shipped system.
- **M9 sub-claim** `next_session.session_type: normal`: confirmed a FALSE POSITIVE
  (free-text field, "normal" is documented) — no change, correctly left as-is.
- **Register Shifting wikilink ambiguity** (vault): vault is gitignored/regenerated and
  the underlying grammar-vs-cultural naming is now disambiguated in CLAUDE.md.

**Status: ready for the canary first session.** Run `docs/canary-first-session.md`.
