# Decision Engine Guide

Loaded when: Standard session (post-onboarding). Used to select today's focus concepts and route to appropriate activities.

> **Machine-readable form:** the scoring weights, gates, and escalation ladders in this guide are mirrored in `curriculum/decision-weights.yaml` (the score/select/gate engine contracts) — tune the numbers there and keep this guide's tables in sync.

## Step 0b — Carryover Escalation Check

Run at session start for each concept in `schedule.yaml > carryover_concepts`. Check `sessions_in_carryover` against the escalation ladder.

### Prerequisite Carryover (is_prerequisite: true)

| Sessions | Stage | Action |
|----------|-------|--------|
| 1-5 | normal | Normal carryover allocation. No special treatment. |
| 6 | flagged | Flag in system-health. Review error patterns: same mistake repeating → explanation isn't landing. Varied errors → insufficient practice volume. |
| 8 | approach_changed | Try a different instructional approach. If rule-based before, try example-based. If drills, try communicative. If always same context, try new context. Update `current_approach` in schedule. |
| 10 | sprint | Auto-trigger a 2-session mini-sprint on this concept. Log sprint rationale in adjustment_log. |
| 12+ | surfaced | Surface to learner: "This concept is taking longer than expected. That's normal — [concept] is genuinely hard for English speakers. Let's talk about what's not clicking." Use learner input to redesign approach. |

### Non-Prerequisite Carryover (is_prerequisite: false)

| Sessions | Stage | Action |
|----------|-------|--------|
| 1-8 | normal | Normal allocation. |
| 9 | flagged | Flag in system-health. Review error patterns. |
| 12 | approach_changed | Try different approach. |
| 15 | sprint or deprioritize | If learner is progressing well on prerequisites, deprioritization is valid. Otherwise, mini-sprint. |
| 18+ | surfaced | Surface to learner. |

**Key principle:** Each escalation step changes the approach, not just the intensity. Repeating the same thing harder doesn't fix a stall.

**Integration with interleaving:** Stalled carryover concepts should be prioritized as interleaving targets in Step 5b. Practicing them woven into other activities (rather than in isolation) may help with transfer.

After checking, increment `sessions_in_carryover` for each carryover concept that was practiced this session. Update `escalation_stage` if a threshold was crossed.

## Step 0c — Regression Escalation Check

Run at session start for each concept whose status transitioned from `acquired` or `automatic` back to `practicing` or `regressed` within the last session. Check `regression_session_count` against the ladder.

### Prerequisite Regression (is_prerequisite: true)

| Sessions in regression | Stage | Action |
|----|----|----|
| 1 | normal | Log. Targeted re-practice in next session's Main Lesson. |
| 2 | flagged | Flag in system-health. Read `recast_uptake_stats`. If `recasts_given >= 5` and uptake rate < 60%, suspect mode mismatch. Read `error_trend` for pattern. |
| 3 | approach_changed | **Mandatory approach switch.** Read `recast_uptake_stats`: **low uptake** (recasts_given >= 5, landed/given < 0.60) -> escalate correction MODE (recast -> explicit -> metalinguistic per error-correction.md Metalinguistic Feedback Protocol). **High uptake but re-erring** (landed/given >= 0.60) -> change CONTEXT or MODALITY (written <-> spoken; isolated drill <-> integrated conversation). **Insufficient data** (recasts_given < 5) -> default to context/modality change. Update `current_approach` in skill-map notes. |
| 4 | sprint | Auto-trigger a single-session dedicated re-teach plus one week of daily micro-drills. Log sprint rationale in `adjustment_log`. |
| 5+ | surfaced | Surface to learner warmly: "[Concept] has slipped back -- it happens. Let's talk about what changed." Use learner input to redesign. Log as fossilized risk if 3+ cycles of re-acquisition have failed. |

### Non-Prerequisite Regression (is_prerequisite: false)

