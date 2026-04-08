# Decision Engine Guide

Loaded when: Standard session (post-onboarding). Used to select today's focus concepts and route to appropriate activities.

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

## Step 1 — Gather Candidates

All concepts in current phase with status: introduced, practicing, regressed, or acquired (for maintenance). Plus `carryover_concepts` from `schedule.yaml`. Plus maintenance from all previous phases (with decaying priority).

**Cultural concepts:** Also gather `cultural_awareness` concepts from skill-map whose `introduced_at_phase` matches the current phase or earlier. Score them using the same formula but with NEED capped at 5 (cultural concepts are secondary to grammar). Cultural concepts are never the primary focus — they supplement grammar work during conversation practice or as a secondary concept.

**Filter:** Exclude any concept where prerequisites are not met. A prerequisite is "met" when its status is "acquired" or "automatic". Status "practicing" or below means the prerequisite is not met and the dependent concept cannot be introduced.

## Step 2 — Score Each Candidate

```
PRIORITY = NEED + GAP + DECAY + TOPIC_BOOST - VARIETY_PENALTY
```

### NEED (0-10)

| Concept type | Score |
|-------------|-------|
| Phase prerequisite (unlocks most concepts) | 10 |
| Current phase concept | 7 |
| Carryover concept from prior phase | 5 |
| Current phase maintenance | 2 |
| Previous phase maintenance | 1 |
| Two+ phases back maintenance | 0.5 |
| Cultural concept (any phase) | min(base score, 5) |

> **Note:** Cultural concepts use the same base scoring as grammar concepts of their type, but the NEED score is capped at 5. This ensures cultural work never displaces grammar as the primary focus.

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

### TOPIC_BOOST (0-3)

| Alignment with weekly narrow topic | Score |
|------------------------------------|-------|
| Direct match (topic naturally elicits this concept) | 3 |
| Adjacent (topic uses related vocabulary) | 1 |
| No connection | 0 |

### VARIETY_PENALTY (0-5)

Same activity type 3 days in a row → penalize that type by 5. Prefer alternation.

## Step 3 — Apply Modifiers

- **Low energy:** Boost passive activities (listening/reading review), reduce production demands. Halve GAP score for challenging concepts.
- **Low motivation / at-risk:** Boost easy wins (high-confidence concepts), add novelty. Double NEED for fun/interesting concepts.
- **Parking lot items:** If a parking lot item aligns with a candidate concept, boost that concept by +3. If the item suggests a concept not in the candidate list but prerequisites are met, it can override secondary concept selection.
- **Sprint override:** If `sprint.active` is true, only score concepts in `sprint.focus_areas`. All others excluded.

## Step 4 — Select Top 1-2 Concepts

Highest score = primary focus. Second highest = secondary (if time allows and not same category). If top concept is grammar, prefer vocabulary or pronunciation as secondary (variety). Tie-break: prefer higher learner interest.

## Step 5 — Route to Activity

**Fluency days** (1x/week in Phase B, 2x/week in Phase C, every session in Phase D): Run Steps 1-4 normally to select concept(s). At Step 5, route to `fluency-activities.md` instead of the stage-based routing below.

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

1. Query skill-map for concepts with status "acquired" or "practicing" at Stage 3+ (guided production or later)
2. Rank by DECAY score (highest = longest since practiced)
3. Prefer stalled carryover concepts (serves double duty as escalation — see Step 0b)
4. Select count based on primary concept's stage:

| Primary Concept Stage | Interleaved Count | Rule |
|----------------------|-------------------|------|
| Stage 1-2 (first session with concept) | 0-1 | At most 1 acquired concept. New concepts need focused attention. |
| Stage 2 (controlled practice, subsequent sessions) | 1 | 1 acquired concept embedded in drill sentences |
| Stage 3 (guided production) | 2 | 1 acquired + 1 practicing (Stage 3+) woven into prompts |
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
