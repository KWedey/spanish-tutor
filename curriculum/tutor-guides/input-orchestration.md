# Input Orchestration Guide

Loaded when: Standard session (post-onboarding), alongside decision-engine.md. Governs input homework selection, comprehension debriefs, level calibration, and input-to-production feedback.

## Overview

Input (listening and reading) is a first-class instructional pathway, not just homework. The system selects level-appropriate resources, debriefs comprehension each session, tracks progression through 5 levels, and feeds observations back into the skill map.

**Key files:**
- `curriculum/listening-progression.yaml` — L1-L5 level definitions with sources and criteria
- `curriculum/reading-progression.yaml` — R1-R5 level definitions with sources and criteria
- `curriculum/media-bank.yaml` — resource catalog with `level_range` and `prescriptive_episodes`
- `state/resource-tracker.yaml` — per-resource engagement tracking
- `state/skill-map.yaml > receptive_skills` — current levels and evidence

## 1. Input Selection (During Homework Assignment)

Run this during the Checkout phase when assigning homework.

### Step 1 — Get current levels

Read `receptive_skills.listening.current_level` and `receptive_skills.reading.current_level` from skill-map.

### Step 2 — Filter resources

From `curriculum/media-bank.yaml`, select resources whose `level_range` includes the learner's current level or one level above (i+1). Apply:

- **Dialect preference:** Prefer resources matching `target_dialect` from learner-profile. Accept neutral-dialect resources.

- **Dialect re-filter (advisory at assignment time):** When the assigned resource's `dialect:` tag is `mixed`, `mixed_latin_american`, `mixed_with_spain`, or `neutral`, the resource may still contain dialect-specific forms that conflict with `target_dialect`. Issue an explicit advisory to the learner at assignment time using the matrix below — this re-filter runs AFTER the preference filter above, so it only fires when no better dialect match was available.

  | Learner `target_dialect` | Resource `dialect:` | Advisory the tutor gives at assignment |
  |--------------------------|---------------------|-----------------------------------------|
  | `es-AR` or `es-UY` (voseo expected) | `mixed`, `mixed_latin_american`, or `neutral` | "Heads up — this resource may use **tú** in places where you'd use **vos**. Note any **tú** forms you hear; we'll cover the voseo conversion." |
  | `es-AR` or `es-UY` | `peninsular` or `mixed_with_spain` | "Heads up — this resource uses **vosotros** (Spain's plural-you) and **tú**. Listen for what they say; you would use **vos** and **ustedes**." |
  | Any non-`es-ES` (Mexico, Colombia, Chile, etc.) | `peninsular` or `mixed_with_spain` | "Heads up — this resource uses **vosotros** (Spain's plural-you). You'll use **ustedes** instead. Notice **vosotros** when it appears." |
  | `es-ES` | `mixed_latin_american` or any es-LATAM-tagged | "Heads up — this resource uses **ustedes** for plural-you (not **vosotros**). The forms you'll hear are the Latin-American ones." |

  When the advisory fires, log it in the session log alongside the assignment: `dialect_advisory: voseo`, `dialect_advisory: vosotros`, or `dialect_advisory: voseo+vosotros` (the literal `+` is the enum value when both apply — see `schemas/session-log.schema.yaml`). This makes per-learner advisory frequency auditable — high frequency suggests the media-bank dialect coverage for that target is thin and should be expanded.

- **Topic alignment:** Score by overlap with the weekly narrow topic (direct match > adjacent > unrelated).

- **Freshness:** Check `resource-tracker.yaml` — prefer resources not assigned in the last 2 sessions. Avoid resources with `learner_engagement: reluctant`.

### Step 3 — Apply autonomy level

| Phase | Assignment Style | Example |
|-------|-----------------|---------|
| A–B | Prescriptive | "Watch Dreaming Spanish — 'Mi rutina diaria' (7 min). Listen twice: once for gist, once for new words." |
| C | Guided | "Choose one of these podcast episodes about [topic]: Españolistos, Hoy Hablamos, or Notes in Spanish Intermediate." |
| D | Autonomous | "Spend 20 minutes on L5 input of your choice. Tell me about it next session." |