| Sessions in regression | Stage | Action |
|----|----|----|
| 1-2 | normal | Log. Targeted re-practice. |
| 3 | flagged | Flag in system-health. Review error patterns. |
| 5 | approach_changed | Same approach-switch logic as prerequisite stage 3. |
| 7 | sprint_or_deprioritize | If the concept is low-value for current goals, deprioritize (move out of active list) with a note. Otherwise sprint. |
| 9+ | surfaced | Surface to learner. |

**Key principle:** Each escalation step changes the approach, not just the intensity. Repeating the same thing harder does not fix a regression -- the Han (2004) fossilization research is explicit about this. The `approach_changed` stage reads `recast_uptake_stats` (from skill-map, aggregated by post-session.sh) to choose the switch, making "change approach" an auditable data-driven decision rather than a vague instruction.

**Data-insufficiency fallback:** When `recast_uptake_stats.recasts_given < 5`, there is not enough data to determine uptake rate. In this case, the approach switch defaults to "change context/modality" rather than "escalate mode" -- this is a safe fallback that does not require uptake data.

**Cross-link:** `curriculum/activities/error-correction.md` Escalation Protocol (3/5/8 sessions -> change approach / fossilized risk / directly inform) is the EXECUTION side of regression handling -- what to do mid-activity. This ladder is the DECISION side -- concept selection and scoring. Both can fire simultaneously on the same concept without conflict.

After checking, update `escalation_stage` if a threshold was crossed. (`regression_session_count` itself is maintained automatically by `post-session.sh` Step 5d — `scripts/recompute-metrics.py` increments it for each `regressed` concept and resets it to 0 on re-acquisition — so do NOT hand-edit it here; just read it.)

## Step 1 — Gather Candidates

All concepts in current phase with status: introduced, practicing, regressed, or acquired (for maintenance). Plus `carryover_concepts` from `schedule.yaml`. Plus maintenance from all previous phases (with decaying priority).

**Cultural concepts:** Also gather `cultural_awareness` concepts from skill-map whose `introduced_at_phase` matches the current phase or earlier. Score them using the same formula but with NEED capped at 5 for non-functional cultural concepts (`regional_awareness`, `humor_and_idioms`). Functional cultural concepts (`politeness_formulas`, `register_shifting`) use their full NEED score — see the NEED table for details. Cultural concepts are never the primary focus — they supplement grammar work during conversation practice or as a secondary concept.

**Filter:** Exclude any concept where prerequisites are not met. A prerequisite is "met" when its status is "acquired" or "automatic". Status "practicing" or below means the prerequisite is not met and the dependent concept cannot be introduced.

## Step 2 — Score Each Candidate

```
PRIORITY = NEED + GAP + DECAY_ADJUSTED + TOPIC_BOOST + INTEREST - VARIETY_PENALTY
```

> `DECAY_ADJUSTED` accounts for concept durability — see DECAY section below for the formula.

### NEED (0-10)

| Concept type | Score |
|-------------|-------|
| Phase prerequisite (unlocks most concepts) | 10 |
| Current phase concept | 7 |
| Carryover concept from prior phase | 5 |
| Current phase maintenance | 2 |
| Previous phase maintenance | 1 |
| Two+ phases back maintenance | 0.5 |
| Cultural concept (any phase) | See note below |

> **Note:** Cultural concepts use the same base scoring as grammar concepts of their type, but the NEED score is capped at 5 for non-functional cultural concepts (`regional_awareness`, `humor_and_idioms`). **Exception:** `politeness_formulas` and `register_shifting` are functionally equivalent to grammar for communication — they use their full base NEED score with no cap. These concepts directly affect whether the learner can communicate appropriately and should compete on equal footing with grammar.

### GAP (0-10) — uses `error_rate_production`

| State | Score |
|-------|-------|
| Regressed | 10 |
| Practicing, production error >30% | 8 |
| Practicing, drill/production mismatch (transfer gap) | 7 |
| Practicing, error rate null (unassessed) | 7 |
| Practicing, production error 15-30% | 5 |
| Practicing, production error <15% | 3 |
| Acquired, not integration-tested | 2 |
| Acquired + integration-tested | 0 |

