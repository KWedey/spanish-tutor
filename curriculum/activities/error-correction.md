# Error Correction

## Purpose

Guides the tutor on WHEN and HOW to correct errors — during activities, after them, and across
sessions. This is not an activity itself; it is the correction framework that applies across all
activities. The goal is to ensure errors are addressed in a way that promotes learning without
interrupting communication or making the learner feel surveilled.

## Core Principles

- **Never correct more than 3 errors per activity.** More than that is overwhelming and
  counterproductive. Select the most instructive errors, not the most numerous.
- **Never correct mid-conversation.** Note errors silently. Correct after the activity ends.
  Interrupting kills communication and teaches the learner to speak in short bursts to minimize
  risk.
- **Prioritize by learning value,** not by how wrong the error sounds to a native ear.
- **Genuine praise is not optional.** Every correction session should include at least one
  specific, accurate positive observation.

## Error Classification

Classify every error before deciding how to address it:

| Type | Definition | Response |
|------|-----------|---------|
| **Developmental** | Expected at this phase; the learner hasn't fully acquired this concept yet | Address if it's the session focus concept; otherwise defer |
| **L1 interference** | English habit causing the error; not a knowledge gap but a transfer habit | Preempt before the activity if predictable; address directly if it surfaces |
| **Fossilized** | Incorrect form that has been used so long it feels right to the learner | Requires dedicated effort — standard correction rarely works |
| **Slip** | Learner knows the correct form but didn't produce it | Brief reminder only; no extended correction needed |

Record the classification in session notes. This affects how the error is tracked and escalated.

## During-Activity Protocol

The tutor's role during free production (conversation, role-play, storytelling):

1. **Say nothing.** Let the learner finish their thought.
2. **Note the error silently.** Record: the error, what it should be, the classification.
3. **If meaning is completely blocked:** Use recasting only. Repeat the sentence correctly
   without labeling it as a correction. "Ah, sí — *saliste* tarde. ¿Y después?"
4. **Do not recast repeatedly.** One recast, then move on. If the learner doesn't notice and
   correct themselves, it goes in the post-activity review.

**Recasting vs explicit correction:**
- **Recasting:** Tutor restates the correct form conversationally ("Saliste tarde —
  ¿y después?"). The learner may or may not notice. No disruption to communication.
- **Explicit correction:** Tutor pauses the flow and directly addresses the error ("Espera —
  it should be 'saliste,' not 'saliste.' " — or more gently: "Eso se dice 'saliste.' ").
  Reserve for Phase A-B or when the error is so persistent that recasting hasn't worked.

In Phase C-D: recast almost exclusively. In Phase A: explicit correction is acceptable for
high-priority errors (current focus concept, meaning-blocking errors).

## Post-Activity Review

After every conversation, role-play, or storytelling activity:

1. End the activity clearly: "Okay, let's talk about what came up."
2. Start with a genuine specific positive: "Your imperfect use for background description
   was really consistent today — that's a real improvement."
3. Present corrections one at a time. For each:
   - State what was said.
   - State what it should be.
   - Explain WHY briefly (1 sentence).
   - Ask the learner to produce the correct form once.
4. Maximum 3 corrections. Stop there even if you logged more.
5. The remaining errors go into session notes and inform future drills.

## Priority Order

When you have more than 3 errors logged, select by this priority:

1. **Current session focus concept** — always first if an error occurred.
2. **Meaning-impeding errors** — the listener couldn't understand what was meant.
3. **High-frequency errors** — patterns that recur across many sentences.
4. **L1 interference errors** — specifically when this is an expected transfer habit that needs
   active intervention.
5. **Fossilized risk patterns** — errors that have appeared across multiple sessions without
   improvement (see Escalation Protocol below).

Defer: accent mark errors in speech, very minor word-choice issues, stylistic preferences.

## Escalation Protocol

| Threshold | Action |
|-----------|--------|
| Same error in 3+ sessions | Change approach. If explicit correction hasn't worked, try recasting. If recasting hasn't worked, try a dedicated 5-minute drill. Try a different context that elicits the same structure. |
| Same error in 5+ sessions | Log as **fossilized risk** in the skill map. Note in `system-health.yaml`. Escalate to a sustained multi-session campaign: dedicated drills, flagging the error every time it occurs (even mid-conversation, gently), explicit discussion of WHY this form is wrong. |
| Same error in 8+ sessions with no improvement | The error is likely fossilized. Inform the learner directly and honestly. Adjust expected acquisition timeline. Consult `curriculum/tutor-guides/l1-interference-protocol.md`. |

Update the skill map when escalating:

```yaml
grammar_concepts:
  - id: "A-02-ser-vs-estar"
    status: practicing
    error_trend: stable
    persistent_errors:
      - pattern: "uses estar for permanent characteristics"
        first_observed: "2025-11-10"
        session_count: 5
        classification: L1-interference
        action: "escalated — started dedicated drill cycle"
```

## Handling Learner Reactions

- **Learner gets frustrated at corrections:** Reduce correction frequency immediately. For the
  next 1-2 sessions, correct only meaning-blocking errors. Then gradually re-introduce. Say:
  "We'll slow down on corrections for a bit. The goal right now is just to keep talking."
- **Learner asks to be corrected more:** Accept it, but still hold to the 3-error limit per
  activity. More than 3 overwhelms even when the learner requests it. Say: "I'll flag more for
  you — and I'll tell you the category each time so you can recognize the pattern."
- **Learner self-corrects before feedback:** Always acknowledge this. "Yes — you caught that.
  Good monitor awareness." Self-correction is a sign of progress. Do not still correct it.
- **Learner keeps making the same error after correction:** Log it. Do not correct the same
  error more than twice in one session. After the second correction, let it go for today. Return
  to it next session with a different approach.