### Step 4 — Calibrate to available time

Input homework must fit within the learner's `schedule.yaml.study_time_budget`. Across ALL homework (input + Anki + writing + any other assignments), the sum of `assignments[].estimated_minutes` must stay within `study_time_budget.daily_target` on a normal day and must never exceed `study_time_budget.daily_maximum + study_time_budget.today_stretch` — `scripts/check-session-log.py` enforces the maximum as a FAIL and the target as a WARN (see CLAUDE.md §Guardrails L179 for the canonical rule). In-session tutor Spanish narration counts toward LISTENING HOURS for receptive-skill tracking but NOT toward the homework budget. Input's share grows with phase:
- **Phase A:** Input is required from session 3 onward. Include a 3-5 min in-session "tutor speaks Spanish" segment where the tutor narrates or describes something in simple Spanish with context support (gestures described in brackets, cognates, visual descriptions). This counts toward listening hours. Outside of the in-session segment, most homework time goes to Anki and exercises
- **Phase B:** Input becomes a regular assignment, roughly equal with Anki and exercises
- **Phase C:** Input is the primary homework — Anki decreases as vocabulary self-sustains through exposure
- **Phase D:** Input dominates — Anki is maintenance only

Input homework, like every other assignment, lands in the per-session `assignments[]` list with its `estimated_minutes`; the enforcer sums ALL assignments — input can never silently blow past the shared budget. (LOAD-06 / D-09)

### Step 5 — Record assignment

In the session log `assignments` section, include:
- `type: listening` or `type: reading`
- `resource:` specific resource name
- `task:` specific instructions (what to listen for, how many passes)
- `estimated_minutes:` estimated duration (this is the schema field name; the homework-budget enforcer at `scripts/check-session-log.py` sums this field across all assignments — using any other name like `input_minutes` causes the input portion to be silently counted as 0)
- `narrow_topic_aligned:` true if aligned with weekly topic

## Section 2. Comprehension Debrief (During Review & Warm-up)

3-5 minutes. Conversational — not a quiz. Conducted increasingly in Spanish as phase advances.

### Flow

**a) What did you consume?**
Ask what they listened to or read since last session. Log: resource name, estimated duration, number of passes.

**b) Topic probe**
"¿De qué se trataba?" / "What was it about?"

Assess gist comprehension. If they can't summarize the general topic, the level may be too high.

**c) Detail probe**
Ask 1-2 follow-up questions natural to the content.

For resources with a `content_summary` in `media-bank.yaml > prescriptive_episodes`: load the summary before asking, so you can probe specific details (e.g., "You watched the one about daily routines — what was the first thing the speaker did in the morning?").

For resources without summaries: rely on the learner's depth-of-elaboration as the comprehension proxy. Can they go beyond a one-sentence summary? Can they describe specifics?

**d) Vocabulary extraction**
"¿Aprendiste alguna palabra nueva?" / "Pick up any new words?"

Record words/phrases they report. If the learner reports none at a level where they should be encountering unknowns:
- If level might be too low → consider level-up assessment
- If level is appropriate → they may not be noticing. Suggest active listening strategies: pause and repeat new words, keep a notepad while listening

**Note:** Most passive vocabulary acquisition is subconscious. The learner won't report most of what they absorbed. The real signal is comprehension quality at level, not word count.

**e) Difficulty self-report**
"¿Cómo te pareció el nivel?" / "How was the difficulty?"

Cross-reference against observed comprehension quality. If the learner says "fine" but couldn't summarize the content, the calibration is off — note in `learner_observations.calibration_note`.

### Recording

Write the debrief results to the session log's `input_reviewed` section:

```yaml
input_reviewed:
  - resource: "Dreaming Spanish - Beginner: Mi rutina"
    type: listening
    duration_minutes: 7
    passes: 2
    comprehension_assessment: main_ideas
    vocabulary_extracted: ["ducharse", "desayunar"]
    production_gaps_observed: ["cepillarse"]
    difficulty_self_report: just_right
    level_at_time: L2
```

### Reading Debrief — Variations

The flow above (a-e) applies to reading the same way it applies to listening, with five reading-specific deltas. Use this sub-section when the input under debrief was assigned from `prescriptive_episodes.reading` in `curriculum/media-bank.yaml`.

**a) What did you read?**
Ask which chapters / pages they covered. Log: resource title, `chapter_range` covered (vs assigned), and number of re-reads of any passages.

**b) Topic probe (chapter-anchored)**
"¿De qué trataba el capítulo?" / "What was this chapter about?"

Probe at chapter granularity, not whole-book. Reading is consumed in chunks — a learner who summarizes Chapter 3 of *El Principito* well but stalls on Chapter 4 needs a chapter-level signal, not "the book in general."

**c) Detail probe (from content_summary)**
The reading entries in `media-bank.yaml > prescriptive_episodes.reading` each carry a `content_summary` written for this debrief. Load it before the probe and ask 1-2 specific questions that the summary anticipates (e.g., for Cajas de Cartón Story 1: "What does the family pack their belongings in? Why?").

For entries that lack a content summary (rare — every entry in 07-01 has one), fall back to depth-of-elaboration as the comprehension proxy, same as listening.

**d) Vocabulary extraction (passive recognition first)**
Reading is the modality where passive vocabulary grows fastest. Ask: "¿Hubo palabras que te confundieron pero entendiste por el contexto?" / "Were there words that tripped you up but you figured out from context?"

These are the passive-vocab acquisitions. Record them; they belong in `passive_known` on the relevant cluster, not `active_known` (production-readiness is a separate signal).

If the entry is dialect-marked (e.g., Benedetti's voseo, Laforet's vosotros), explicitly ask which dialect-specific forms they noticed — this closes the loop with the assignment-time dialect advisory (Section 1 Step 2 re-filter) and feeds the L1-interference preempts (`curriculum/l1-interference.yaml` — see entries `voseo-tu-conversion`, `vosotros-ustedes-recognition`).

**e) Difficulty self-report (pace, not just gist)**
"¿El ritmo te pareció bien? ¿Tuviste que releer mucho?" / "How was the pace? Did you have to re-read often?"

Reading allows arbitrary slow-down, so the pure "could you understand it" signal is less informative than for listening. The right signal is whether the learner could maintain reading flow without dropping into translation. If they re-read every paragraph, the level is too high regardless of whether they eventually understood.

### Recording (reading)

The session-log shape is the same as listening, with `type: reading` and `chapter_range_covered` in place of `passes`. Use the same field names that already exist under `session-log.schema.yaml > input_reviewed`. The reading-specific fields below (`chapter_range_covered`, `passive_vocabulary_inferred`, `dialect_friction_noted`) are recorded as free-form prose inside the existing `notes:` field today — see the schema for the enforced field set.

## Section 3. Skipped Input Homework

- **Single skip:** No intervention. Life happens. Assign normally next session.
- **2 consecutive skips:** Reduce input assignment load — the time budget may be wrong. Do a brief in-session listening moment (2-3 min): describe a short scenario or play a brief segment, then discuss.
- **3+ skips:** Ask the learner what's getting in the way. The assignment format may need to change (different resource type, shorter segments, different time of day), not just the quantity. Adjust and re-engage.

## 4. Level Calibration

### Level-up assessment

All three must be met:
1. Comprehension debrief shows consistent target-quality performance for 2+ consecutive weeks
2. Learner self-reports "just right" or "too easy"
3. Minimum hours at current level reached (see progression YAML for thresholds)

Hour minimums prevent premature level-up from a few good sessions. But a learner consistently excelling before the hour target should not be held back — use judgment.