**Minimum observation count:** Error rates require a minimum of 8-10 observations per context (drill, production) before they can be used for advancement decisions. Below this threshold, the error rate is unreliable — rely on qualitative assessment (`performance_scaffolded` / `performance_unscaffolded`) instead and require an additional session of observation before advancing. When observation count is below threshold, use the qualitative field to estimate GAP: `struggling` = treat as >30%, `developing` = treat as 15-30%, `competent` = treat as <15%.

**Error trend minimum data:** Do not compute `error_trend` (improving, stable, declining) until 5+ sessions of data exist for a concept. Below that threshold, report `error_trend: insufficient_data` in the skill map. Computing a trend from 2-3 data points produces misleading signals that can cause premature advancement or unnecessary intervention.

**Recency weighting for error rates:** Observations are not equally reliable over time. Apply confidence weighting:
- **Within 7 days:** Full confidence. Use error rates as-is for scoring and advancement.
- **8-30 days ago:** Moderate confidence. Error rates inform scoring but should not be the sole basis for advancement decisions. Supplement with a spot-check if advancing.
- **31-60 days ago:** Low confidence. Error rates are stale — re-verify with at least one production observation before using for any advancement decision. If the concept hasn't been practiced in 31+ days, the DECAY score already captures urgency; don't also trust the old error rate for status changes.

### Vocabulary GAP Scoring

Vocabulary clusters with `error_tracking` data are now scored using the same GAP formula as grammar:

| State | Score |
|-------|-------|
| error_rate_production > 0.30 | 8 |
| error_rate_production 0.15-0.30 | 5 |
| error_rate_production < 0.15 | 3 |
| error_rate_production null (unobserved) | 4 |
| No error_tracking data and last_observed null | 2 |

**Weight vocabulary GAP below grammar GAP** — vocabulary production errors are observed less frequently (incidentally during conversation, not in dedicated drills). Specific weight ratio should be tuned after 20+ sessions of real data. Until then, treat vocabulary GAP as roughly 70% of equivalent grammar GAP when comparing cross-category candidates.

Vocabulary clusters where `passive_known` has increased in the last 2 sessions (input exposure logged) receive a +2 TOPIC_BOOST — the learner has encountered these words in context and is primed for production.

### DECAY (0-10)

| Days since last practiced | Score |
|--------------------------|-------|
| 0-1 | 0 |
| 2-3 | 2 |
| 4-7 | 5 |
| 8-14 | 7 |
| 15+ | 9 |

**Durability adjustment:** Well-practiced concepts are more resistant to decay. After computing the raw DECAY score, apply:

```
DECAY_ADJUSTED = DECAY * (1 - min(practice_count / 20, 0.7))
```

A concept practiced 20+ times gets only 30% of the raw decay score. A concept practiced 10 times gets 50%. A concept practiced only twice gets 90%. Use `DECAY_ADJUSTED` in the final PRIORITY formula instead of raw DECAY.

### TOPIC_BOOST (0-3)

| Alignment with weekly narrow topic | Score |
|------------------------------------|-------|
| Direct match (topic naturally elicits this concept) | 3 |
| Adjacent (topic uses related vocabulary) | 1 |
| No connection | 0 |

### INTEREST (0-3)

Tutor-inferred learner interest in this concept. Captured post-session from four signal sources. Missing or stale (> 28 days since last inferred) = 0.

| Signal strength | Score |
|----------------|-------|
| Learner asked about it unprompted, referenced it in a real-world debrief, or wrote about it in journal within the last 2 sessions | 3 |
| Concept aligns with a recent parking-lot item or topic the learner showed enthusiasm for in the last 2 weeks | 2 |
| No explicit signal but concept sits in a topical cluster the learner has engaged with | 1 |
| No signal, OR last inferred > 28 days ago (stale decay) | 0 |

