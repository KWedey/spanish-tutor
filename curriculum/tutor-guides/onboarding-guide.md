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
   - Sessions 3-4: Dreaming Spanish bookmarked, SpanishDict bookmarked
   - Sessions 5-6: Language Transfer queued (episodes 1-5), graded reader obtained
   - Sessions 7-8: Speechling account created
   - Sessions 9-10: Whisper transcription script set up (optional, if learner is technical)

## At Session 10

- Set `onboarding_complete: true` in schedule.yaml
- Write a summary of what you've learned about this learner's style, speed, and preferences
- Populate any learner-profile fields that are still blank
- The decision engine activates at session 11
- The learner shouldn't notice the transition — sessions just gradually become more tailored
