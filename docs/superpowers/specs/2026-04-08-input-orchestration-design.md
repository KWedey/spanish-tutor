# Input Orchestration & Decision Engine Enhancements

**Date:** 2026-04-08
**Status:** Draft
**Scope:** Structured input pathway, interleaving protocol, carryover escalation, vocabulary production tracking

## Problem Statement

The tutoring system's strongest machinery — decision engine, skill tracking, 4-stage instruction — is entirely pointed at production. Listening and reading are treated as homework suggestions rather than a first-class instructional pathway. There is no level progression through input materials, no comprehension assessment protocol, and no feedback loop from input observations into the skill map.

SLA research consistently identifies comprehensible input as the primary driver of acquisition. The system already curates the right external tools (Dreaming Spanish, podcasts, graded readers) but doesn't orchestrate them — media-bank.yaml is a list, not a curriculum.

Secondary gaps: the decision engine doesn't interleave concepts during practice, carryover concepts have no escalation protocol when stalled, and vocabulary production errors aren't formally tracked.

## Design

### 1. Input Progression Model

Listening and reading get the same leveled, tracked treatment that grammar concepts already have. Levels advance independently — a learner might be L3 listening but R2 reading.

#### Listening Levels (L1–L5)

| Level | Speed | Support | Key Sources | Comprehension Target |
|-------|-------|---------|-------------|---------------------|
| L1 | Simplified tutor speech | Full context | In-session, Anki audio, Forvo | Recognize individual words |
| L2 | Slow, structured | Heavy visual + repetition | Dreaming Spanish Beginner, News in Slow Spanish | Gist — "what was it about?" |
| L3 | Moderate, semi-structured | Visual support, less repetition | Dreaming Spanish Intermediate, structured podcasts | Main ideas + some details |
| L4 | Natural speed | Text support available | Language Reactor, subtitled content, Duolingo Podcast | Details + basic inference |
| L5 | Natural speed, varied accents | None | Radio Ambulante, native TV/film, unscripted YouTube | Full comprehension with inference |

The L2→L3→L4 progression is deliberately granular. The transition from slow/structured to natural speed is where most learners stall. L3 (moderate with visual support) bridges this gap. L4 (natural speed with subtitle safety net) provides a second bridge before L5 drops all support.

#### Reading Levels (R1–R5)

| Level | Description | Key Sources | Comprehension Target |
|-------|------------|-------------|---------------------|
| R1 | Cognate recognition, familiar-topic short texts, simple descriptions | In-session materials, Anki card context, basic web content | Word-level recognition, cognate identification |
| R2 | Short paragraphs, graded readers L1 | Olly Richards, CIDEB readers, SpanishDict articles | Gist with dictionary support |
| R3 | Graded readers L2–3, simple articles | News in Slow Spanish articles, short blog posts | Main ideas, limited lookup |
| R4 | Authentic articles, blog posts, short stories | BBC Mundo, medium-length articles, cuentos cortos | Details, infrequent lookup |
| R5 | Literature, journalism, technical content | Novels, longform journalism, academic content | Full comprehension |

#### Level-Up / Level-Down Criteria

Levels are decoupled from grammar phases. A motivated learner doing heavy input outside sessions could reach L4 while still in Phase B grammar.

**Level-up triggers (all three required):**
- Comprehension debrief shows consistent target-quality performance for 2+ consecutive weeks
- Learner self-reports "just right" or "too easy"
- Minimum hours at current level reached (soft guidelines, not hard gates):
  - L1→L2: ~5 hours
  - L2→L3: ~20 hours
  - L3→L4: ~40 hours
  - L4→L5: ~60 hours
  - Reading levels: similar thresholds scaled to reading speed

Hour minimums prevent premature level-up from a few good sessions. A learner consistently excelling well before the hour target shouldn't be held back.

**Level-down triggers (either one):**
- Comprehension debrief shows gist-only at a level targeting details, for 2+ sessions
- Learner reports sustained struggle for 2+ sessions

Level-down is never framed as failure: "Let's build more at this level before jumping up."

#### Multi-Pass Protocol (L2–L3)

At lower levels, recommend re-listening with different focus per pass:
- First pass: gist (what is this about?)
- Second pass: details (what specifically happened?)
- Third pass: vocabulary (what new words can you pick out?)

At L4+, single-pass is expected. Re-listening is optional and self-directed.

Multi-pass is recommended when time allows, not mandatory. A single focused pass is acceptable if the learner's homework time is tight.

### 2. Input Orchestration Protocol

#### 2a. Input Selection Logic