**Signal sources:** `parking-lot.md` mentions, session-log `learner_observations` engagement notes, real-world debrief outputs (from `real-world-debrief.md`), journal entries referencing the concept.

**Stale decay:** If `learner_interest.last_inferred` is more than 28 days ago, the scoring engine treats the stored score as 0 regardless of the stored value. The next post-session update rewrites `signal_source: stale` with `score: 0`. This prevents a 6-month-old parking-lot item from influencing today's scoring.

**Storage:** Per-concept in `state/skill-map.yaml` as `learner_interest: {score, last_inferred, signal_source}`. Applies to grammar concepts, vocabulary clusters, and cultural concepts (per D-03).

**Cap:** Maximum contribution is 3. Cannot exceed. This is enforced by `validate-state.py` (score > 3 = FAIL). The additive cap ensures a regressed concept (NEED 10 + GAP 10 = 20 baseline) always beats a maximally interesting but non-regressed concept (NEED 7 + GAP 3 + INTEREST 3 = 13). Interest guides the engine toward what the learner cares about; it does not override repair priority.

> Example: C-03 (subjunctive) — learner asked about it unprompted last session and wrote about it in their journal → `INTEREST=3`.

### VARIETY_PENALTY (0-5)

Same activity type 3 days in a row → penalize that type by 5. Prefer alternation.

## Step 3 — Apply Modifiers

- **Low energy:** Boost passive activities (listening/reading review), reduce production demands. Halve GAP score for challenging concepts.
- **Low motivation / at-risk:** Boost easy wins (high-confidence concepts), add novelty. Double NEED for fun/interesting concepts.
- **Parking lot items:** If a parking lot item aligns with a candidate concept, boost that concept by +3. If the item suggests a concept not in the candidate list but prerequisites are met, it can override secondary concept selection.
- **Sprint override:** If `sprint.active` is true, only score concepts in `sprint.focus_areas`. All others excluded.
- **Just-right streak preservation:** Track consecutive "just-right" `session_difficulty_rating` values across sessions. If the streak reaches 3+, preserve current calibration — do not increase or decrease challenge level. The current balance is working. Only break the streak intentionally (e.g., sprint mode activation, phase transition approaching, or learner explicitly requesting more challenge). Reset the counter when a "too-easy" or "too-hard" rating is logged. Record `just_right_streak` in `schedule.yaml`.
- **Stale interest decay:** When reading `learner_interest.score` for any concept, check `last_inferred`. If > 28 days ago, treat as 0. This applies automatically in Step 2 scoring — Step 3 does not need to override, but the decay is noted here for completeness.

## Step 4 — Select Top 1-2 Concepts

Highest score = primary focus. Second highest = secondary (if time allows and not same category). If top concept is grammar, prefer vocabulary or pronunciation as secondary (variety). Tie-break: prefer higher learner interest.

## Step 5 — Route to Activity

**Fluency days** (Phase A: none; 1x/week in Phase B; 2x/week in Phase C; up to 3x/week non-consecutive in Phase D — `route_session.py` is authoritative): Run Steps 1-4 normally to select concept(s). At Step 5, route to `fluency-activities.md` instead of the stage-based routing below. In Phase D, sessions that are NOT routed as dedicated fluency days still embed a fluency *component* per `fluency-activities.md` (Phase D), so fluency exposure is in every session even though dedicated fluency-day routing caps at 3/week.

**Non-fluency days** — check `error_rate_drills` and `error_rate_production`:

| Drills | Production | Route |
|--------|-----------|-------|
| Both high | → | Stage 2 (controlled practice from concept file) |
| Drills low, production high | → | Stage 3-4 (communicative practice) |
| Both low | → | Spot-check via conversation, move to secondary |
| Integration untested (check integration_tested_with for specific combinations) | → | Combined exercise with another acquired concept **not yet in** `integration_tested_with` list. After successful integration practice, append the tested combination to the list. |

