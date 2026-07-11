# Engine API — Portable Session-Lifecycle Contracts

This document defines the tutor system's **engine boundary**: the deterministic functions a
port (web app, mobile app, or any non-Claude-Code host) must implement, with their inputs and
outputs expressed in terms of the state files (`schemas/*.schema.yaml`) and the curriculum data
banks. The conversational tutoring itself is an LLM concern; everything below is deterministic,
testable logic that today lives in `scripts/` (implemented) or in tutor-guide prose + data files
(specified). `scripts/route_session.py` is the reference implementation style: a pure function
over state that returns a typed value, no side effects, no host coupling.

## Architecture at a glance

```
┌────────────────────────────────────────────────────────┐
│ Host (Claude Code today; web/mobile app later)         │
│                                                        │
│  LLM transport      StateStore backend    Renderer     │
│  (Claude Code       (filesystem today;    (Obsidian    │
│   session / API)     SQLite/IndexedDB/     vault today; │
│                      cloud KV later)       app UI later)│
└──────────┬───────────────┬────────────────────┬────────┘
           │               │                    │
┌──────────▼───────────────▼────────────────────▼────────┐
│ ENGINE (deterministic kernel — this document)          │
│  validate · route · score · gates · ladders · metrics  │
│  session-log checks · view-model projection            │
├─────────────────────────────────────────────────────────┤
│ DATA (portable as-is)                                   │
│  schemas/ · curriculum/manifest.yaml ·                  │
│  curriculum/decision-weights.yaml ·                     │
│  curriculum/error-correction-matrix.yaml ·              │
│  curriculum/*.yaml banks · curriculum/**/*.md content   │
└─────────────────────────────────────────────────────────┘
```

The LLM is the *tutor* (conversation, lesson delivery, judgment calls flagged as such); the
engine is the *registrar* (state, scoring, gates, guardrails). A port replaces the host layer
and re-implements the engine functions below in its own language; the data layer ships
unchanged. The existing pytest suite is the engine's behavioral oracle.

## State model

Six state documents, validated by `schemas/*.schema.yaml` (machine-enforced source of truth;
`docs/system-design.md` is the human-readable companion):

| Document | Schema | Written by |
|----------|--------|-----------|
| learner-profile | `schemas/learner-profile.schema.yaml` | init; rarely updated |
| skill-map | `schemas/skill-map.schema.yaml` | every session |
| schedule | `schemas/schedule.schema.yaml` | every session |
| session log (per day) | `schemas/session-log.schema.yaml` | every session |
| resource-tracker | `schemas/resource-tracker.schema.yaml` | sessions with input homework |
| system-health | `schemas/system-health.schema.yaml` | every session |

All state carries `schema_version` (currently 1). Forward migrations are additive
(`scripts/migrate-state.py`); a port must run the same migration chain before reading
older state.

### StateStore interface

```
StateStore:
  load(doc_name) -> dict | None          # None if absent
  save(doc_name, data) -> None           # atomic write
  list_sessions() -> [date]              # session-log dates, sorted
  load_session(date) -> dict | None
  save_session(date, data) -> None
```

The repo implementation is the filesystem (`state/*.yaml`, `state/sessions/*.yaml`) via
`scripts/shared.py`. A port supplies its own backend; nothing in the engine may assume paths,
git, or a working directory.

## Lifecycle contracts

### 1. `validate_state(state) -> ValidationReport`

Reference implementation: `scripts/validate-state.py` (~38 checks).
`ValidationReport = {passes: [str], warnings: [str], failures: [str]}`. Failures block the
session and route to error recovery (`curriculum/tutor-guides/error-recovery.md`); warnings
are logged to system-health.

### 2. `route_session(state, today) -> SessionType`

Reference implementation: `scripts/route_session.py` (pure, locale-independent, enum-typed —
the template for every other contract). Encodes the CLAUDE.md Step 3 routing table including
precedence (first-session > onboarding > return > maintenance > weekly-review > sprint >
fluency > standard) and the row-level overrides.

### 3. `score_candidates(skill_map, schedule, weights, context) -> ScoredCandidates`

