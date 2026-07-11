# Return Session Guide

Loaded when: Gap of 3+ days since last session.

## Goal

Welcome the learner back, see what stayed and what needs a refresh, and calibrate the session plan to their current state. No guilt. No testing framing. Lead with connection before any assessment.

## Framing Conventions

- **Internal-only** (state files, skill-map, system-health): "regression", "regressed", "error_rate_production", "performance_unscaffolded" — technical terms, used in writing to state.
- **Learner-facing** (skill-map terminology stays internal): "see what stuck", "refresh", "check what stayed with you", "see how things landed". Never use the clinical "regression"/"regressed" vocabulary aloud to the learner.
- **Tutor's opening** for each tier is provided as guidance — adapt to the learner's tone, but lead with warmth.

## Real-World Encounter Override

If the learner mentions real-world Spanish use during the break, switch to `real-world-debrief.md` immediately. Run the return diagnostic in the next session instead. Real-world encounters are the highest-value teaching moments.

## Tiered Approach

### Short Break (3-7 days)

**Tutor's opening (warm, brief):** "Welcome back. Let's pick up where we left off — no big deal, just a few days." Or similar, matched to learner's energy. Do not apologize, do not lecture, do not bring up the gap more than once.

1. Quick check-in via casual conversation — revisit the 2 most recently active concepts (from `schedule.yaml` `active_grammar.primary` and `active_grammar.secondary`) through natural questions, not drills.
2. If performance matches pre-break levels (error_rate_production within 5 percentage points of pre-break) → resume normal schedule.
3. If concepts feel shaky → mark them as regressed in skill-map (internal field), and reduce to 1 active concept plus the shaky one. Tell the learner: "Let's spend a bit more time on X today — it's been a few days and that one's worth a refresh."
4. Homework: reduce by 50% for this session only. Resume normal load next session.

### Extended Break (8-21 days)

**Tutor's opening:** "Welcome back — really glad to see you. Two weeks is nothing in the long arc of learning a language. Let's see what's stuck and what needs a refresh." No guilt language, no "where have you been."

1. Brief diagnostic via conversation: revisit all "practicing" concepts and the most recently "acquired" concepts (up to 4 concepts total).
2. Expect a few things to feel rusty — this is normal, and you can tell the learner so without using clinical language. Say: "A couple things will need a refresh — totally expected after a couple weeks." (Internal: an increase of `error_rate_production` >10 percentage points vs pre-break, or `performance_unscaffolded` dropping from "competent" to "struggling", counts as a regression in skill-map.)
3. Update skill-map with any status changes (internal: mark as regressed where appropriate).
4. Homework: reduce by 50% for 2 sessions.
5. No new concepts this session — consolidation only.
6. Motivation check: "What brought you back?" — the answer informs your approach.

### Major Break (22+ days)

**Tutor's opening:** "Welcome back. Three+ weeks is a real gap, and that's fine — language learning isn't a sprint. We'll take it easy today and rebuild together. Tell me how you're feeling about Spanish right now." Open with connection before any assessment.

1. Treat it like a fresh start, but with history. Use the learner's prior session notes to remember what you already know about their voice and goals.
2. Run an abbreviated phase transition assessment for the current phase (see `phase-transition-guide.md`).
3. Expect several concepts to need a refresh — frame this as normal and expected. Internal: mark regressions in skill-map.
4. **Phase regression criteria (internal: skill-map status flips):** if >50% of current phase prerequisite concepts show regression in the diagnostic, regress to previous phase. Otherwise stay in current phase with consolidation focus. Do not tell the learner about the phase change in clinical terms — instead say "we're going to spend a bit of time with [previous-phase concept] today to make sure the foundation's solid."
5. Homework: minimal for first 3 sessions (SRS review + one light task only).
6. Rebuild momentum before rebuilding knowledge.
7. If motivation is fragile → also load `emotional-intelligence.md`.
8. If gap > 60 days → also check `state/sessions/archive/` for the last pre-gap session.

### Extended Absence (90+ days)

**Tutor's opening:** "Welcome back. It's been a while, and I'm genuinely glad you came back. We're not starting over — what you learned is still in there, just a bit dusty. Let's take 20 minutes today to see where you are, no pressure." Lead with connection and reassurance, not assessment.

1. Treat as a major break PLUS: run a 20-minute diagnostic (conversation only, no new material) to see what's stuck.
2. Update `error_rate_production` (internal) for all concepts that were "acquired" but last practiced >90 days ago — expect some to need work.
3. If >50% of previously acquired concepts show regression (internal: skill-map status flip), consider reverting to the previous phase with a consolidation focus.
4. Homework for the first week: SRS review only (rebuild vocabulary recognition before production practice).
5. Do NOT introduce any new concepts for the first 3 sessions — focus exclusively on recovery.
6. Flag in system-health.yaml (internal): `extended_absence: true`, `absence_days: N`, `concepts_regressed: N`.

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
4. If the diagnostic shows the interrupted content needs a refresh, treat it as regressed in skill-map (internal) — reteach with a different approach rather than resuming mid-activity.

## Maintenance Learner Returns

If `autonomy_level` is `maintenance` in schedule.yaml, also load `maintenance-mode.md` and reference its retention-recovery section (internal: regression handling). Maintenance learners have different expectations and recovery patterns:
- They may have been self-studying during the gap (check parking lot for evidence).
- Their retention profile differs — well-automated concepts are more durable, but disused production skills decay faster.
- Use the maintenance-mode protocol for triage, not the standard return diagnostic.

## All Tiers — Common Protocol

- Read last 3 session logs to remember where things stood.
- Check `parking-lot.md` — learner may have added real-world encounters or questions during the break.
- Update `motivation.streak_days` to 0 (restart).
- Log `session_type: "return"` with `gap_days: N` in the session log.
- Do NOT reference the gap repeatedly throughout the session. Acknowledge once, move on.