**New concept introduction (concurrent concept gate):** Before scoring any unseen concept, count concepts currently in "practicing" status. If count ≥ 3 (or ≥ 4 with carryover), exclude all unseen concepts from candidates — consolidate first. Otherwise, route new concept to Stage 1 (noticing) from concept file.

## Step 5b — Select Interleaved Concepts

After selecting the primary concept and routing to an activity stage, select 1-3 prior concepts to weave into the practice activities. Interleaving exercises prior concepts organically during new learning — replacing separate review blocks.

### Selection

1. Query skill-map for eligible interleaving concepts: status `acquired` or `automatic`, OR status `practicing` with `performance_unscaffolded: competent` (concepts solid enough to weave in without derailing the primary). Note: there is no persisted per-concept activity "stage" in skill-map — the activity stage (1-4) is an ephemeral in-session routing artifact derived from error rates (Step 5), so interleaving eligibility is judged from the persisted `status` and `performance_unscaffolded` fields, not a stored stage.
2. Rank by DECAY score (highest = longest since practiced)
3. Prefer stalled carryover concepts (serves double duty as escalation — see Step 0b)
4. Select count based on primary concept's stage:

| Primary Concept Stage | Interleaved Count | Rule |
|----------------------|-------------------|------|
| Stage 1-2 (first session with concept) | 0-1 | At most 1 acquired concept. New concepts need focused attention. |
| Stage 2 (controlled practice, subsequent sessions) | 1 | 1 acquired concept embedded in drill sentences |
| Stage 3 (guided production) | 2 | 1 acquired + 1 practicing-but-competent (per `performance_unscaffolded`) woven into prompts |
| Stage 4 (integration) | 2-3 | Concepts across status levels combined in conversation |

### How to Interleave

Don't create separate review activities. Embed prior concepts in the primary concept's practice:

- **Stage 2 drills:** Write drill sentences that require both the primary concept and the interleaved concept. Example: preterite drills where sentences also require correct ser/estar.
- **Stage 3 prompts:** Design conversation prompts that naturally elicit both. Example: "Tell me about a trip you took" targets preterite but requires prepositions and object pronouns.
- **Stage 4 scenarios:** Create scenarios that demand the primary concept plus 2-3 others. Example: giving advice about a problem (conditional + subjunctive + opinion vocabulary).

### Guardrails

- Never interleave a concept the learner hasn't reached Stage 3+ on
- Never interleave more than 3 concepts in a single activity
- If the primary concept is brand new (Stage 1-2, first session), interleave at most 1 acquired concept
- **Interleaving-only trap:** If a concept has been interleaved (practiced as secondary) 5+ times but has not been the primary focus in the same period, elevate it to primary in the next session. Interleaving alone is insufficient for advancement — the concept needs dedicated primary attention to progress through stages.

### Recording

Log interleaved concepts in the session log:

```yaml
interleaved_concepts:
  - concept_id: A-02
    interleave_context: "embedded ser/estar usage in preterite drill sentences"
    errors_observed: 0
```

Reset the DECAY clock for interleaved concepts — they count as practiced.

## Step 6 — Weekly Topic Selection (during weekly review)

Score each candidate from `curriculum/topic-bank.yaml`:

| Factor | Range | Description |
|--------|-------|-------------|
| GRAMMAR_FIT | 0-5 | Does the topic naturally elicit the primary grammar concept? |
| VOCABULARY_FIT | 0-5 | Aligned with active or upcoming vocabulary cluster? |
| LEARNER_INTEREST | 0-3 | Connects to known interests, goals, real-world situations? |
| FRESHNESS | 0-3 | 3=never used, 2=4+ weeks ago, 1=2-3 weeks, 0=last week (exclude) |

`TOPIC_SCORE = GRAMMAR_FIT + VOCABULARY_FIT + LEARNER_INTEREST + FRESHNESS`

Highest score wins. Tie-break: prefer higher LEARNER_INTEREST.

