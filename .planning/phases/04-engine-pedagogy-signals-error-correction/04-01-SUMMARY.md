---
phase: 04-engine-pedagogy-signals-error-correction
plan: 01
subsystem: curriculum
tags: [decision-engine, learner-interest, regression-ladder, scoring-dimensions, sla-pedagogy]

# Dependency graph
requires:
  - phase: 04-00
    provides: "Phase 4 planning context and research"
provides:
  - "INTEREST (0-3) scoring dimension in decision-engine.md Step 2"
  - "Updated PRIORITY formula with 6 dimensions"
  - "Step 0c regression escalation ladder with prerequisite and non-prerequisite tables"
  - "Worked Examples 1-4 with INTEREST column and regression-beats-interest demo"
  - "Doc-content test suite (34 tests) for decision engine integrity"
affects: [04-02, 04-03, 04-04, 04-05]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Additive capped dimension (0-3) in PRIORITY formula"
    - "Ladder table shape mirroring Step 0b for regression escalation"
    - "Data-driven approach switches reading recast_uptake_stats"

key-files:
  created:
    - "tests/test_decision_engine_doc.py"
  modified:
    - "curriculum/tutor-guides/decision-engine.md"

key-decisions:
  - "INTEREST dimension placed between TOPIC_BOOST and VARIETY_PENALTY with 0-3 additive cap"
  - "Stale decay at 28 days referenced in both Step 2 and Step 3 modifiers"
  - "Step 0c regression ladder uses tighter thresholds than Step 0b carryover ladder"
  - "approach_changed stage reads recast_uptake_stats with data-insufficiency fallback"

patterns-established:
  - "Doc-content test class pattern: pytest classes that parse decision-engine.md sections and assert structural invariants"
  - "Regression ladder mirrors carryover ladder shape (Sessions | Stage | Action columns) for doc consistency"

requirements-completed: [ENGINE-01, ENGINE-02, ENGINE-05]

# Metrics
duration: 4min
completed: 2026-04-15
---

# Phase 4 Plan 1: Decision Engine INTEREST Dimension + Regression Ladder Summary

**INTEREST (0-3) scoring dimension added to decision engine with stale decay, regression escalation ladder (Step 0c) with data-driven approach switches, and 4 worked examples including regression-beats-interest proof**

## Performance

- **Duration:** 3 min 43 sec
- **Started:** 2026-04-15T13:26:34Z
- **Completed:** 2026-04-15T13:30:17Z
- **Tasks:** 2
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments
- Added INTEREST (0-3) scoring dimension to Step 2 with 4-level rubric, signal source citations, stale decay rule, storage spec, and additive cap explanation
- Updated PRIORITY formula to include INTEREST term; recomputed Examples 1-3 (Example 3 C-04 now 17.0 vs 15.0); added Example 4 proving regression beats max interest
- Inserted Step 0c regression escalation ladder with prerequisite (5 stages, sessions 1-5+) and non-prerequisite (5 stages, sessions 1-9+) tables
- Step 0c approach_changed stage reads recast_uptake_stats with explicit low-uptake vs high-uptake decision paths and data-insufficiency fallback
- Created 34-test verification suite covering INTEREST dimension, cap mechanics, worked examples, and regression ladder structure

## Task Commits

Each task was committed atomically:

1. **Task 1: Add INTEREST dimension to Step 2 and update PRIORITY formula** - `cf8631e` (feat)
2. **Task 2: Add Step 0c Regression Escalation Ladder** - `5a205e1` (feat)

## Files Created/Modified
- `curriculum/tutor-guides/decision-engine.md` - Added INTEREST subsection in Step 2, stale decay in Step 3, Step 0c regression ladder, updated formula, recomputed examples 1-3, added example 4
- `tests/test_decision_engine_doc.py` - 34 doc-content tests across 4 test classes (TestInterestDimension, TestInterestCap, TestWorkedExamplesUpdated, TestRegressionLadder)

## Decisions Made
None - followed plan as specified. All content matched the plan's action blocks exactly.

## Deviations from Plan

None - plan executed exactly as written. The test file `tests/test_decision_engine_doc.py` was created as part of Task 1 since the plan's `<verify>` section referenced it but it did not pre-exist. This is standard for verification test creation during doc-editing plans.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- decision-engine.md now has all 6 PRIORITY dimensions and the regression escalation ladder
- Step 0c references `recast_uptake_stats` which will be added to skill-map schema in a later plan (04-03 or 04-04)
- Step 0c cross-links to `error-correction.md` Escalation Protocol which will be expanded in plan 04-02
- Example 4 references the INTEREST cap from ENGINE-02, providing auditable proof the cap works

---
*Phase: 04-engine-pedagogy-signals-error-correction*
*Completed: 2026-04-15*