The decision engine already selects a weekly topic. Input selection layers on top.

**Selection flow:**
1. Check learner's current listening level and reading level from skill-map
2. Filter media-bank to resources at current level or one above (i+1 — slightly challenging is ideal)
3. Prefer resources aligned with weekly topic
4. Apply variety — don't assign the same resource 2 sessions in a row; rotate between listening and reading
5. Check resource-tracker for staleness — prefer resources not recently used; avoid resources with `learner_engagement: reluctant`
6. Fit to available homework time (from learner-profile capacity fields)

**Prescriptiveness follows the autonomy ladder:**

| Phase | Input Assignment Style |
|-------|----------------------|
| A–B | Prescriptive: "Watch this Dreaming Spanish episode" (specific title) |
| C | Guided: "Pick a podcast episode about [topic] from these 2–3 options" |
| D | Autonomous: "20 min of L5 input, your choice — tell me about it next session" |

#### 2b. In-Session Comprehension Debrief

3–5 minutes during Review & Warm-up. Conversational, not quiz-like. Conducted increasingly in Spanish as phase advances.

**Flow:**

1. **What did you consume?** — Log resource, estimated duration, number of passes
2. **Topic probe:** "¿De qué se trataba?" — Assesses gist comprehension. If they can't summarize the general topic, the level is too high.
3. **Detail probe:** 1–2 follow-up questions natural to the content — Assesses depth appropriate to their level target. For resources with a `content_summary` in media-bank, the tutor loads it before the debrief to ask informed follow-ups. For resources without summaries, the tutor relies on depth-of-elaboration as the comprehension proxy.
4. **Vocabulary extraction:** "¿Aprendiste alguna palabra nueva?" — Record new words/phrases picked up passively. If the learner reports none at a level where they should be encountering unknowns, that's a signal (either level is too low, or they're not noticing — different interventions).
5. **Difficulty self-report:** "¿Cómo te pareció el nivel?" — Cross-reference against observed comprehension quality. Feeds learner calibration trust weight.

The tutor does NOT: replay content, quiz on specifics they couldn't know, or frame this as assessment.

**Vocabulary extraction caveat:** Most passive acquisition is subconscious — the learner won't report most of what they absorbed. The real signal is comprehension quality at level, not explicit word counting. Track what's reported but don't over-weight it.

#### 2c. Content Summaries

Content summaries in media-bank enable informed debriefs but must be pre-authored by the system designer (sourced from episode descriptions, resource metadata, or written manually). The tutor cannot generate them — it can't watch videos or listen to podcasts.

Pre-populate summaries for the 10–15 core L2–L3 resources that will be assigned during early sessions. Everything else operates in elaboration-only debrief mode. Summaries can be added incrementally as new resources enter regular rotation.

**Format in media-bank.yaml:**

```yaml
- name: "Dreaming Spanish - Super Beginner: Mi rutina"
  type: youtube
  level: L2
  dialect: neutral_latam
  topic_alignment: [daily-routine]
  duration_minutes: 8
  content_summary: "Speaker describes morning routine using present tense. Key vocabulary: despertarse, ducharse, desayunar, salir. Heavily visual with acting out each action."
```

#### 2d. Skipped Input Homework

If the learner reports not completing input homework:

- **Single skip:** No intervention. Life happens. Assign normally next session.
- **2 consecutive skips:** Reduce input assignment load (time budget may be wrong). Do a brief in-session listening moment (2–3 min) — play/describe a short segment, discuss.
- **3+ skips:** Ask the learner what's getting in the way. The assignment format may need to change (different resource type, shorter segments, different time of day), not just the quantity.

#### 2e. Input Time Allocation

Input's share of homework time grows with phase. These are guidelines that shape the tutor's allocation, not rigid percentages:

- **Phase A:** Input is supplementary. Most homework time goes to Anki and basic exercises. Introduce input as "bonus" listening.
- **Phase B:** Input becomes a regular assignment. Roughly equal weight with Anki and exercises.
- **Phase C:** Input is the primary homework. Anki decreases as vocabulary becomes self-sustaining through exposure.
- **Phase D:** Input dominates. Anki is minimal (maintenance only). The learner's main growth driver is volume of comprehensible input.

#### 2f. State Feedback Loop

After the debrief, the tutor silently updates:

| Target | What Gets Updated |
|--------|------------------|
| `resource-tracker.yaml` | Hours logged per resource, sessions used, vocabulary extracted count, learner engagement |
| `skill-map > receptive_skills` | `current_level`, `comprehension_quality`, `hours_at_level`, `hours_total`, `level_up_evidence` |
| `skill-map > vocabulary_clusters` | Increment `passive_known` for words encountered in input; add confirmed gaps to `weak_production` |
| Session log | `input_reviewed` section (see schema below) |

