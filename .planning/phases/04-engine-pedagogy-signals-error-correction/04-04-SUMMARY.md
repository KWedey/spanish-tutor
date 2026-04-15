---
phase: 04-engine-pedagogy-signals-error-correction
plan: 04
subsystem: validation-enforcement
tags: [engine, validators, aggregation, recasts, learner-interest, post-session]
dependency_graph:
  requires: [04-00, 04-03]
  provides: [conditional-recasts-enforcement, learner-interest-validators, recast-aggregation]
  affects: [scripts/check-session-log.py, scripts/validate-state.py, scripts/post-session.sh]
tech_stack:
  added: []
  patterns: [date-guarded-enforcement, backward-compat-skip, additive-aggregation]
key_files:
  created: []
  modified:
    - scripts/check-session-log.py
    - scripts/validate-state.py
    - scripts/post-session.sh
decisions:
  - "PHASE_4_CUTOFF = 2026-04-20 for backward-compat date guard on recasts enforcement"
  - "learner_interest staleness uses WARN not FAIL (D-03: non-blocking)"
  - "recast_uptake_stats aggregation is additive-only (T-04-04-04: no deletion/overwrite)"
  - "Step numbering changed from /6 to /7 to accommodate Step 5b"
metrics:
  duration_seconds: 214
  completed: "2026-04-15T13:40:06Z"
  tasks_completed: 3
  tasks_total: 3
  files_modified: 3
  tests_passed: 127
  tests_failed: 0
---

# Phase 04 Plan 04: Wire ENGINE Fields into Validators and Aggregation Summary

Conditional recasts enforcement in check-session-log.py with PHASE_4_CUTOFF date guard, three new validator functions in validate-state.py (learner_interest range, staleness, recast_uptake_stats invariant), and Step 5b recast aggregation in post-session.sh.

## Task Completion

| Task | Name | Commit | Key Changes |
|------|------|--------|-------------|
| 1 | Add conditional recasts enforcement to check-session-log.py | 36678e2 | PHASE_4_CUTOFF, check_recasts_required, D-06 wiring |
| 2 | Add learner_interest and recast_uptake_stats validators to validate-state.py | 659fe64 | check_learner_interest_range, check_learner_interest_staleness, check_recast_uptake_stats_consistency |
| 3 | Add Step 5b recast aggregation to post-session.sh | 545e54a | Step 5b aggregator, step renumbering /6 to /7 |

## Implementation Details

### Task 1: Conditional Recasts Enforcement (check-session-log.py)

- Added `PHASE_4_CUTOFF = "2026-04-20"` at module level for backward compatibility
- Added `check_recasts_required(data: dict) -> bool` helper that detects when recasts are needed:
  - Short-circuits on `session_type == "fluency"` (Pitfall 6)
  - Scans `session_activities` for stage-3, stage-4, conversation, role-play, storytelling
  - Falls back to free-text scan for "recast" substring in activity notes/observations
- Wired into `check_log` after existing field iteration with date guard: `session_date >= PHASE_4_CUTOFF`
- FAIL message references D-06 decision ID

### Task 2: Validator Functions (validate-state.py)

- `check_learner_interest_range`: Iterates grammar, vocabulary, AND cultural_awareness. FAILs on score outside 0-3. Missing field = OK (D-10 backward compat).
- `check_learner_interest_staleness`: WARNs (not FAILs) when `last_inferred` > 28 days stale. Handles unparseable dates gracefully.
- `check_recast_uptake_stats_consistency`: Grammar-only (D-07). FAILs when `landed + missed + partial > recasts_given`. Missing stats = OK.
- All three registered in `main()` after existing skill-map checks.

### Task 3: Recast Aggregation (post-session.sh)

- Inserted Step 5b between protocol compliance check (Step 5) and git commit (Step 7)
- Aggregator reads `$SESSION_LOG` recasts array, writes to `$ROOT/state/skill-map.yaml`
- Handles empty recasts gracefully (`sys.exit(0)`)
- Initializes `recast_uptake_stats` with all-zero defaults when missing from grammar entry
- Increments `recasts_given` and matching uptake counter (`landed`/`missed`/`partial`)
- Sets `last_updated` to `$DATE`
- DRY_RUN branch prints preview without modifying files
- `yaml.safe_load` exclusively (V5 Input Validation / T-04-04-01)
- All step headers renumbered from `/6` to `/7`

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- `python3 -m pytest tests/test_check_session_log.py` - 43 passed
- `python3 -m pytest tests/test_validate_state.py` - 68 passed
- `python3 -m pytest tests/test_schema_fields_present.py` - 16 passed (4 previously RED now GREEN)
- `bash -n scripts/post-session.sh` - exits 0
- Full suite: 127 passed, 0 failed

### RED-to-GREEN Tests

| Test | Status |
|------|--------|
| TestRecastsFieldPresent::test_check_session_log | RED -> GREEN |
| TestLearnerInterestFieldPresent::test_validate_state | RED -> GREEN |
| TestRecastUptakeStatsFieldPresent::test_validate_state | RED -> GREEN |
| TestFieldNameConsistency::test_recast_uptake_stats_cross_file_count | RED -> GREEN |

## Threat Mitigations Applied

| Threat ID | Mitigation |
|-----------|-----------|
| T-04-04-01 | yaml.safe_load exclusively in Step 5b heredoc; concept_id validated against grammar dict; uptake checked against enum |
| T-04-04-02 | isinstance(score, int) type check; .get(..., 0) or 0 safe defaults; no learner data echoed in error messages |
| T-04-04-03 | FAIL messages reference field paths and D-06 decision ID, not learner data values |
| T-04-04-04 | Aggregator only increments counters (additive); Step 0 snapshot provides rollback |

## Self-Check: PASSED

- All 3 modified files exist on disk
- All 3 task commits found in git log (36678e2, 659fe64, 545e54a)
- SUMMARY.md exists at expected path
- 127 tests pass, 0 fail
