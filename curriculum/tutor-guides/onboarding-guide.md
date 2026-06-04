# Onboarding Guide (Sessions 2-10)

Loaded when: `onboarding_complete` is false in schedule.yaml.

## Purpose

During onboarding, follow the fixed sequence in `curriculum/onboarding/` rather than the decision engine. The decision engine doesn't have enough data yet.

This period accomplishes:
- Introduce core Phase A concepts in a tested, reliable order
- Collect baseline performance data (error rates, learning speed, energy patterns)
- Discover the learner's preferences (grammar approach, correction style, motivation triggers)
- Set up external tools progressively (don't overwhelm on day 1)
- Build momentum with early wins

## Concurrent Concept Cap

During onboarding, the decision engine is not loaded, so its concurrent concept gate does not apply automatically. Enforce it manually: **never advance to a new concept if 3+ concepts are currently in "practicing" status.** If 3 concepts are practicing, the next onboarding session should consolidate existing concepts instead of introducing the next one in the sequence. Insert an unscheduled consolidation session (see "Struggling During Onboarding" below) and resume the sequence once at least one concept advances to "acquired."

This cap exists because cognitive load from too many active concepts degrades learning across all of them. It is better to slow the onboarding sequence than to introduce material the learner cannot absorb.

## Ser/Estar Avoidance (Sessions 2-4)

Ser vs estar is not formally introduced until session 5 (A-02). In sessions 2-4, restrict production activities to contexts that minimize ser/estar demand:
- **Prefer:** action verbs (comer, ir, hablar, trabajar), routine descriptions ("por la mañana como..."), tener expressions (tengo hambre, tengo 30 años), hay constructions
- **Avoid:** descriptive tasks requiring adjective + ser/estar ("the house is big," "I am tired"), location tasks ("the book is on the table"), profession/identity tasks ("I am a teacher")
- If the learner spontaneously uses ser or estar correctly, acknowledge it but do not teach the contrast yet. If they use it incorrectly, do not correct — simply note the error for session 5.
- The goal is to build confidence with action-oriented Spanish before introducing the ser/estar distinction, which is a major L1 interference point.

## Each Onboarding Session

1. Read the corresponding `curriculum/onboarding/session-NN-*.md` for today's plan (zero-padded `NN` with a descriptive suffix, e.g. `session-02-present-tense.md` — match the single file for that number, per CLAUDE.md L65)
2. Follow the plan, but adapt pacing if the learner is faster or slower than expected
3. Log everything in the session file — this data will feed the decision engine at session 11
4. Introduce one new external tool every 2-3 sessions (absolute session numbers):
   - Sessions 2-3: Anki installed and first deck created
   - Sessions 3-4: SpanishDict bookmarked, Dreaming Spanish bookmarked
   - Sessions 5-6: Language Transfer queued, graded reader obtained
   - Sessions 7-8: Speechling account created
   - Session 10: Whisper transcription script set up (optional, if learner is technical)
5. Sessions 6 and 10 are scheduled consolidation sessions (no new grammar concept) — they correspond to `session-06-consolidation-midpoint.md` and `session-10-consolidation-final.md`. Use session 6 for midpoint review of sessions 1-5. If the learner has already been consolidating due to pacing adjustments, use the consolidation session for the next planned concept instead.
6. **Advance the onboarding counter.** Once today's planned concept has been delivered, set `current_onboarding_session` to the next session number (`N+1`) in `schedule.yaml` before finishing (CLAUDE.md State Updates step 4 also covers this). **Hold the number** (do not advance) on a partial/interrupted session, a gap-resume session (see "Gap During Onboarding"), or an *ad-hoc inserted* consolidation session (the unscheduled ones from "Struggling During Onboarding"). The two *scheduled* consolidations (sessions 6 and 10) are part of the normal 10-session arc and do advance. Without this step the next session silently re-serves the same content.

## At Session 10 (Final Consolidation)

- Set `onboarding_complete: true` in schedule.yaml
- Write a summary of what you've learned about this learner's style, speed, and preferences
- Populate any learner-profile fields that are still blank
- The decision engine activates at session 11
- The learner shouldn't notice the transition — sessions just gradually become more tailored

## Post-Onboarding Transition Note

Sessions 1-10 cover A-00 through A-07. Two Phase A concepts remain:
- **A-08 (Numbers & Quantifiers)** — prerequisite: A-03
- **A-09 (Accent & Stress Rules)** — no prerequisites

These are intentionally left for the decision engine to introduce in sessions 11+. The first post-onboarding standard session should load `decision-engine.md` and these concepts will score highest in NEED (phase prerequisite + unseen). No special handling required — the engine will prioritize them naturally. Session 10 should mention to the learner: "Starting next session, I'll be adapting to you instead of following a fixed script."

## Struggling During Onboarding

### Signals
- Unable to reproduce previous session's concept after review
- Error rate >50% on controlled practice after full explanation
- Learner expresses frustration or confusion 2+ sessions in a row
- Homework consistently incomplete or reported as too difficult

### Step 1 — Check External Factors FIRST

Before assuming concept difficulty, check:
- Is homework getting done? If not, the fix is reducing load, not reteaching.
- Has available study time changed? Life events, schedule shifts?
- Is the learner overwhelmed by tools (Anki setup, multiple apps)?
- Ask: "How's your study time been this week?"
- If external factors are the cause → adjust homework load and tool expectations. Do NOT insert consolidation.

### Step 2 — If Concept Difficulty Confirmed

1. Never repeat the exact same session — reteach with a different approach (examples-first if rules-first failed, or vice versa).
2. Insert an unscheduled consolidation session before advancing.
   - **Consolidation sessions** are scheduled (sessions 6 and 10) or inserted ad-hoc when a concept needs more time. They review existing concepts with no new grammar.
   - **Extended onboarding** (sessions 11-15) is a last resort when multiple concepts remain at "introduced" status after session 10.
3. Maximum 2 inserted consolidation sessions per concept — if still struggling, note as "slow acquisition" in skill-map and continue forward (concept resurfaces via decision engine post-onboarding).
4. Extend onboarding beyond session 10 if:
   - 3+ A-phase concepts are still "introduced" (not "practicing")
   - Learner hasn't demonstrated basic sentence construction
   - Communication repair phrases are not emerging
   - Maximum extension: 5 additional sessions (to session 15)
5. If extended onboarding exceeds session 15:
   - Complete onboarding regardless
   - Decision engine takes over with heavy consolidation weighting
   - Flag in system-health.yaml: `onboarding_extended: true`, `onboarding_sessions: N`
   - Reduce `max_new_concepts_per_week` to 1

### Emotional Considerations
- Never imply the learner is behind or slow
- Frame consolidation as "let's make sure this is solid before we build on it"
- Adjust energy: more games, less drilling

## Weekly Review During Onboarding

If the learner's `weekly_review_day` falls during onboarding, run a simplified review:

1. Progress check: "Here's what we've covered so far" — list concepts introduced and their status.
2. Homework review: completion rate, difficulty feedback.
3. Tool check: is Anki working? Any setup issues?
4. Quick wins: highlight 2-3 specific things they can do now that they couldn't before.
5. Motivation check: "How's it feeling so far?"

**Skip:** narrow topic selection, decision engine references, skill-map audit, system health review, resource rotation.

Write an abbreviated weekly summary noting it's an onboarding review. First full weekly review happens the first review day after `onboarding_complete = true`.

## Gap During Onboarding

If the learner has a 3+ day gap during onboarding (CLAUDE.md Step 3 routes the session to Onboarding but also loads `return-session.md`), use this resume protocol — do not skip ahead to the next session number.

1. Run the appropriate `return-session.md` tier on concepts covered so far. Use the lightweight conversational diagnostic, not a formal test.
2. Identify any concepts that feel rusty — internally mark them as regressed in skill-map, but frame to the learner as "let's refresh X before we move on."
3. **Resume from the same `current_onboarding_session`** in `schedule.yaml` — the session number does not advance until the planned concept is delivered.
4. If 2+ concepts feel rusty after a long gap (8+ days), insert an unscheduled consolidation session (per "Struggling During Onboarding" Step 2) before resuming the sequence.
5. Homework load follows the `return-session.md` tier reduction (50% for one or two sessions), not the standard onboarding load.

**Why resume same-step rather than advance:** Onboarding builds A-00 → A-07 in a deliberate order. Skipping a session due to a gap fragments the foundation. The cost of "repeating" today's planned content is far smaller than the cost of building on weak ground.