**Input→production pipeline:** When the decision engine selects vocabulary for practice, it boosts clusters where passive exposure has been logged. The learner has heard/read these words — they're primed for production. This creates a natural input → recognition → production flow instead of introducing vocabulary cold.

### 3. Decision Engine Enhancements

#### 3a. Interleaving Protocol

Currently the engine selects one primary concept per session and reviews prior concepts separately. The change: weave retrieval of prior concepts into the practice activities for the primary concept, not as separate review blocks.

**Interleaving by instruction stage:**

| Stage | Primary Concept | Interleaved Concepts | Example |
|-------|----------------|---------------------|---------|
| Stage 2 (controlled practice) | Full focus, heavy scaffolding | 1 acquired concept embedded in drill sentences | Preterite drills where sentences also require correct ser/estar |
| Stage 3 (guided production) | Main target | 1 acquired + 1 practicing (Stage 3+) concept woven into prompts | "Tell me about a trip" targets preterite but requires prepositions and object pronouns |
| Stage 4 (integration) | Combined focus | 2–3 concepts across status levels | Conversation scenario that naturally demands primary + several prior concepts |

**Selection of interleaved concepts:**
- Prefer concepts with highest DECAY score (longest since last practiced)
- Prefer stalled carryover concepts (serves double duty as escalation)
- Log interleaved concepts in session log; reset their DECAY clock

**What this changes:** Warm-up becomes lighter — quick check-in, homework review, input debrief — rather than a dedicated review session. Prior concepts get exercised organically during the main lesson.

**Guardrails:**
- Never interleave a concept the learner hasn't reached Stage 3+ on — early-stage concepts need focused attention
- Never interleave more than 3 concepts in a single activity — cognitive overload defeats the purpose
- If the primary concept is brand new (Stage 1–2, first session), interleave only 1 acquired concept at most
- Track which concepts were interleaved in the session log so the DECAY clock resets

#### 3b. Carryover Escalation Protocol

Concepts that don't reach "acquired" before a phase transition carry over at their current performance level. Currently there's no escalation if they stall.

**Escalation ladder (by session count, not calendar weeks):**

| Sessions in Carryover | Action |
|----------------------|--------|
| 1–5 | Normal carryover allocation. No special treatment. |
| 6 | Flag in system-health. Tutor reviews error patterns — same mistake repeating, or varied errors? Same → explanation isn't landing. Varied → not enough practice volume. |
| 8 | Try a different instructional approach. If rule-based before, try example-based. If drills, try communicative. If always in the same context, try a new one. |
| 10 | Auto-trigger a 2-session mini-sprint on the stalled concept. Log sprint rationale in adjustment log. |
| 12+ | Surface to the learner: "This concept is taking longer than expected. That's normal — [concept] is genuinely hard for English speakers. Let's talk about what's not clicking." Use learner input to redesign approach. |

**Non-prerequisite carryover gets a longer leash:**

| Sessions in Carryover | Action |
|----------------------|--------|
| 1–8 | Normal allocation. |
| 9 | Flag in system-health. Review error patterns. |
| 12 | Try different approach. |
| 15 | Mini-sprint or deprioritize (if learner is progressing well on prerequisites, deprioritization is valid). |
| 18+ | Surface to learner. |

**Key principle:** Each escalation step changes the approach, not just the intensity. Repeating the same thing harder doesn't fix a stall.

**Integration with interleaving:** Stalled carryover concepts are prioritized as interleaving targets — they get woven into other activities rather than always practiced in isolation, which may be part of why they're stuck.

#### 3c. Vocabulary Production Error Tracking

Grammar concepts track `error_rate_drills` and `error_rate_production`. Vocabulary clusters only track word counts. This means the decision engine can't score vocabulary using GAP the way it scores grammar.

**Add to each vocabulary cluster in skill-map.yaml:**

```yaml
error_tracking:
  error_rate_production: 0.0   # rolling average, last 5 observations
  common_errors: []             # e.g., "gender: 'el mano' → 'la mano'"
  last_observed: null           # date of last in-session observation
```

**What counts as a vocabulary production error:**
- Wrong word choice (false cognate, near-synonym confusion)
- Wrong gender/article
- Wrong form (verb conjugation when the issue is the vocabulary, not the grammar pattern)

