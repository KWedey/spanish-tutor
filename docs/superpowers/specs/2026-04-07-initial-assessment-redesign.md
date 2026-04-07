# Initial Assessment & Placement Validation Redesign

## Problem

The current initial assessment protocol has three gaps:

1. **Accuracy for non-beginners** — 3 conversational prompts are too coarse, risking misplacement when prior Spanish experience is claimed. The higher someone places, the more concepts get auto-marked "acquired" with less evidence, and the harder it is to recover.
2. **Missing dimensions** — The protocol only tests grammar production. Vocabulary breadth, receptive skills, and self-assessment calibration are not assessed, leaving the skill-map partially populated from inference rather than observation.
3. **No recovery mechanism** — There is no structured way to detect and correct a bad placement in the sessions immediately following assessment. The system assumes placement is correct and proceeds accordingly.

## Design Principles

- **Assessment investment should be proportional to placement risk.** True beginners need no assessment (onboarding self-corrects over 10 sessions). Non-beginners who skip onboarding need more scrutiny because assumed mastery is harder to walk back.
- **Assessment is woven into practice, not front-loaded as testing.** This aligns with the existing system design principle. The session 1 assessment stays lightweight; the real validation happens through teaching.
- **Place generously, validate through practice, correct gradually.** The system always places at the assessed level. Corrections happen through the validation protocol, not by second-guessing the initial placement.
- **The learner should never feel tested.** All assessment and validation is embedded in natural conversation and warm-up activities.

## Design

### 1. Enhanced Session 1 Assessment

Assessment only runs if the learner reports prior Spanish experience during goals/experience discovery. True beginners skip straight to first assignment — no assessment needed.

#### Self-Assessment Calibration

Before the grammar prompts, ask one question: "Before we try some Spanish — how would you rate your level? Beginner, intermediate, advanced?"

This populates the `calibration` fields in learner-profile.yaml by comparing self-report to actual performance (see Calibration Initialization below). The signal is used throughout the program to weight future self-reports ("that felt easy" / "I'm struggling").

#### Grammar Production — 3 Graded Prompts

Same prompts as current protocol, with more granular scoring:

