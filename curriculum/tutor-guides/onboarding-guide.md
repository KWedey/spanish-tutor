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
4. Introduce one new external tool every 2-3 sessions:
   - Sessions 1-2: Anki installed and first deck created
   - Sessions 2-3: SpanishDict bookmarked, Dreaming Spanish bookmarked
   - Sessions 4-5: Language Transfer queued, graded reader obtained
   - Session 7: Speechling account created
   - Session 9: Whisper transcription script set up (optional, if learner is technical)
5. Sessions 6 and 10 are consolidation sessions (no new grammar concept). Use session 6 for midpoint review of sessions 2-5. If the learner has already been consolidating due to pacing adjustments, use the consolidation session for the next planned concept instead.

## At Session 10 (Final Consolidation)

- Set `onboarding_complete: true` in schedule.yaml
- Write a summary of what you've learned about this learner's style, speed, and preferences
- Populate any learner-profile fields that are still blank
- The decision engine activates at session 11
- The learner shouldn't notice the transition — sessions just gradually become more tailored
