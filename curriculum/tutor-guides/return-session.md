# Return Session Guide

Loaded when: Gap of 3+ days since last session.

## Goal

Welcome the learner back, assess what's been retained, and calibrate the session plan to their current state. No guilt. No testing framing.

## Real-World Encounter Override

If the learner mentions real-world Spanish use during the break, switch to `real-world-debrief.md` immediately. Run the return diagnostic in the next session instead. Real-world encounters are the highest-value teaching moments.

## Tiered Approach

### Short Break (3-7 days)

1. Welcome back warmly. Zero guilt.
2. Quick diagnostic: revisit the 2 most recently active concepts (from `schedule.yaml` `active_grammar.primary` and `active_grammar.secondary`) via casual conversation — not drills.
3. If performance matches pre-break levels (error_rate_production within 5 percentage points of pre-break) → resume normal schedule.
4. If regression detected → mark concepts as regressed in skill-map, reduce to 1 active concept + the regressed one.
5. Homework: reduce by 50% for this session only. Resume normal load next session.

### Extended Break (8-21 days)

1. Welcome back, acknowledge the gap without judgment.
2. Diagnostic: revisit all "practicing" concepts and the most recently "acquired" concepts (up to 4 concepts total).
3. Expect 1-2 regressions — this is normal, tell the learner so. (A regression = error_rate_production increases by >10 percentage points vs pre-break levels, or performance_unscaffolded drops from "competent" to "struggling".)
4. Update skill-map with any status changes.
5. Homework: reduce by 50% for 2 sessions.
6. No new concepts this session — consolidation only.
7. Motivation check: "What brought you back?" — the answer informs your approach.

### Major Break (22+ days)

1. Welcome back as if it's a fresh start, but with history.
2. Run abbreviated phase transition assessment for current phase (see `phase-transition-guide.md`).
3. Regressions likely across multiple concepts — don't alarm the learner.
4. **Phase regression criteria:** if >50% of current phase prerequisite concepts show regression in the diagnostic, regress to previous phase. Otherwise stay in current phase with consolidation focus.
5. Homework: minimal for first 3 sessions (SRS review + one light task only).
6. Rebuild momentum before rebuilding knowledge.
7. If motivation is fragile → also load `emotional-intelligence.md`.
8. If gap > 60 days → also check `state/sessions/archive/` for the last pre-gap session.

### Extended Absence (90+ days)
1. Treat as a major break PLUS: run a 20-minute diagnostic (conversation only, no new material) to assess broad skill decay.
2. Update `error_rate_production` for all concepts that were "acquired" but last practiced >90 days ago — expect regression.
3. If >50% of previously acquired concepts show regression, consider reverting to the previous phase with a consolidation focus.
4. Homework for the first week: SRS review only (rebuild vocabulary recognition before production practice).
5. Do NOT introduce any new concepts for the first 3 sessions — focus exclusively on recovery.
6. Flag in system-health.yaml: `extended_absence: true`, `absence_days: N`, `concepts_regressed: N`.

## Short Gap with Continued Study — Shortcut

If gap is 3-5 days AND the most recent session log shows homework completed AND `parking-lot.md` has new entries added during the gap, skip the full return protocol. Instead:
1. Run a standard session with a brief check-in: "Welcome back — looks like you kept at it. How'd the homework go?"
2. Verify homework claims naturally (as in a standard session).
3. Address 1-2 parking lot items during warm-up.
4. Proceed with normal decision engine flow.

The full return diagnostic is unnecessary when evidence shows the learner stayed engaged during a short gap.

## Partial Session + Gap

If the most recent session log has `session_status: partial` AND the gap is 3+ days:
1. Run the return diagnostic first (per the appropriate tier above) to assess current retention.
2. After diagnostic, check what was interrupted in the partial session's `session_activities` and `next_session.recommended_focus`.
3. If the diagnostic shows the interrupted content was retained, resume it as the primary focus.
4. If the diagnostic shows regression on the interrupted content, treat it as a regressed concept — reteach with a different approach rather than resuming mid-activity.

## Maintenance Learner Returns

If `autonomy_level` is `maintenance` in the learner profile, also load `maintenance-mode.md` and reference its regression handling section. Maintenance learners have different expectations and recovery patterns:
- They may have been self-studying during the gap (check parking lot for evidence).
- Their regression profile differs — well-automated concepts are more durable, but disused production skills decay faster.
- Use the maintenance-mode regression protocol for triage, not the standard return diagnostic.

## All Tiers — Common Protocol

- Read last 3 session logs to remember where things stood.
- Check `parking-lot.md` — learner may have added real-world encounters or questions during the break.
- Update `motivation.streak_days` to 0 (restart).
- Log `session_type: "return"` with `gap_days: N` in the session log.
- Do NOT reference the gap repeatedly throughout the session. Acknowledge once, move on.