**What does NOT count:**
- Grammar errors that happen to involve a vocabulary word ("yo gusto pizza" → gustar construction error, not vocabulary)
- Code-switching to English for a word not yet in an active cluster — this is a gap indicator, not an error. Observed code-switching instances are logged in the session log's `production_gaps_observed` field. The tutor reviews session logs at startup and updates `weak_production` when patterns emerge across sessions.

**When to observe:** Vocabulary production errors surface naturally during conversation practice and guided production. The tutor already notices these — this change formalizes recording them.

**Decision engine integration:**
- Vocabulary clusters now scored using `error_rate_production` (for GAP) and `last_observed` (for DECAY), same formula as grammar
- Weight vocabulary GAP below grammar GAP to reflect lower observation resolution. Specific weight ratio should be tuned after 20+ sessions of real data.
- Unobserved clusters rise in priority via DECAY, which self-corrects the uneven observation frequency across clusters

#### 3d. Input Selection Step (New)

Added to the decision engine, runs during homework assignment:

1. Get `current_listening_level` and `current_reading_level` from skill-map
2. Filter media-bank to resources at current level or +1
3. Filter to weekly topic alignment where possible
4. Check resource-tracker: prefer resources not recently assigned, with `learner_engagement` != reluctant
5. Fit to available homework time using autonomy-appropriate prescriptiveness (see Section 2a)

#### 3e. Interleaving Selection Step (New)

Added to the decision engine, runs during activity design:

1. Get primary concept for session (existing logic)
2. Query skill-map for concepts with status "acquired" or "practicing" at Stage 3+ with highest DECAY
3. Select 1–3 based on primary concept's stage (see Section 3a table)
4. Prefer stalled carryover concepts as interleaving targets
5. Log interleaved concepts in session log; reset their DECAY clock

#### 3f. Carryover Escalation Check (New)

Added to session startup, runs after state validation:

1. For each carryover concept, read `sessions_in_carryover` from schedule.yaml
2. Check `is_prerequisite` to determine which escalation timeline applies
3. If threshold reached, load appropriate intervention
4. Log escalation actions in schedule.yaml adjustment log

### 4. Schema Changes

#### 4a. skill-map.yaml — Receptive Skills

Replace current minimal receptive skills section:

```yaml
receptive_skills:
  listening:
    current_level: L1            # L1-L5
    comprehension_quality: null  # gist | main_ideas | details | inference
    hours_at_level: 0
    hours_total: 0
    level_up_evidence: []        # list of dated observations, e.g., [{date: 2026-05-01, note: "summarized podcast details accurately"}]
    level_history: []            # e.g., [{level: L1, entered: 2026-04-10, hours_spent: 6}]
  reading:
    current_level: R1
    comprehension_quality: null
    lookup_frequency: frequent   # frequent | occasional | rare | none
    hours_at_level: 0
    hours_total: 0
    level_up_evidence: []
    level_history: []
```

Removed `speed_tolerance` — redundant with level definitions (L2 implies slow, L4 implies natural).

#### 4b. skill-map.yaml — Vocabulary Cluster Additions

Add to each vocabulary cluster:

```yaml
vocabulary_clusters:
  VC-01-greetings:
    # ... existing fields (words_total, passive_known, active_known, weak_production, weak_recognition, status)
    error_tracking:
      error_rate_production: 0.0
      common_errors: []
      last_observed: null
```

No `production_gaps` field — code-switching instances are logged per-session in session logs. The tutor reviews patterns across sessions and updates the existing `weak_production` list directly.

#### 4c. resource-tracker.yaml

New schema replacing current near-empty file:

```yaml
input_summary:
  total_listening_hours: 0
  total_reading_hours: 0
  current_listening_level: L1
  current_reading_level: R1

resources: []
  # Entries created on first assignment, not pre-populated. Example:
  # - name: "Dreaming Spanish"
  #   type: listening              # listening | reading | mixed
  #   level_range: [L2, L4]       # levels this resource spans
  #   sessions_assigned: 0
  #   sessions_completed: 0
  #   hours_logged: 0
  #   comprehension_trend: null    # improving | stable | declining (updated each debrief)
  #   vocabulary_extracted: 0      # count of words surfaced in debriefs
  #   last_assigned: null
  #   last_completed: null
  #   learner_engagement: null     # enthusiastic | neutral | reluctant
  #   notes: ""
```

#### 4d. schedule.yaml — Carryover Tracking

Add tracking fields to carryover concept entries:

```yaml
carryover_concepts:
  # Example entry:
  # - concept_id: A-05
  #   carryover_date: 2026-06-15
  #   sessions_in_carryover: 0       # incremented each session the concept is practiced
  #   current_approach: rule_based   # tracks instructional approach for escalation
  #   is_prerequisite: true          # determines which escalation timeline applies
```

#### 4e. Session Log — Input Section

Add to session log schema:

```yaml
input_reviewed:
  # Example entry:
  # - resource: "Dreaming Spanish - Beginner: Mi rutina"
  #   type: listening
  #   duration_minutes: 8
  #   passes: 2
  #   comprehension_assessment: main_ideas  # gist | main_ideas | details | inference
  #   vocabulary_extracted: ["ducharse", "desayunar"]
  #   production_gaps_observed: ["cepillarse"]
  #   difficulty_self_report: just_right    # too_easy | just_right | too_hard
  #   level_at_time: L2
```

#### 4f. Session Log — Interleaving Tracking

Add to session log schema:

```yaml
interleaved_concepts:
  # Example:
  # - concept_id: A-02
  #   interleave_context: "embedded ser/estar usage in preterite drill sentences"
  #   errors_observed: 0
```

#### 4g. media-bank.yaml — Content Summary Field

Add `content_summary` to prescriptive-phase resources (L2–L3 staples):

```yaml
content_summary: "Speaker describes morning routine using present tense. Key vocabulary: despertarse, ducharse, desayunar, salir. Heavily visual."
```

Pre-populate for 10–15 core resources. Must be human-authored (from episode descriptions or manual review). The tutor cannot generate these — it can't watch/listen to content.

### 5. New Files

| File | Purpose |
|------|---------|
| `curriculum/tutor-guides/input-orchestration.md` | Main tutor guide: input selection, comprehension debrief protocol, level calibration, skipped homework handling |
| `curriculum/listening-progression.yaml` | Structured data: each listening level with sources, comprehension targets, level-up criteria, recommended hours |
| `curriculum/reading-progression.yaml` | Structured data: each reading level with sources, comprehension targets, level-up criteria |

### 6. Modified Files

| File | Changes |
|------|---------|
| `CLAUDE.md` | Add input debrief to Review & Warm-up flow. Add input selection to homework assignment. Add carryover escalation to guardrails. Reference input-orchestration.md in conditional loads (always load post-onboarding). |
| `curriculum/tutor-guides/decision-engine.md` | Add input selection step, interleaving selection step, carryover escalation check, vocabulary GAP scoring update. |
| `curriculum/media-bank.yaml` | Add `content_summary` and `level` fields to existing entries. |
| `docs/system-design.md` | Update schemas: skill-map receptive skills, vocabulary error tracking, resource-tracker, session log input/interleaving sections, schedule carryover fields. |
| `state/skill-map.yaml` | Apply new receptive skills schema and vocabulary error tracking fields. |
| `state/resource-tracker.yaml` | Apply new schema. |
| `state/schedule.yaml` | Apply carryover tracking fields (when carryover concepts exist). |
| `scripts/validate-state.py` | Validate new required fields: receptive skill levels, vocabulary error tracking, resource-tracker schema, carryover session counts. |
| `scripts/generate-vault.py` | Add input progress (listening/reading levels, hours, level history) to vault Progress dashboard. |

### 7. What This Does NOT Include

Explicitly out of scope for this design:

- **Writing curriculum** — tracked in skill-map but no dedicated progression guide. Separate design needed.
- **Phase D graduation criteria** — unspecified in current system. Separate design needed.
- **Extended onboarding (beyond session 15)** — current guidance is vague. Separate design needed.
- **Metacognitive strategy instruction** — teaching the learner how to learn. Valuable but separate effort.
- **Autonomy ladder operationalization** — `autonomy_level` field exists but isn't wired into the decision engine beyond input prescriptiveness. Partial coverage here; full operationalization is separate.

### 8. Tuning Parameters

These values are initial estimates, flagged for revision after real session data:

| Parameter | Initial Value | Tune After |
|-----------|--------------|------------|
| Listening level-up hour minimums (L1→2: 5h, L2→3: 20h, etc.) | As specified | 10+ level transitions |
| Vocabulary GAP weight vs grammar GAP | Lower than grammar; specific ratio TBD | 20+ sessions |
| Carryover escalation session thresholds (6/8/10/12 prerequisite) | As specified | 5+ carryover escalations |
| Carryover escalation session thresholds (9/12/15/18 non-prerequisite) | As specified | 5+ carryover escalations |
| Maximum interleaved concepts per activity (3) | 3 | Observation of cognitive overload signals |
