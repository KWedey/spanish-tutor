---
phase: 04-engine-pedagogy-signals-error-correction
plan: 03
subsystem: schema
tags: [yaml-schema, session-log, skill-map, engine-fields, recast-tracking, learner-interest]

requires:
  - phase: 04-00
    provides: "Phase 4 CONTEXT, RESEARCH, PATTERNS planning docs"
provides:
  - "recasts list field in session-log schema (D-05 per-event recast log)"
  - "INTEREST dimension in decision_engine_trace.top_candidates (D-04)"
  - "learner_interest per-concept field on grammar, vocabulary, cultural_awareness (D-01/D-03)"
  - "recast_uptake_stats per-concept field on grammar entries only (D-07)"
  - "regression_session_count per-concept field on grammar entries only (D-09/ENGINE-05)"
  - "Human-readable documentation of all new fields in docs/system-design.md"
affects: [04-04, validate-state, check-session-log, post-session, decision-engine]

tech-stack:
  added: []
  patterns: ["per-concept map field with children pattern in skill-map schema", "list field with item_shape pattern in session-log schema"]

key-files:
  created: []
  modified:
    - schemas/session-log.schema.yaml
    - schemas/skill-map.schema.yaml
    - docs/system-design.md

key-decisions:
  - "Placed recasts field after interleaved_concepts and before assignments in session-log schema for logical grouping"
  - "Used inline comment block for INTEREST per-candidate shape documentation rather than nested children to match existing top_candidates description style"

patterns-established:
  - "item_shape pattern for list-of-maps fields in session-log schema (concept_id, error_form, corrected_form, uptake, activity_stage)"
  - "Per-concept map-with-children pattern for skill-map extensions (learner_interest, recast_uptake_stats)"

requirements-completed: [ENGINE-03, ENGINE-07, ENGINE-08]

duration: 3min
completed: 2026-04-15
---

# Phase 04 Plan 03: Schema + Docs Extension Summary

**Extended session-log and skill-map YAML schemas with recast tracking, learner interest, uptake stats, and regression count fields; documented all in system-design.md**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-15T13:26:53Z
- **Completed:** 2026-04-15T13:30:17Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Added `recasts` top-level list field to session-log schema with full item_shape (concept_id, error_form, corrected_form, uptake tri-state enum, activity_stage)
- Added `INTEREST` dimension (int 0-3, D-04) to decision_engine_trace.top_candidates description and shape comment
- Extended grammar_entry_template with `learner_interest` (map), `recast_uptake_stats` (map), and `regression_session_count` (int)
- Added `learner_interest` to vocabulary_entry_template and cultural_awareness_entry_template (but NOT recast_uptake_stats per D-03 scope)
- Documented all new fields in docs/system-design.md with both code-block examples and prose explanations

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend session-log and skill-map YAML schemas** - `a4b86df` (feat)
2. **Task 2: Document new fields in docs/system-design.md** - `25739bc` (docs)

## Files Created/Modified
- `schemas/session-log.schema.yaml` - Added recasts list field with item_shape; added INTEREST to top_candidates description
- `schemas/skill-map.schema.yaml` - Added learner_interest (3 templates), recast_uptake_stats (grammar only), regression_session_count (grammar only)
- `docs/system-design.md` - Documented recasts in Session Logs section; added INTEREST to decision_engine_trace; added learner_interest, recast_uptake_stats, regression_session_count to Skill Map grammar block with prose explanations

## Decisions Made
- Placed recasts field after interleaved_concepts for logical grouping (recast data relates to session activities, not assignments)
- Used inline comment block for INTEREST per-candidate shape docs rather than nested children entries to match existing compact top_candidates style

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Schema definitions are complete and ready for Plan 04-04 (validator scripts and regression tests)
- Field names are byte-identical across all three files, satisfying Pitfall 3 consistency requirement
- Both YAML schemas parse cleanly via yaml.safe_load

---
*Phase: 04-engine-pedagogy-signals-error-correction*
*Completed: 2026-04-15*
