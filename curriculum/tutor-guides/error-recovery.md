# Error Recovery Guide

Loaded when: State validation fails during the startup protocol.

## Severity Levels

### LOW — Fixable Inconsistency
Auto-fix silently. Log the fix in system-health.yaml.

Examples:
- Error rate doesn't match recent session data — recalculate from sessions
- `passive_known < active_known` for a vocabulary cluster — set passive = active
- Missing non-critical field — populate with reasonable default

### MEDIUM — Ambiguous State
Fix and inform learner briefly.

Examples:
- Status is "acquired" but recent error rate is 40% — downgrade to "practicing" and tell the learner: "I noticed a small data issue and corrected it — your [concept] skill was marked inconsistently."
- Schedule references a concept not in skill-map — add the concept entry

### HIGH — Unparseable File or Major Corruption
Attempt to recover from git history:

1. Run `git log --oneline -5 state/` to find recent good state
2. If recoverable, roll back that specific file: `git checkout <commit> -- state/<file>`
3. Inform the learner: "I found a data issue and recovered from a backup. Everything should be fine."

If not recoverable:
1. Inform the learner honestly
2. Rebuild state from the most recent session logs and summaries
3. Ask the learner to confirm key details if needed
4. This is a last resort — it loses some data but gets the system running

## Always

- Log all validation issues and recoveries in `state/system-health.yaml` under `last_validation_issues`
- Never silently ignore a validation failure
- Never let a validation failure prevent the session from starting — degrade gracefully
