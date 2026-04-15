---
phase: 04-engine-pedagogy-signals-error-correction
plan: 02
subsystem: curriculum
tags: [error-correction, metalinguistic-feedback, pedagogy, correction-matrix]

# Dependency graph
requires:
  - phase: 04-00
    provides: "Phase 04 planning context, RESEARCH.md with metalinguistic protocol and matrix content"
provides:
  - "Stage x Phase Correction Matrix (4x4) in error-correction.md as source of truth"
  - "Metalinguistic Feedback Protocol with when/how/guardrails"
  - "CLAUDE.md footnote cross-referencing error-correction.md matrix"
  - "Escalation Protocol cross-link to decision-engine.md Step 0c"
affects: [04-01, 04-03, decision-engine, session-flow]

# Tech tracking
tech-stack:
  added: []
  patterns: ["source-of-truth delegation (CLAUDE.md -> error-correction.md)", "stage x phase matrix pattern for correction mode selection"]

key-files:
  created:
    - tests/test_error_correction_doc.py
  modified:
    - curriculum/activities/error-correction.md
    - CLAUDE.md

key-decisions:
  - "Used RESEARCH.md content verbatim for metalinguistic protocol (proper Spanish accents preserved)"
  - "Kept CLAUDE.md table unmodified as quick reference; full matrix lives in error-correction.md only"
  - "Created test file for matrix/protocol/consistency checks (20 tests) since plan verification assumed it existed"

patterns-established:
  - "Source-of-truth footnote: CLAUDE.md quick-reference table delegates to error-correction.md matrix for authoritative rules"
  - "Cross-link pattern: Escalation Protocol (execution) links to decision-engine.md Step 0c (decision)"

requirements-completed: [ENGINE-04, ENGINE-06]

# Metrics
duration: 4min
completed: 2026-04-15
---

# Phase 04 Plan 02: Error Correction Matrix and Metalinguistic Protocol Summary

**Explicit 4x4 Stage x Phase Correction Matrix replacing implicit correction dichotomy, with Metalinguistic Feedback Protocol as third correction tier and CLAUDE.md source-of-truth footnote**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-15T13:26:24Z
- **Completed:** 2026-04-15T13:30:18Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Replaced vague "Recasting vs explicit correction" prose with a complete 4-stage x 4-phase correction matrix specifying MODE, FREQUENCY, and explicit-vs-recast ratios per cell
- Added Metalinguistic Feedback Protocol section with trigger conditions, phrasing guidelines (1 rule + 1 example + 1 learner example), and 6 "What NOT to do" guardrails including 1-concept-per-session cap
- Added source-of-truth footnote to CLAUDE.md Error Correction table, establishing error-correction.md matrix as authoritative while keeping CLAUDE.md as quick reference
- Added cross-link from Escalation Protocol to decision-engine.md Step 0c connecting execution and decision sides of regression handling

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace implicit correction dichotomy with Stage x Phase Matrix and add Metalinguistic Feedback Protocol** - `c5aff6f` (feat)
2. **Task 2: Annotate CLAUDE.md Error Correction table with source-of-truth footnote** - `4e8fa0f` (feat)

## Files Created/Modified
- `curriculum/activities/error-correction.md` - Added Stage x Phase Correction Matrix, Metalinguistic Feedback Protocol, Escalation cross-link; replaced implicit dichotomy
- `CLAUDE.md` - Added source-of-truth footnote below Error Correction table referencing matrix and metalinguistic protocol
- `tests/test_error_correction_doc.py` - 20 regression tests covering matrix structure, protocol subsections, CLAUDE.md consistency

## Decisions Made
- Used RESEARCH.md metalinguistic protocol content verbatim with proper Spanish accents (matching existing error-correction.md convention)
- Kept CLAUDE.md Error Correction table rows entirely unmodified -- footnote provides the source-of-truth delegation without duplicating matrix content (per RESEARCH.md Pitfall 1)
- Created test_error_correction_doc.py with 20 tests since the plan's verification step assumed the test file existed (Rule 3 - blocking issue)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created missing test file test_error_correction_doc.py**
- **Found during:** Task 1 (verification step)
- **Issue:** Plan verification references `tests/test_error_correction_doc.py` with specific test classes (TestStagePhaseMatrix, TestMetalinguisticProtocol, TestClaudeMdConsistency) but the file did not exist
- **Fix:** Created the test file with 20 tests across 3 test classes matching the plan's expected test structure
- **Files modified:** tests/test_error_correction_doc.py
- **Verification:** All 20 tests pass green
- **Committed in:** c5aff6f (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Test file creation was necessary for the plan's verification to work. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Error correction framework is now fully explicit with matrix + protocol
- CLAUDE.md and error-correction.md are cross-referenced without contradiction
- Ready for remaining Phase 04 plans (recast uptake tracking, regression escalation, learner interest signal)

## Self-Check: PASSED

All created files verified on disk. All commit hashes found in git log.

---
*Phase: 04-engine-pedagogy-signals-error-correction*
*Completed: 2026-04-15*