Sprint override: if `sprint.active` is true, topic = sprint scenario theme. Skip scoring.

## Step 6b — Input Selection for Homework

**Full protocol in `curriculum/tutor-guides/input-orchestration.md` Section 1.** Summary:

1. **Level filter:** Resources whose `level_range` includes current listening/reading level or one above (i+1)
2. **Dialect preference:** Prefer resources matching `target_dialect`. Accept neutral-dialect.
3. **Topic alignment:** Score by overlap with weekly narrow topic
4. **Freshness:** Check `resource-tracker.yaml` — prefer resources not assigned in last 2 sessions. Avoid `learner_engagement: reluctant`.
5. **Autonomy:** Prescriptive (Phase A-B), guided (Phase C), autonomous (Phase D)
6. **Time budget:** Fit to remaining homework time after Anki and writing assignments. Input share increases with phase.

For L2-L3 prescriptive assignments, check `media-bank.yaml > prescriptive_episodes` for entries with `content_summary` — these enable informed comprehension debriefs.

**Vocabulary boost:** If a vocabulary cluster's `passive_known` increased recently (from input exposure), boost that cluster for production practice. Input primes production.

## Step 7 — Session Format (occasional)

Most sessions use the standard 4-phase flow. Occasionally consider an alternative format from `curriculum/tutor-guides/session-variety.md`. Triggers:
- Motivation dipping or routine fatigue → Game Day
- Grammar consolidation phase with 3+ acquired concepts → Story Building or Teach-Back
- Weekly topic has strong media options → Media Reaction
- Phase transition approaching → Immersion-Only
- Sprint mode or upcoming real-world event → Real-World Simulation

Frequency: no more than 1 alternative format per week. The standard session is the default.

## Quick Reference — Common Scenarios

- **"Stuck on ser/estar for 4 sessions"**: GAP=8, DECAY=0, NEED=10 → score 18. Top priority. Route: try a different Stage 2 approach.
- **"Preterite not practiced in 10 days, was acquired"**: GAP=0, DECAY=7, NEED=1 → score 8. Maintenance. Spot-check in conversation.
- **"New concept ready to introduce"**: NEED=10, GAP=10, DECAY=0 → score 20. Highest. Route: Stage 1 (noticing).
- **"Post-return regression on gender agreement"**: GAP=10, DECAY=9, NEED=7 → score 26. Urgent. Dedicated recovery.
- **"Parking lot: learner asked about conditional"**: If C-04 prerequisites met, boost by +3 and consider as primary.

## Worked Scoring Examples

### Example 1 — High-priority practicing concept

Concept A-02 (Ser vs Estar): Phase A prerequisite, practicing for 3 sessions, production error rate 35%, last practiced 2 days ago, weekly topic is "daily routines" (adjacent), practice_count=6.

| Dimension | Calculation | Score |
|-----------|------------|-------|
| NEED | Phase prerequisite | 10 |
| GAP | Practicing, production error >30% | 8 |
| DECAY | 2 days ago → raw 2, durability: 2 * (1 - min(6/20, 0.7)) = 2 * 0.7 = 1.4 | 1.4 |
| TOPIC_BOOST | Adjacent to weekly topic | 1 |
| INTEREST | No explicit signal | 0 |
| VARIETY_PENALTY | Different activity type from last 2 days | 0 |
| **PRIORITY** | 10 + 8 + 1.4 + 1 + 0 - 0 | **20.4** |

Selected as primary because highest total and production errors need targeted Stage 2 practice.

### Example 2 — Maintenance concept with high decay

Concept B-01 (Preterite Regular): Previously acquired, last practiced 12 days ago, production error rate <15%, weekly topic unrelated, practice_count=18.

