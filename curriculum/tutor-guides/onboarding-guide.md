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

## Each Onboarding Session

1. Read the corresponding `curriculum/onboarding/session-NN.md` for today's plan
2. Follow the plan, but adapt pacing if the learner is faster or slower than expected
3. Log everything in the session file — this data will feed the decision engine at session 11
4. Introduce one new external tool every 2-3 sessions (absolute session numbers):
   - Sessions 2-3: Anki installed and first deck created
   - Sessions 3-4: SpanishDict bookmarked, Dreaming Spanish bookmarked
   - Sessions 5-6: Language Transfer queued, graded reader obtained
   - Sessions 7-8: Speechling account created
   - Session 10: Whisper transcription script set up (optional, if learner is technical)
5. Sessions 7 and 11 are consolidation sessions (no new grammar concept). Use session 7 for midpoint review of sessions 2-6. If the learner has already been consolidating due to pacing adjustments, use the consolidation session for the next planned concept instead.

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
   - **Consolidation sessions** are scheduled (sessions 7 and 11) or inserted ad-hoc when a concept needs more time. They review existing concepts with no new grammar.
   - **Extended onboarding** (sessions 12-15) is a last resort when multiple concepts remain at "introduced" status after session 11.
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
