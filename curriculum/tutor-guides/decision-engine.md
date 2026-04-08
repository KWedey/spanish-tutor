# Decision Engine Guide

Loaded when: Standard session (post-onboarding). Used to select today's focus concepts and route to appropriate activities.

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

## Step 6b — Media Selection for Homework

When assigning listening or reading homework, select from `curriculum/media-bank.yaml` using:

1. **Phase filter:** Only resources whose `phase_range` includes the learner's current phase
2. **Dialect preference:** Prefer resources matching `target_dialect` from learner-profile. Accept neutral-dialect resources.
3. **Topic alignment:** Score by overlap with the current weekly narrow topic (direct match > adjacent > unrelated)
4. **Level calibration:** Match to `receptive_skills.listening.current_level` or `receptive_skills.reading.current_level` — assign at-level or one step above
5. **Freshness:** Avoid assigning the same channel/source 3 sessions in a row. Rotate.

If multiple resources tie, prefer the one the learner has engaged with before (check `resource-tracker.yaml` engagement data). For new learners, start with the most accessible option in each category.

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