| Dimension | Calculation | Score |
|-----------|------------|-------|
| NEED | Previous phase maintenance | 1 |
| GAP | Acquired + integration-tested | 0 |
| DECAY | 12 days → raw 7, durability: 7 * (1 - min(18/20, 0.7)) = 7 * 0.3 = 2.1 | 2.1 |
| TOPIC_BOOST | No connection | 0 |
| INTEREST | No signal | 0 |
| VARIETY_PENALTY | None | 0 |
| **PRIORITY** | 1 + 0 + 2.1 + 0 + 0 - 0 | **3.1** |

Low priority despite 12-day gap because the concept is well-practiced (high durability dampens DECAY) and already acquired. Suitable as an interleaving target, not a primary focus.

### Example 3 — Competing concepts with parking lot boost

Concept C-01 (Subjunctive Triggers): Current phase concept, practicing, production error 20%, last practiced 5 days ago, practice_count=8. Concept C-04 (Conditional): Current phase concept, practicing, production error 25%, last practiced 1 day ago, practice_count=4. Learner asked about conditional in parking lot.

| | C-01 Subjunctive | C-04 Conditional |
|---|---|---|
| NEED | 7 | 7 |
| GAP | Production 15-30% → 5 | Production 15-30% → 5 |
| DECAY | 5 days → raw 5, durability: 5 * (1 - 0.4) = 3.0 | 1 day → raw 0, durability: 0 * 0.8 = 0 |
| TOPIC_BOOST | 0 | 0 |
| INTEREST | No signal → 0 | Parking-lot question → 2 |
| Parking lot | — | +3 |
| VARIETY_PENALTY | 0 | 0 |
| **PRIORITY** | **15.0** | **17.0** |

C-04 wins. The parking-lot boost (+3) and interest signal (INTEREST=2) combined give C-04 a clear lead. C-01 becomes secondary or interleaving target. Tie-break rule (prefer higher learner interest) is not needed here — C-04 wins on score alone.

### Example 4 — Regression beats high interest (ENGINE-02 demonstration)

Concept A-02 (Ser vs Estar): Phase A prerequisite, REGRESSED (was acquired, now regressed), production error rate 40%, last practiced 3 days ago, practice_count=15, INTEREST=0. Concept C-05 (Por vs Para): Current phase concept, practicing, production error 18%, last practiced 5 days ago, practice_count=4, learner asked about it unprompted two sessions ago, INTEREST=3.

| | A-02 (Regressed) | C-05 (High Interest) |
|---|---|---|
| NEED | Phase prerequisite → 10 | Current phase → 7 |
| GAP | Regressed → 10 | Production 15-30% → 5 |
| DECAY | 3 days → raw 2, durability: 2 * (1 - 0.7) = 0.6 | 5 days → raw 5, durability: 5 * (1 - 0.2) = 4.0 |
| TOPIC_BOOST | 0 | 0 |
| INTEREST | No signal → 0 | Asked unprompted → 3 |
| VARIETY_PENALTY | 0 | 0 |
| **PRIORITY** | **20.6** | **19.0** |

A-02 wins despite having zero interest. The regression (NEED=10, GAP=10) creates a baseline of 20 that even maximum INTEREST=3 cannot overcome for a non-regressed concept. This is the additive cap working as designed: interest guides the engine when priorities are comparable, but never overrides a true regression.

## Naturally-Acquired Concepts

When the learner spontaneously uses a concept that hasn't been formally introduced (status: unseen):

1. **Confirm understanding:** Test it naturally in 2-3 more contexts within the same session. Don't announce you're testing.
2. **If confirmed:** Update skill-map:
   - Set `introduced_date` to today
   - Set `status` to `practicing` (not acquired — needs more observation)
   - Set `performance_unscaffolded` to `competent` (they demonstrated it unprompted)
   - Set `error_rate_production` based on observed accuracy
   - Add note: "Naturally acquired — observed in free production before formal introduction"
3. **If shaky:** Set to `introduced` with a note. The decision engine will prioritize it for formal practice.
4. **Skip formal Stage 1 (noticing)** for confirmed natural acquisitions. Route directly to Stage 3-4 communicative practice.