| Prompt | Can't attempt | Fragments / heavy errors | Gets point across with errors | Mostly correct, minor errors |
|--------|--------------|------------------------|-------------------------------|------------------------------|
| "Introduce yourself" | Pre-A | Early A | Late A | Acquired A-01 |
| "Tell me about yesterday" | Below B | Early B (knows some forms, can't sustain) | Mid B (past tense functional but messy) | Acquired B-01–B-04 |
| "What would you do if..." | Below C | Early C (recognizes the structure, can't produce) | Mid C (attempts with errors) | Acquired through C |

The two new middle columns distinguish "has seen this" from "can use this" — a distinction the current binary scoring collapses.

#### Embedded Vocabulary Observation (No Extra Time)

No standalone vocabulary prompt. The tutor actively notes vocabulary signals during the grammar prompts:

- **Introduce yourself:** Do they name their job, city, hobbies? Do they use "me llamo" (formulaic) vs constructing sentences with adjectives? How many domains can they touch — just name and origin, or family, work, interests?
- **Tell me about yesterday:** What verbs do they reach for — just "fui" and "comí," or a range? Can they name times, places, activities? Do they circumlocute when stuck, or just stop?
- **What would you do if:** Can they express abstract ideas — wishes, reasons, opinions? Or only concrete nouns?

After the grammar prompts, one natural follow-up draws out more signal: take something the learner mentioned and ask them to expand. "You mentioned you like cooking — tell me more about that in Spanish. Use English for any words you don't know." The English fallback words reveal the vocabulary ceiling precisely, and it feels like conversation, not a test.

The tutor logs a vocabulary observation at one of four qualitative levels:

| Observation | Level |
|-------------|-------|
| Only formulaic phrases (me llamo, buenos días) | Minimal |
| Functional within 1-2 familiar topics | Narrow |
| Can discuss varied topics, reaches for specific words | Broad |
| Uses nuanced vocabulary, near-synonyms, low-frequency words | Deep |

Additionally logged:
- **Domains demonstrated:** which topic areas they showed vocabulary in
- **Production gap indicators:** topics where they understood the concept but lacked the Spanish word (used English, circumlocuted, or gestured at the idea)

#### Reading Comprehension Check (~2 min)

Framed honestly as reading, not listening. After the grammar prompts, the tutor transitions: "Let me try something — I'm going to write you a short passage in Spanish. Don't worry about responding in Spanish, just tell me what it says."

The passage is calibrated one half-step above the learner's demonstrated production level:

- **Placed at A:** 2-3 simple sentences using present tense with some unfamiliar vocabulary
- **Placed at B:** A short paragraph mixing past tenses, some B-level structures they didn't produce
- **Placed at C+:** A passage with subjunctive, conditional, or compound tenses

Scoring:

| Comprehension | Signal |
|--------------|--------|
| Gets the gist, misses details | Reception ≈ production (typical) |
| Understands nearly everything | Reception ahead of production — assign ambitious reading/listening homework from day 1 |
| Understands less than expected | Possible over-placement on grammar prompts — flag for heavier validation |

**What this does not test:** Listening comprehension. That is deferred to homework — the first Dreaming Spanish assignment goes out in session 1, and the tutor reviews what they could follow at the start of session 2. This becomes the listening baseline.

### 2. Placement Mapping & Skill-Map Pre-Population

#### Placement Level Determination

Grammar production is the primary signal — it determines the phase. Vocabulary and reading are secondary signals that inform validation priority and vocabulary pre-population, but do not override grammar-based phase placement.

| Grammar result | Secondary signals | Placement | Confidence |
|---|---|---|---|
| Can't attempt prompt 1 | (skipped) | True beginner — enter onboarding | N/A |
| Early A | Any | Early A — onboarding from session 2 | N/A (onboarding calibrates) |
| Late A | Any | Late A — onboarding from session 5 | N/A (onboarding calibrates) |
| Early B+ | Vocab Broad/Deep, reading at or above | Phase as assessed | High |
| Early B+ | Vocab Narrow, reading at expected | Phase as assessed | Medium |
| Early B+ | Vocab Minimal, or reading below expected | Phase as assessed | Low — front-load validation |

Confidence determines how aggressively the validation protocol probes in sessions 2-4. It does not change the placement itself.

#### Grammar Concept Pre-Population

**Below placement level:** Always `acquired` with `performance_unscaffolded: competent`. The inference "they produce above this level, therefore they've acquired this" is strong for grammar due to its hierarchical nature. If the inference is wrong, the validation protocol catches it.

**At placement level:**
- Concepts the learner directly demonstrated (even with errors) → `practicing`, error rates estimated from the sample
- Concepts at the same phase level but not directly demonstrated → `practicing`, error rates `null`. This signals "needs assessment, not introduction." The tutor won't re-teach from Stage 1, but will probe these early.

**Above placement level:** `unseen`. No change.

**Guardrail exception:** The acquisition guardrail ("never mark acquired unless practiced in 3+ separate sessions") is inherently violated by placement pre-population. Placement-acquired concepts are exempt from the session count requirement. The validation protocol serves as the verification mechanism in lieu of 3 sessions of observed practice.

#### Vocabulary Cluster Pre-Population

Vocabulary is domain-specific — knowing food words says nothing about direction words. Grammar-to-vocabulary inference is weaker than grammar-to-grammar, so the vocabulary observation carries more weight.

| Vocab observation | Clusters below placement | Clusters at placement |
|---|---|---|
| Minimal | Demonstrated → `acquired`, undemonstrated → `practicing` | `unseen` |
| Narrow | Demonstrated → `acquired`, undemonstrated → `acquired` | Demonstrated → `practicing`, undemonstrated → `unseen` |
| Broad / Deep | `acquired` | `practicing` |

**Concurrent concept gate interaction:** If the Minimal observation at B+ placement creates more than 2-3 vocabulary clusters in "practicing," limit vocabulary pre-population to the 2-3 clusters most likely to be weakest (based on what topics the learner avoided) and leave the rest as `acquired`. This keeps the decision engine unblocked while surfacing the most likely gaps.

#### Receptive Skills Initialization

| Reading check result | `receptive_skills.reading` |
|---|---|
| Understands less than expected | current_level: one sub-level below grammar placement (e.g., Early B → Late A) |
| Gets the gist | current_level: matches grammar placement |
| Understands nearly everything | current_level: one sub-level above grammar placement |

`receptive_skills.listening`: null until session 2 Dreaming Spanish review establishes baseline.

#### Calibration Initialization

| Self-report vs actual | `calibration` fields |
|---|---|
| Matches | self_report_accuracy: `reliable`, tendency: `accurate`, trust_weight: 0.7 |
| Self-report higher | self_report_accuracy: `unreliable`, tendency: `over-estimates`, trust_weight: 0.3 |
| Self-report lower | self_report_accuracy: `unreliable`, tendency: `under-estimates`, trust_weight: 0.5 |

Under-estimators get higher trust weight than over-estimators — "I'm worse than I think" is less dangerous for placement decisions than "I'm better than I think." These are initial values; the validation period and ongoing sessions refine them.

### 3. Placement Validation Protocol

The core new mechanism. Runs for learners who skip onboarding (Early B+ placement) and confirms or corrects placement through real practice.

#### Activation & Duration

- **Activates** when `onboarding_complete: true` was set during placement (Early B+)
- Learners placed at Early A or Late A enter onboarding, which calibrates naturally. No validation needed.
- **Duration:** Sessions 2-4 (3 teaching sessions). Can close early after session 3 if confidence is high. Extends if sessions are missed — requires 3 actual sessions, not 3 calendar days. Maximum extension to session 5 if validation period performance is mixed.

#### Validation Queue

Populated during session 1 state initialization. Stored in `schedule.yaml` under `placement_validation.queue`. Ordered by priority:

1. **Highest-level acquired concepts first (top-down strategy).** Grammar is hierarchical — if B-04 (preterite vs imperfect) is solid, B-01/B-02/B-03 are almost certainly solid too. Testing the peak validates the foundation beneath it. A failing check at the peak tells you where to dig deeper.
2. Prerequisites for the learner's current work (if A-01 is wrong, everything downstream is wrong)
3. Concepts marked `practicing` with null error rates (undemonstrated — never directly observed)
4. Remaining acquired concepts, low confidence first

Priority is further weighted by placement confidence:
- **Low confidence:** More concepts queued, front-loaded into session 2
- **Medium confidence:** Standard queue, spread across sessions 2-4
- **High confidence:** Lighter queue, mostly sessions 3-4

#### Spot-Check Methodology

2-3 concepts validated per session. The tutor selects warm-up topics, conversation prompts, and homework review questions that naturally elicit the target structures:

| Concept to validate | Natural elicitation |
|---|---|
| A-02 ser vs estar | "How are you feeling today? Tell me about your house." |
| B-01 preterite | "What did you do this weekend?" |
| B-04 preterite vs imperfect | "Tell me about a trip you took — what was happening, what happened." |
| B-05 reflexive verbs | "Walk me through your morning routine." |
| B-06 direct object pronouns | "Did you finish the homework? When did you start it?" |

The learner experiences this as "my tutor is getting to know me," not "my tutor is testing me." No explicit framing.

#### Scoring

| Observation | Result | Action |
|---|---|---|
| Uses concept correctly and naturally | Validated | Stays `acquired`, remove from queue |
| Minor errors (1-2 per exchange) | Validated with note | Stays `acquired`, add maintenance note to skill-map |
| Significant errors, struggles to produce | Downgrade | → `practicing`, set error rates from observed performance |
| Can't produce or avoids entirely | Downgrade | → `introduced`, flag for Stage 1-2 work |
| Concept not naturally elicited | Inconclusive | Remains in queue for next session |

#### Downgrade Pacing

Maximum 2 concept downgrades per session. If more concepts fail in a single session, validate and record all failures but defer remaining downgrades to the next session. Deferred downgrades are marked `pending_downgrade` in the queue — the tutor does not re-validate them, just processes the status change.

Rationale: each downgrade adds to the "practicing" count, interacting with the concurrent concept cap. Spreading corrections keeps the decision engine functional.

#### Widespread Gap Handling

If 4+ total downgrades occur across the validation period, this signals meaningful misplacement. The tutor does NOT reroute to onboarding, but:

- Logs `placement_adjustment: significant` in the session file
- Reduces `max_new_concepts_per_week` to 1 in schedule.yaml (consolidation-heavy mode)
- Notes in system-health.yaml for trend tracking
- Frames it to the learner: "You've got a solid foundation — there are just some spots I want to make sure are rock solid before we build on them."

The decision engine's existing mechanics handle recovery:
- The 3-concept concurrent cap prevents overwhelm
- Prerequisite gating forces the right order
- NEED=10 for prerequisites means foundations are prioritized first
- The learner experiences consolidation-heavy sessions, not a dramatic course correction

#### Listening Baseline (Session 2)

- Review the Dreaming Spanish assignment from session 1
- "What level did you watch? How much did you follow?"
- Sets `receptive_skills.listening.current_level`
- Cross-reference with `calibration.tendency` — if learner over-estimates, probe: "What was the video about? Can you tell me what happened?"

#### Closing the Validation Period

After session 4 (or session 3 for early close):

- Concepts still in queue not yet spot-checked: accept current status if overall performance is consistent. If mixed, extend to session 5.
- Remove active queue from schedule.yaml
- Set `placement_validation.active: false`, `placement_validation.confidence: validated`
- Log validation summary in session file: concepts checked, pass/downgrade counts, final assessment
- Update system-health.yaml with validation metrics

#### Scope Boundaries

The validation protocol does NOT handle:
- **Later regression** on validated concepts — that's the decision engine's normal regression detection
- **Vocabulary cluster validation** — gaps surface naturally through conversation; no structured spot-check protocol
- **Pronunciation assessment** — deferred to Speechling introduction (sessions 3-4 for placement-skip learners)

### 4. Schema Changes

#### `schedule.yaml` — New `placement_validation` Block

```yaml
placement_validation:
  active: false
  confidence: null          # high / medium / low / validated
  sessions_completed: 0
  listening_baseline_set: false
  total_downgrades: 0
  queue:
    - concept_id: ""
      priority: 1
      status: pending       # pending / checked-pass / checked-fail / pending_downgrade
      checked_in_session: null
      notes: ""
```

#### `learner-profile.yaml` — New `initial_placement` Block

```yaml
initial_placement:
  level: ""                 # pre-A / early-A / late-A / early-B / mid-B / early-C / mid-C
  date: null
  self_report: ""           # beginner / intermediate / advanced
  grammar_result: ""
  vocabulary_observation: "" # minimal / narrow / broad / deep
  reading_result: ""        # below-expected / at-expected / above-expected
  confidence: ""            # high / medium / low
  evidence_summary: ""
```

#### Session Log — Assessment Fields (Session 1)

```yaml
assessment:
  self_report: ""
  grammar_prompts:
    introduce_yourself:
      response_summary: ""
      scoring: ""           # pre-A / early-A / late-A / acquired-A-01
    tell_about_yesterday:
      response_summary: ""
      scoring: ""
    what_would_you_do:
      response_summary: ""
      scoring: ""
  vocabulary_observation:
    level: ""               # minimal / narrow / broad / deep
    domains_demonstrated: []
    production_gap_indicators: []
    follow_up_topic: ""
    follow_up_notes: ""
  reading_check:
    passage_level: ""
    comprehension: ""       # below-expected / gets-the-gist / understands-nearly-all
  placement_decision:
    level: ""
    confidence: ""
    rationale: ""
```

#### Session Log — Validation Fields (Sessions 2-4)

```yaml
validation_checks:
  - concept_id: ""
    elicitation: ""
    observation: ""
    result: ""              # checked-pass / checked-fail
    action: ""              # validated / downgrade-to-practicing / downgrade-to-introduced
    error_rate_estimate: null
```

#### `system-health.yaml` — New `placement_validation_metrics` Block

```yaml
placement_validation_metrics:
  placement_level: null
  initial_confidence: null
  total_concepts_validated: 0
  total_downgrades: 0
  final_assessment: null    # placement-confirmed / placement-adjusted
  validation_completed: null
```

#### Decision Engine — New GAP Table Row

Add to the GAP scoring table in `curriculum/tutor-guides/decision-engine.md`:

| State | Score |
|-------|-------|
| Practicing, error rate null (unassessed) | 7 |

This ensures unassessed concepts (pre-populated at placement level with null error rates) are prioritized for early practice, which both teaches and assesses them.

### 5. File Changes Summary

#### Modified Files

| File | Change |
|------|--------|
| `curriculum/tutor-guides/first-session.md` | Replace Experience Assessment section with enhanced protocol. Replace Placement Protocol with refined scoring. Replace skill-map pre-population rules. Add validation queue initialization to State Initialization. Update onboarding skip rules. |
| `curriculum/tutor-guides/decision-engine.md` | Add GAP table row for null error rates (score 7). |
| `state/schedule.yaml` | Add `placement_validation` block to schema with default values. |
| `state/learner-profile.yaml` | Add `initial_placement` block to schema with empty defaults. |
| `state/system-health.yaml` | Add `placement_validation_metrics` block with null/zero defaults. |
| `docs/system-design.md` | Update session log schema with assessment and validation_checks fields. Add placement_validation to schedule schema. Add initial_placement to learner-profile schema. Add placement_validation_metrics to system-health schema. |
| `CLAUDE.md` | Add Step 4 conditional load: when `placement_validation.active` is true and `sessions_completed < 3`, also load `curriculum/tutor-guides/placement-validation.md`. Add guardrail exception for placement-acquired concepts. |

#### New Files

| File | Purpose |
|------|---------|
| `curriculum/tutor-guides/placement-validation.md` | Tutor guide loaded during validation period. Contains spot-check methodology, elicitation examples, scoring rubric, downgrade rules and pacing, listening baseline protocol, validation close-out procedure, and learner-facing framing language. |