**Reduced L2 minimum:** The L2 minimum hours threshold is 10-15 hours (not 20). Count in-session tutor Spanish toward listening hours — the tutor's Spanish narration segments, Spanish-language instructions, and conversation practice all contribute to comprehensible input. The two-consecutive-weeks criterion and comprehension quality checks are the real advancement gates, not the hour count alone.

When leveling up:
1. Update `receptive_skills.[listening/reading].current_level` in skill-map
2. Record the level change in `level_up_evidence` with date and observation
3. Move the old level to `level_history` with `hours_spent`
4. Reset `hours_at_level` to 0
5. Update `resource-tracker.yaml > input_summary`

### Level-down assessment

Either trigger:
1. Comprehension debrief shows gist-only at a level targeting details, for 2+ sessions
2. Learner reports sustained struggle for 2+ sessions

**Before leveling down:** Try a different source at the same level first. If Dreaming Spanish Intermediate is too fast, try Españolistos or Hoy Hablamos (more scaffolding). Only level down if multiple sources at the level are too challenging.

Frame level-down positively: "Let's build more foundation at this level before jumping up."

## 5. State Updates

After each session, update:

| State File | What to Update |
|-----------|---------------|
| `resource-tracker.yaml` | Increment `hours_logged` and `sessions_completed` for debriefed resources. Update `comprehension_trend` (compare last 3-4 debriefs for this resource). Update `learner_engagement` based on how they talked about the resource. |
| `skill-map > receptive_skills` | Update `hours_at_level` and `hours_total` from debrief data. Update `comprehension_quality` to reflect most recent assessment. Add to `level_up_evidence` if relevant. |
| `skill-map > vocabulary_clusters` | Increment `passive_known` for clusters containing words extracted during debrief. Add confirmed production gaps to `weak_production` if the same word appears in `production_gaps_observed` across 2+ sessions. |

## 6. Passive Vocabulary Inference

Estimate passive vocabulary growth from comprehensible input: approximately +3-5 words per 10 minutes of comprehended input at the learner's current level. This supplements learner-reported vocabulary counts, which capture only consciously noticed words.

**Usage:**
- After each debrief, estimate passive vocabulary gain: `(duration_minutes / 10) * 4` (midpoint of 3-5 range) for input at the learner's level. Reduce to `* 2` for i+1 level input (harder material = less absorbed). Increase to `* 5` for i-1 level input (easier = more reinforcement).
- Add the estimate to `passive_known` for relevant vocabulary clusters. This is an approximation — the learner won't consciously know all these words, but they are building recognition.
- Do not use this estimate for production readiness. Only learner-demonstrated vocabulary (extracted during debrief or observed in conversation) counts toward `active_known` or `weak_production`.

## 6b. Receptive-Productive Gap Guidance

When receptive skills (listening/reading level) exceed productive skills (speaking/writing ability) by 1+ levels, this gap is an asset, not a problem. The learner understands more than they can produce — a natural and productive state.

**Leverage the gap:**
- Assign more input homework at the receptive level to widen exposure. The learner is primed to absorb vocabulary and structures they already comprehend passively.
- During production practice, draw on vocabulary and structures the learner has encountered in input. They will recognize these and produce them more readily than "cold" vocabulary.
- The gap typically narrows naturally as production catches up through conversation practice. If the gap exceeds 2 levels, increase conversation time and production-focused homework to accelerate the catch-up.

**Do not:** slow down input progression to wait for production to catch up. Receptive skills pulling ahead is the natural acquisition order and should be encouraged.

## 7. Input → Production Pipeline

When the decision engine selects vocabulary clusters for practice (Step 6b in decision-engine.md), boost clusters where passive input exposure has been logged:

- If `passive_known` has increased for a cluster in the last 2 sessions → the learner has encountered these words in input and is primed for production practice
- This creates a natural flow: input exposure → passive recognition → active production practice
- Don't introduce vocabulary "cold" — prefer clusters the learner has already encountered in context

This integration happens in the decision engine's vocabulary scoring, not in this guide. See decision-engine.md Step 6b.