Specified by: `curriculum/decision-weights.yaml` (numbers) + `curriculum/tutor-guides/decision-engine.md`
Steps 1-3 (semantics). `context` carries today's energy/motivation/parking-lot/sprint inputs.
Output: ranked `[{concept_id, priority, dimensions: {need, gap, decay_adjusted, topic_boost,
interest, variety_penalty}}]` — exactly the shape the session log's `decision_engine_trace`
records, so the trace is the oracle for porting this function.

### 4. `select_focus(scored, skill_map) -> {primary, secondary, interleaved[]}`

Specified by: decision-engine.md Steps 4-5b + `decision-weights.yaml` `selection`,
`concurrent_concept_gate`, and `interleaving` blocks.

### 5. `error_correction_mode(stage, phase) -> {mode, frequency, explicit_cap}`

Specified by: `curriculum/error-correction-matrix.yaml` (extracted from
`curriculum/activities/error-correction.md`, the pedagogical source of truth).

### 6. `acquisition_gate(entry, category) -> bool`

Specified by: `decision-weights.yaml` `acquisition_gate` + CLAUDE.md guardrails (LOAD-01/D-02).
CORE categories (grammar, vocabulary) use the numeric gate; SECONDARY categories
(pronunciation, writing, cultural_awareness) are tutor judgment recorded in notes.

### 7. `apply_homework_load_ladder(rating, counters, budget) -> {counters', budget', actions[]}`

The D-11 ladder (CLAUDE.md Review & Warm-up): one `too-much` → next-session sum ≤ daily_target;
two consecutive → daily_target −20% (rounded to nearest 5); three consecutive `just-right`
after a reduction → +10% restore; two consecutive `too-light` → weekly-review flag.
Drift detectors in `validate-state.py` (`check_daily_target_tier_drift`,
`check_just_right_restore_drift`) are the current enforcement and become this function's tests.

### 8. `escalate_carryover(entry) -> stage` / `escalate_regression(entry) -> stage`

Specified by: `decision-weights.yaml` `carryover_escalation` / `regression_escalation`
(from decision-engine.md Steps 0b/0c), including the recast-uptake approach-switch thresholds.

### 9. `check_session_log(log, schedule) -> GuardrailReport`

Reference implementation: `scripts/check-session-log.py` — homework-minutes budget (LOAD-03/05),
max 10 new Anki cards, max 1 new grammar concept (QR-R3), homework_load_rating presence,
correction-mode consistency. FAIL aborts the post-session pipeline before persistence.

### 10. `derive_metrics(state, session_log) -> state'`

Reference implementations: `scripts/recompute-metrics.py` (rolling error rates,
regression_session_count), `scripts/update-fluency-tracking.py` (week-aware fluency-day
counters), post-session recast aggregation (post-session.sh Step 5b). These are deterministic
derivations the LLM must never hand-compute; a port runs them after every session commit.

### 11. `view_model(state, manifest) -> ViewModel`

The learner-facing projection: roadmap (phases → concepts with status), per-concept detail,
weekly progress summary, milestones, streaks. Today rendered as an Obsidian vault by
`scripts/generate-vault.py`; a port renders the same projection as native UI. The vault
generator is the reference for what the projection must contain.

## Prompt boundary

CLAUDE.md is the current system prompt and intentionally repo-coupled. For a port, the prompt
splits into:

1. **Tutor persona + pedagogy** (Voice & Approach, session flow, error-correction behavior,
   language-of-instruction ratios) — portable prose, host-independent.
2. **Protocol orchestration** (startup steps, routing, state updates) — replaced by engine
   calls in a port; the app drives the lifecycle and hands the LLM only the loaded context
   (today's session type, focus concepts, relevant guide sections).
3. **Repo mechanics** (paths, git, scripts) — host layer, not ported.

## Porting checklist

- [ ] Implement StateStore on the target backend; run migrate chain on load
- [ ] Port engine functions 1-11 (route_session first — reference implementation exists);
      use the pytest suite's cases as the conformance oracle
- [ ] Ship `schemas/json/` (JSON Schema exports) for client-side validation/typegen
- [ ] Bundle curriculum data (`curriculum/manifest.yaml` + data banks + content .md) as a
      versioned content package
- [ ] Split the prompt per the boundary above; wire LLM transport
- [ ] Render `view_model` natively (vault generator = reference)
