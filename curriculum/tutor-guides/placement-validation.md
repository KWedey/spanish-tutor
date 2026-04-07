# Placement Validation Guide

Loaded when: `placement_validation.active` is true and `placement_validation.sessions_completed` < 3 in schedule.yaml. This applies only to learners who skipped onboarding (Early B+ placement).

## Purpose

Confirm or correct the initial placement through real practice. The learner should experience this as normal warm-up and conversation — never as testing.

## How It Works

Each session during the validation period (sessions 2-4), overlay 2-3 spot-checks on top of the normal session flow. The decision engine runs normally — validation adds to the session, it doesn't replace it.

## Session Flow Overlay

### Before the session
1. Read `placement_validation.queue` from schedule.yaml
2. Select 2-3 concepts to validate this session (highest priority `pending` items)
3. Plan warm-up topics and conversation prompts that naturally elicit these structures

### During warm-up and conversation
4. Use directed conversation to elicit target concepts (see Elicitation Examples below)
5. Observe and score each concept
6. Do NOT tell the learner you're validating placement — frame everything as getting to know them

### After the session
7. Log results in the session file under `validation_checks`
8. Process downgrades (max 2 per session)
9. Update `placement_validation.sessions_completed`
10. Update the queue: mark checked concepts, add `pending_downgrade` for deferred downgrades

## Elicitation Examples

Choose warm-up topics and conversation prompts that naturally require the target structure:

| Concept | Natural elicitation |
|---|---|
| A-01 present regular | "Tell me about your typical day." |
| A-02 ser vs estar | "How are you feeling today? Describe your house." |
| A-03 gender agreement | "What's your favorite restaurant like? Describe it." |
| A-05 basic questions | "Ask me a few questions about myself." |
| A-06 gustar-type verbs | "What do you like doing on weekends? What bothers you?" |
| A-07 present irregular | "What do you want to do this summer? What do you know about...?" |
| B-01 preterite regular | "What did you do this weekend?" |
| B-03 imperfect | "What was your childhood like? What did you used to do?" |
| B-04 preterite vs imperfect | "Tell me about a trip — what was happening, what happened." |
| B-05 reflexive verbs | "Walk me through your morning routine." |
| B-06 direct object pronouns | "Did you finish the homework? When did you start it?" |
| B-07 indirect object pronouns | "Tell me about a gift you gave someone." |
| B-08 progressive | "What are you working on these days?" |
| C-01 present subjunctive | "What do you hope happens this year?" |
| C-04 conditional | "If you could live anywhere, where would it be?" |

## Scoring Rubric

For each spot-checked concept:

| Observation | Result | Action |
|---|---|---|
| Uses concept correctly and naturally | Validated | Stays `acquired`, remove from queue, log `checked-pass` |
| Minor errors (1-2 per exchange) | Validated with note | Stays `acquired`, add maintenance note to skill-map, log `checked-pass` |
| Significant errors, struggles to produce | Downgrade | → `practicing`, set error rates from observation, log `checked-fail` |
| Can't produce or avoids entirely | Downgrade | → `introduced`, flag for Stage 1-2 work, log `checked-fail` |
| Concept not naturally elicited by the conversation | Inconclusive | Remains `pending` in queue for next session |

## Downgrade Rules

- **Maximum 2 downgrades per session.** If 3 concepts fail in one session, record all failures but defer the third downgrade: mark it `pending_downgrade` in the queue. Process the status change at the start of the next session — do not re-validate it.
- **Each downgrade:** Update skill-map (status, error rates), log in session file with evidence.
- **Prerequisite cascade:** If a downgraded concept is a prerequisite for other acquired concepts, those dependent concepts should be queued for validation in the next session (they may be fine, but check).

## Widespread Gap Handling

If total downgrades across the validation period reach 4+:

1. Log `placement_adjustment: significant` in the session file
2. Reduce `max_new_concepts_per_week` to 1 in schedule.yaml
3. Note in system-health.yaml under `placement_validation_metrics`
4. Frame to the learner: "You've got a solid foundation — there are just some spots I want to make sure are rock solid before we build on them."
5. Do NOT reroute to onboarding. The decision engine handles recovery through its existing mechanics (concurrent concept cap, prerequisite gating, NEED scoring).

## Listening Baseline (Session 2)

During the session 2 warm-up:
1. Review the Dreaming Spanish assignment from session 1
2. Ask: "What level did you watch? How much did you follow?"
3. If the learner's `calibration.tendency` is `over-estimates`, probe: "What was the video about? Can you summarize what happened?"
4. Set `receptive_skills.listening.current_level` based on reported and observed comprehension
5. Set `placement_validation.listening_baseline_set: true`

## Closing the Validation Period

After session 4 (or session 3 if confidence is high and no downgrades):

1. Concepts still `pending` in queue: accept current status if overall performance is consistent. If performance has been mixed, extend to session 5 (maximum).
2. Process any remaining `pending_downgrade` items
3. Set `placement_validation.active: false`
4. Set `placement_validation.confidence: validated`
5. Log validation summary in the session file:
   - Total concepts validated
   - Pass/downgrade counts
   - Final assessment: `placement-confirmed` or `placement-adjusted`
6. Update `system-health.yaml` `placement_validation_metrics` with final numbers

## Early Close Criteria

Close validation after session 3 (skip session 4) if ALL of:
- Placement confidence was high or medium
- Zero downgrades in sessions 2-3
- Overall session performance is strong (no struggling on any practiced concepts)

## Framing Language

**Do say:**
- "Tell me about..." / "How would you say..." / "Let's talk about..."
- "I want to make sure we're building on the right foundation"
- "Your [concept] is solid — nice work"
- "I noticed [concept] needs a bit more practice — totally normal, we'll work on it"

**Do NOT say:**
- "I'm testing your placement"
- "Let me check if you actually know this"
- "Your placement might have been wrong"
- "We need to go back to basics"

## Tool Introduction Schedule

Non-beginners who skip onboarding still need external tools introduced. Anki, Dreaming Spanish, and SpanishDict are set up in session 1 (see first-session.md Section 6). Introduce the remaining tools during the validation period:

- **Session 3:** Speechling — by now you've heard the learner in conversation and know their pronunciation gaps. Set up their account and assign a first exercise targeting a specific sound.
- **Session 3-4:** Graded reader — suggest one at the reading level established by the session 1 reading comprehension check.
- **Language Transfer:** Only introduce if validation reveals significant grammar foundation gaps. It's audio-based grammar instruction — a placed B+ learner with solid foundations doesn't need it.

## Weekly Review Interaction

If a validation session falls on the learner's weekly review day, both this guide and the weekly review guide will be loaded. To avoid redundancy:

- Integrate your 2-3 validation spot-checks into the Skill Map Audit step (step 4) of the weekly review rather than running them separately.
- This session still counts toward `placement_validation.sessions_completed`.
- Report validation findings so far as part of the Progress Summary (step 1).
