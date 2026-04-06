# Curriculum Build-Out and Infrastructure Evaluation — Design Spec

**Date:** 2026-04-06
**Scope:** Comprehensive evaluation of existing infrastructure, curriculum content design, state schema refinements, decision engine updates, and supporting file changes.
**Output:** 89 curriculum files + infrastructure modifications to existing state schemas, CLAUDE.md, system-design.md, and supporting YAML files.

---

## 1. Design Principles

These principles govern all decisions in this spec:

1. **Acquisition stages, not rule memorization.** Every grammar concept follows: exposure → noticing → controlled practice → guided production → communicative practice. Curriculum files encode this structure.
2. **Guardrails, not scripts.** Curriculum files provide sequencing, known pitfalls, drill templates, and signs of acquisition. The tutor uses its own Spanish knowledge for examples, conversation, and contextual drills.
3. **Honest precision.** State tracking uses the level of precision the tutor can reliably observe. No false quantification of qualitative assessments.
4. **Dependency-driven progression.** Phase transitions and concept sequencing follow prerequisite chains, not arbitrary thresholds.
5. **Content verification.** Every example sentence, paradigm table, and vocabulary entry is verified against authoritative sources (SpanishDict, RAE) during creation.

---

## 2. Revised Grammar Progression

### 2.1 Changes from Current

**Added as standalone concepts (6):**
- A-06: Gustar-type verbs — promoted from L1 interference note. Reversed sentence structure requires dedicated teaching.
- B-08: Estar + gerund (progressive) — high-frequency, reinforces estar usage.
- B-09: Imperatives (tu/usted commands) — fundamental communicative function with own conjugation patterns.
- B-10: Comparatives and superlatives — distinct grammatical pattern (mas...que, irregular forms).
- C-08: Indirect speech — "Me dijo que..." requires subjunctive/indicative distinction.
- C-09: Diminutives and augmentatives — essential for natural speech, especially Mexican Spanish. Cultural marker.

**Expanded within existing concepts (3):**
- A-03: Gender and number agreement — now includes demonstratives (este/ese/aquel) and unstressed possessives (mi/tu/su) as subsections. These are small pattern extensions of agreement, not standalone concepts.
- A-04: Articles, prepositions, and contractions — now includes personal 'a' as a dedicated section. Introduced here, reinforced in B-06 (direct object pronouns).
- A-07: Common irregular present — explicitly includes "hay" (there is/there are) as a key entry.

**Evaluated and rejected as standalone:**
- Demonstratives — subsection of A-03 (same gender agreement pattern)
- Unstressed possessives — subsection of A-03
- Adverb formation — taught in context, -mente rule is one sentence
- Stressed possessives (el mio, la tuya) — deferred to Phase B, taught as vocabulary/usage when it arises

### 2.2 Phase A — Foundation (A1-A2): 8 Concepts

| # | Concept | Prerequisites | Key L1 Interference |
|---|---------|--------------|---------------------|
| 00 | Communication repair phrases | None | — |
| 01 | Present tense (regular -ar, -er, -ir) | None | Subject pronoun overuse |
| 02 | Ser vs estar | A-01 | Ser/estar confusion (high severity) |
| 03 | Gender, number, agreement + demonstratives + possessives | None | Adjective placement |
| 04 | Articles, prepositions, personal 'a' | A-03 | Preposition mapping |
| 05 | Basic questions and negation | A-01 | Double negative avoidance |
| 06 | Gustar-type verbs (gustar, encantar, molestar, importar, interesar, doler) | A-01 | Gustar construction (high severity) |
| 07 | Common irregular present (ir, tener, querer, poder, hacer, decir, saber/conocer, hay) | A-01 | — |

### 2.3 Phase B — Conversational (A2-B1): 11 Concepts

| # | Concept | Prerequisites | Key L1 Interference |
|---|---------|--------------|---------------------|
| 01 | Preterite regular | A-01 | — |
| 02 | Preterite irregular | B-01 | — |
| 03 | Imperfect | A-01 | — |
| 04 | Preterite vs imperfect | B-01, B-02, B-03 | English doesn't distinguish aspect (high severity) |
| 05 | Reflexive verbs | A-01 | — |
| 06 | Direct object pronouns | A-01, A-04 | — |
| 07 | Indirect object pronouns | B-06 | — |
| 08 | Estar + gerund (progressive) | A-01, A-02 | Progressive overuse for habitual actions |
| 09 | Imperatives (tu/usted commands) | A-01, A-07 | Pronoun placement with commands |
| 10 | Comparatives and superlatives | A-03 | de vs que distinction |
| 11 | Future with ir + a | A-01 | — |

### 2.4 Phase C — Intermediate (B1-B2): 9 Concepts

| # | Concept | Prerequisites | Key L1 Interference |
|---|---------|--------------|---------------------|
| 01 | Present subjunctive (forms) | A-01, A-07 | Subjunctive avoidance (high severity) |
| 02 | Subjunctive triggers | C-01 | — |
| 03 | Formal future tense | A-01 | — |
| 04 | Conditional | C-03 | — |
| 05 | Por vs para | A-04 | — |
| 06 | Present perfect and compound tenses | B-01 | — |
| 07 | Relative clauses (que, quien, donde, lo que) | C-01 | — |
| 08 | Indirect speech (me dijo que..., queria saber si...) | C-01, C-02, B-04 | Tense shifting with subjunctive |
| 09 | Diminutives and augmentatives (-ito/-ita, -ote/-ota) | A-03 | Diminutive underuse (absence, not wrong form) |

### 2.5 Phase D — Advanced (B2-C1): 6 Concepts (Unchanged)

| # | Concept | Prerequisites |
|---|---------|--------------|
| 01 | Past subjunctive (imperfect subjunctive) | C-01, B-03 |
| 02 | Si clauses (if...then) | C-04, D-01 |
| 03 | Subjunctive across all tenses | D-01, C-06 |
| 04 | Passive voice and se constructions | B-01 |
| 05 | Register shifting (tu/usted/vos) | — |
| 06 | Nuanced connectors (sin embargo, no obstante, a pesar de que) | — |

### 2.6 Totals

| Phase | Concepts | Change |
|-------|----------|--------|
| A | 8 | +1 |
| B | 11 | +3 |
| C | 9 | +2 |
| D | 6 | 0 |
| **Total** | **34** | **+6** |

---

## 3. Phase Transition Rules

### 3.1 Current Rule (Replace)

"All concepts in the current phase must be at 'acquired' or 'automatic' status."

### 3.2 New Rule: Dependency-Based Transitions

Phase transition requires ALL of:

1. Every concept that is a **prerequisite for any next-phase concept** must have status "acquired"
2. All remaining concepts must have status "practicing" with error_trend "stable" or "improving"
3. No concept in the current phase has status "regressed"
4. Phase transition assessment passed (integrated exercise covering all phase concepts)

Concepts not meeting "acquired" enter `schedule.carryover_concepts` and continue receiving active practice in the new phase.

### 3.3 Phase A to B: Specific Requirements

**Must be acquired (prerequisites for Phase B concepts):**
- A-01 (present regular) — prerequisite for B-01, B-03, B-05, B-06, B-08, B-11
- A-02 (ser/estar) — prerequisite for B-08
- A-04 (articles/prepositions/personal 'a') — prerequisite for B-06

**May carry over as "practicing":**
- A-03 (gender/agreement)
- A-05 (questions/negation)
- A-06 (gustar-type)
- A-07 (irregular present)

### 3.4 Phase B to C: Specific Requirements

**Must be acquired (prerequisites for Phase C concepts):**
- B-01 (preterite regular) — prerequisite for C-06
- B-04 (preterite vs imperfect) — prerequisite for C-08

**May carry over as "practicing":**
- B-02, B-03, B-05, B-06, B-07, B-08, B-09, B-10, B-11

### 3.5 Phase C to D: Specific Requirements

**Must be acquired (prerequisites for Phase D concepts):**
- C-01 (present subjunctive) — prerequisite for D-01
- C-04 (conditional) — prerequisite for D-02
- C-06 (compound tenses) — prerequisite for D-03

**May carry over as "practicing":**
- C-02, C-03, C-05, C-07, C-08, C-09

Note: B-01 and B-03 should already be acquired from the B→C transition.

### 3.6 Carryover Concept Rules

- Carryover concepts are prioritized over new-phase concepts in the decision engine (unfinished business is more urgent unless a new concept is needed for communication)
- The "max 2 concepts in practicing simultaneously" guardrail expands to **max 3** when carryover concepts are present, ensuring at least one new-phase concept can always be introduced
- Carryover concepts are removed from the list when they reach "acquired"

---

## 4. State Schema Changes

### 4.1 Skill Map: Context Performance (Replaces `context_gap: boolean`)

```yaml
# Per grammar concept — replaces context_gap
performance_scaffolded: null    # null (untested), struggling, competent
performance_unscaffolded: null  # null (untested), struggling, competent
integration_tested: false       # tested in combination with other active concepts?
```

- **scaffolded** = drills, fill-in-the-blank, guided exercises (tutor can count attempts/errors)
- **unscaffolded** = spontaneous conversation, open-ended production (tutor assesses qualitatively)
- **integration_tested** = has the concept been tested alongside other active concepts in free production?

Three fields, two possible values each (plus null). The tutor can reliably distinguish "struggling" from "competent." Finer granularity is false precision from text-based interaction.

**Acquisition requirement:** A concept cannot be marked "acquired" unless `performance_unscaffolded` is "competent."

### 4.2 Skill Map: Receptive Skills (New Section)

```yaml
receptive_skills:
  listening:
    current_level: null           # superbeginner, beginner, intermediate, advanced, native
    comprehension_quality: null   # gist, main-ideas, detailed, near-native
    speed_tolerance: null         # slow, moderate, natural
    last_level_change: null
    notes: ""

  reading:
    current_level: null           # graded-A1, graded-A2, graded-B1, adapted, authentic-simple, authentic
    comprehension_quality: null   # gist, main-ideas, detailed, near-native
    lookup_frequency: null        # constant, frequent, occasional, rare
    last_level_change: null
    notes: ""
```

Updated during weekly review based on homework verification patterns across the week. Level-up decisions are the tutor's judgment, informed by comprehension quality over multiple sessions.

### 4.3 Skill Map: Cultural Awareness Clarification

Cultural awareness skills are distinct from grammar concepts — they track **pragmatic judgment** (when/why), not **grammatical form** (how).

```yaml
cultural_awareness:
  register_shifting:
    status: unseen
    introduced_at_phase: D
    assessed_through: "conversation behavior, role-play scenarios"
    signs_of_acquisition: "Shifts registers appropriately without prompting in role-play"
    notes: ""
  # Same structure for: politeness_formulas, conversational_rhythm,
  # regional_awareness, humor_and_idioms
```

Grammar D-05 (register shifting) teaches the conjugation forms for tu/usted/vos. Cultural register_shifting teaches the social judgment of when to use each. The grammar concept can be "acquired" while the cultural skill is still developing.

### 4.4 Vocabulary Clusters: Core/Exposure Distinction

```yaml
# In each vocabulary cluster file header
cluster_meta:
  core_words: 30          # must be actively known for cluster "acquired"
  exposure_words: 20      # passive recognition sufficient
  phase_alignment: A
  grammar_reinforcement: ["A-01-present-regular", "A-02-ser-vs-estar"]
```

- Core words become Anki cards with personal example sentences
- Exposure words are recycled through examples and context — passive recognition is the goal
- Cluster sizes expanded from 20-40 to 40-60 total words (30 core + 20 exposure typical)
- Phase vocabulary targets (300-500 for Phase A) include all sources: cluster files, grammar examples, conversation, incidental learning

### 4.5 Error Rate Methodology

- `error_rate_recent`: calculated from **scaffolded activities only**, where attempts can be reliably counted
- Minimum **10 observations across 3+ sessions** before the rate is considered reliable; below threshold, shows as `null`
- Free production assessment flows through `performance_unscaffolded`, not the error rate
- Self-corrections noted in session logs as qualitative indicators of monitor awareness, not factored into rate calculation

### 4.6 Session Log: Structured Observations

For scaffolded activities (drills, exercises):
```yaml
observations:
  - concept: "A-01-present-regular"
    context: scaffolded
    attempts: 12
    errors: 2
```

For unscaffolded activities (conversation, free production):
```yaml
observations:
  - concept: "A-01-present-regular"
    context: unscaffolded
    assessment: competent    # struggling or competent
```

This aligns session logs with the skill-map's context performance fields.

### 4.7 Session Log Retention

Extend from 30 days to **60 days**. Enables detection of regression patterns spanning 6-8 weeks. Weekly summaries (6-month retention) remain unchanged.

### 4.8 Schedule.yaml Changes

**Add:**
```yaml
carryover_concepts: []   # concepts from prior phase still in active practice
```

**Move from system-health.yaml to schedule.yaml:**
```yaml
anki_new_cards_per_session: 8
anki_retirement_threshold_days: 60
```

These are tunable configuration knobs, not health metrics.

### 4.9 System-Design.md: Resources Directory

Update the architecture tree to reflect the actual structure: single `resources/resource-catalog.yaml` instead of 7 individual YAML files. No functional change — the catalog already has `type` fields for filtering.

---

## 5. Decision Engine Refinements

### 5.1 GAP Score: Context-Aware

The GAP component of the priority formula considers context performance. Expressed as relative priorities, not numeric scores:

```
GAP considerations (highest to lowest urgency):

1. Regressed concepts — something that worked is actively failing
2. Scaffolded struggling — concept not understood fundamentally
3. Scaffolded competent, unscaffolded struggling — knows it but can't use freely
4. Scaffolded competent, unscaffolded untested — unknown risk, needs testing
5. Both competent, integration untested — likely solid but unverified in combination
6. Fully competent and integration tested — maintenance only (driven by DECAY)
```

### 5.2 Activity Type Routing

After selecting a focus concept, the engine routes to an activity type based on context performance. These are guidelines that inform the tutor's judgment, not hard rules:

- **Scaffolded struggling** → prioritize controlled practice (drills, fill-in, translation). Reference: concept file Stage 2.
- **Scaffolded competent, unscaffolded struggling** → prioritize communicative practice (conversation, role-play, storytelling). Reference: concept file Stages 3-4.
- **Integration untested** → prioritize combined exercises with other active concepts. Reference: activities/grammar-in-context.md.
- **All competent** → spot-check only (brief verification during conversation). Move to next priority.

### 5.3 Carryover Handling

- Carryover concepts are prioritized over new-phase concepts unless a new concept is urgently needed for communicative purposes
- They compete in the standard priority scoring with their elevated urgency
- The practicing limit expands from 2 to 3 when carryover concepts are present
- Removed from carryover list upon reaching "acquired"

### 5.4 Homework: Receptive Skill Matching

When assigning listening or reading homework, use the receptive_skills fields:

- **Listening:** If comprehension_quality is "gist" at current level, assign at same level. If "detailed" or better, step up one level.
- **Reading:** If lookup_frequency is "constant," the resource is too hard — step down. If "rare," step up.
- Resources from the target dialect region are preferred.

### 5.5 Weekly Topic Selection

During weekly review, prefer topics that:
- Align grammar_alignment with the current active_grammar.primary
- Align vocabulary_alignment with the current active_vocabulary.primary
- Match the learner's known interests
- Haven't been used in the last 4 weeks

---

## 6. Onboarding Sequence (10 Sessions)

### 6.1 Design Rationale

- 10 sessions: 1 discovery + 7 concept introductions + 2 consolidation
- Consolidation at **midpoint** (session 6) and **endpoint** (session 10) for baseline data collection
- One grammar concept per session (guardrail satisfied)
- Vocabulary clusters staggered alongside grammar (not counted as "concepts")
- Tool setup distributed across sessions to avoid overwhelming day 1
- Pacing escape valve: if the learner is struggling, consolidate instead of introducing. Remaining concepts get introduced post-onboarding via the decision engine.

### 6.2 Session Sequence

| Session | Grammar Concept | Vocabulary Focus | Tool Setup |
|---------|----------------|-----------------|------------|
| 1 | A-00 repair phrases (as memorized phrases during discovery) | tier1-greetings (begin) | Anki |
| 2 | A-01 present tense regular (-ar, -er, -ir) | tier1-greetings (continue) | SpanishDict |
| 3 | A-03 gender, agreement, demonstratives, possessives | tier1-basic-descriptions (begin) | Dreaming Spanish |
| 4 | A-04 articles, prepositions, personal 'a' | tier1-basic-descriptions (continue) | — |
| 5 | A-02 ser vs estar | tier1-numbers-time (begin) | Language Transfer, graded reader |
| 6 | **Midpoint consolidation** — review sessions 2-5, collect baseline data | tier1 review | — |
| 7 | A-05 questions and negation | tier1-directions (begin) | Speechling |
| 8 | A-06 gustar-type verbs | tier1-food-restaurant (begin) | — |
| 9 | A-07 common irregular present (including hay) | tier1-food-restaurant (continue) | Whisper (optional) |
| 10 | **Final consolidation** — all-concept review, transition assessment, set onboarding_complete | tier1 full review | — |

### 6.3 Sequencing Rationale

**Ser/estar at session 5 (not session 2):** The learner uses "soy" as a memorized phrase from session 1. By session 5, they have present tense conjugation (A-01), gender agreement (A-03), and articles (A-04) — enough language to practice the contrast in meaningful sentences. The 3 sessions of implicit ser usage builds intuition before formal instruction.

**A-03 before A-04:** Gender agreement is prerequisite for articles (el/la/los/las require knowing noun gender). Teaching articles before gender understanding leads to guessing.

**Midpoint consolidation at session 6:** Prevents 7 consecutive new-concept sessions. Reviews the first 4 concepts before introducing the second batch. Provides early baseline data for the decision engine.

**Adaptive consolidation:** If the learner has been consolidating due to pacing adjustments (escape valve), the consolidation session can be used for the next planned concept instead.

### 6.4 Tutor Guide / Session File Relationship

- **first-session.md** (tutor guide): protocol for HOW to run discovery. Already exists, no changes.
- **onboarding-guide.md** (tutor guide): protocol for HOW to run onboarding sessions. Already exists, minor update to reflect 10 sessions with midpoint consolidation.
- **curriculum/onboarding/session-NN.md** (session files): WHAT to cover in each session. These are the new files to create.

Tutor guides provide the *why*. Session files provide the *what*. The tutor loads both.

---

## 7. Curriculum File Templates

### 7.1 Grammar Concept File

```
# [Concept Name]

## Overview
1-2 sentences: what this concept is and why it matters for communication.

## When to Teach
- Phase: [A/B/C/D]
- Prerequisites: [list]
- L1 interference to preempt: [reference l1-interference.yaml IDs]

## The Pattern
Clear grammatical explanation with paradigm tables as needed.
Show the pattern before explaining the rule.

## Examples in Context
8-10 sentences using the concept naturally.
**Bolded** target structures.
Dialect-appropriate vocabulary.
Graduated: simple to complex.

## L1 Interference
English habits that cause errors with this concept.
Contrast pairs: English instinct vs correct Spanish.
Preemption script: what to say BEFORE the learner makes the error.

## Common Errors
3-5 most frequent errors with corrections.
Each classified: developmental, L1 interference, or overgeneralization.

## Teaching Sequence

### Stage 1: Noticing
1-2 activities where the learner discovers the pattern before explicit instruction.
"Look at these sentences. What do you notice about...?"

### Stage 2: Controlled Practice
1-2 drill formats with concept-specific items.
References activity templates by name for reusable formats.

### Stage 3: Guided Production
1-2 structured conversation prompts requiring the concept.
Scaffolding strategies and how to reduce them.

### Stage 4: Communicative Practice
1-2 open-ended tasks where the concept is needed but focus is on meaning.
Topic suggestions that naturally elicit this structure.

## Dialect Notes
Relevant dialect differences. Cross-references dialect-notes.yaml.

## Signs of Acquisition
- Scaffolded: [what competence looks like in drills]
- Unscaffolded: [what competence looks like in free conversation]
- Integrated: [what competence looks like when combined with other concepts]

## Connection Points
How this relates to other concepts. What it enables, what it builds on.
Common regression triggers when later concepts are introduced.
```

Each concept file should be approximately 2 pages. The teaching sequence section uses 1-2 items per stage, not exhaustive lists. The file encodes the SHAPE of the lesson; the tutor provides the specific content.

### 7.2 Vocabulary Cluster File

```
# [Cluster Name]

## Cluster Meta
- Phase alignment: [A/B/C/D]
- Core words: [count]
- Exposure words: [count]
- Grammar reinforcement: [concept IDs]
- Topic bank alignment: [weekly topic names]

## Core Vocabulary

### [Subtopic 1]
| Spanish | English | Example Sentence | Notes |
|---------|---------|-----------------|-------|

### [Subtopic 2]
[same format]

## Exposure Vocabulary
| Spanish | English | Notes |
|---------|---------|-------|
[No example sentences — recognition-level entries only]

## Common Collocations
Phrases and word pairings native speakers use naturally.

## False Cognates and Tricky Translations
Words that look like English words but mean something different.

## Dialect Variations
Key vocabulary that differs by dialect. Cross-references dialect-notes.yaml.

## Cultural and Pragmatic Notes
When/how these words are used differently than English equivalents.
Register notes: formal, informal, slang.

## Pronunciation Alerts
Words with sounds the learner is likely to mispronounce.
Stress patterns that differ from English intuition.
```

Example sentences provided for core words that meet any of these criteria: non-obvious translations (idiomatic usage), false cognates, important collocations (tener hambre, not just hambre), gender surprises (el agua — feminine but uses el), or pronunciation traps. Expect 15-20 sentences per cluster. Straightforward translations (mesa = table) get table entries without sentences.

### 7.3 Activity Template File

```
# [Activity Name]

## Purpose
What skill(s) this activity develops.
When in a session to use it.

## Phase Suitability
Which phases this works for and how it adapts.

## Setup
What the tutor needs to prepare or explain.

## How to Run

### Basic Version (Phase A-B)
Step-by-step with example prompts.

### Advanced Version (Phase C-D)
Scaled up: reduced scaffolding, increased complexity.

## What to Assess
What to observe and record during this activity.

## Variations
2-3 modifications for different energy levels or time constraints.

## Example Implementation
Complete run-through with sample dialogue.
```

### 7.4 Onboarding Session File

```
# Session N: [Title]

## Concept
Which grammar concept is introduced, or "Consolidation."

## Prerequisites Check
What the learner should be able to do before this session.

## Session Plan

### Review (5-8 min)
Specific homework review, verification questions.

### New Material (15-20 min) / Consolidation (15-20 min)
Step-by-step teaching following acquisition stages.
L1 interference to preempt with specific phrases.
References the grammar concept file for content.

### Practice (5-10 min)
Conversation prompts eliciting today's structures.

### Checkout (3-5 min)
Specific homework with tool and time estimates.
Tool setup tasks if applicable.

## Learner Observation Targets
What to note: preferences, energy, speed, correction response.

## Adjustment Notes
What to do if faster/slower than expected.
"If [previous concept] not yet at 'practicing,' consolidate instead."
```

### 7.5 Pronunciation Guide File

```
# [Sound Name]

## Phase
When this sound is actively taught.

## The Sound
Articulation description for English speakers.
IPA symbol. Closest English approximation.

## Common English Speaker Errors
What English speakers do wrong and why.

## Minimal Pairs
5-8 word pairs that differ only in this sound.

## Practice Assignments
Specific Speechling recording prompts.
Forvo words to listen to.
Target words for self-narration homework.

## Signs of Acquisition
Based on external tool feedback (Speechling coach, Whisper transcription accuracy).
```

---

## 8. L1 Interference Updates

### 8.1 Existing Entries to Modify

- `gustar-construction`: change `preempt_at` from `A-06-present-irregular-common` to `A-06-gustar-type-verbs`

### 8.2 New Entries

| ID | English Cause | Preempt At | Severity |
|----|--------------|-----------|----------|
| progressive-overuse | English overuses progressive for habitual actions ("I'm eating a lot" for habit vs current action) | B-08-progressive | medium |
| imperative-pronoun-placement | Object pronouns attach to affirmative commands but precede negative commands | B-09-imperatives | medium |
| comparative-de-vs-que | "de" with numbers (mas de 5) vs "que" with comparisons (mas grande que) | B-10-comparatives | low |
| indirect-speech-subjunctive | Spanish requires subjunctive in certain indirect speech contexts English doesn't | C-08-indirect-speech | medium |
| diminutive-underuse | English has no productive diminutive system; learner sounds overly formal without them | C-09-diminutives | low |

---

## 9. Dialect Notes Updates

Add entries to `curriculum/dialect-notes.yaml`:

**Grammar differences:**
- Imperative forms in voseo regions (vos: habla, come, vivi)
- Progressive frequency by region (Caribbean uses progressive more than highland varieties)

**Vocabulary differences:**
- Diminutive variation by region (-ito standard, -ico Costa Rica/Colombia, -illo parts of Spain)

---

## 10. Topic Bank Updates

### 10.1 New Topics

| Topic | Grammar Alignment | Vocabulary Alignment | CEFR |
|-------|------------------|---------------------|------|
| "Giving directions" | B-09-imperatives | tier1-directions-transportation | A2-B1 |
| "Comparing cities and countries" | B-10-comparatives | tier3-travel-culture | A2-B1 |
| "What are you doing right now?" | B-08-progressive | tier2-home-household | A2-B1 |
| "Retelling a friend's story" | C-08-indirect-speech | tier3-storytelling-narration | B1-B2 |
| "Terms of endearment and affection" | C-09-diminutives | tier2-family-relationships | B1-B2 |

### 10.2 Existing Topics: Alignment Updates

Update grammar_alignment for existing topics where new concepts are relevant (e.g., "My daily routine" can also align with B-08-progressive).

---

## 11. CLAUDE.md Updates

Targeted changes to the existing CLAUDE.md. The structure remains the same; these are line-level modifications.

### 11.1 Session Startup Protocol — Step 2 (Validate State)

Add checks:
- `performance_scaffolded` and `performance_unscaffolded` are not contradictory with `status` (e.g., scaffolded=struggling but status=acquired is a flag)
- `receptive_skills` levels are populated after session 5

### 11.2 Standard Session Flow — Consolidation Path

Replace: "If consolidating: skip explanation, reduce scaffolding, more free production"

With: "If consolidating: check context performance fields. Scaffolded struggling → controlled practice. Scaffolded competent but unscaffolded struggling → communicative practice. Integration untested → combined exercises with other active concepts."

### 11.3 State Updates — Additions

After every session, also update:
- `performance_scaffolded` and `performance_unscaffolded` for each practiced concept
- `integration_tested` if concepts were combined in free practice
- `receptive_skills` if listening/reading homework was reviewed
- Structured observation counts for scaffolded activities in the session log

### 11.4 Guardrails — Additions

- "Never mark a concept as 'acquired' unless `performance_unscaffolded` is 'competent'"
- "Never advance phases unless all prerequisite concepts for the next phase are 'acquired'"
- "Count carryover concepts toward the practicing limit. When carryover exists, limit expands from 2 to 3."

### 11.5 Guardrails — Revision

Current: "Never advance to a new concept if 2+ concepts are in 'practicing' status."
Revised: "Never advance to a new concept if 2+ concepts (3 when carryover exists) are in 'practicing' status. Consolidate first."

---

## 12. Known Limitations

### 12.1 Text-Based Tutoring Constraints

The tutor interacts through text. This means:

- **Fluency metrics** (speaking_pace, hesitation_frequency, self_correction_rate) are estimated from external tool reports and typed interaction patterns, not direct observation. They are lower-confidence than grammar error rates.
- **"Free conversation"** in sessions is typed. The learner has more processing time than real speech. The system has a built-in optimism bias for unscaffolded performance assessment.
- **Pronunciation** is entirely outsourced to Speechling, Forvo, and Whisper. The tutor assigns and tracks, but does not directly teach or assess.

### 12.2 Mitigations

- italki/Tandem recommended from Phase B specifically because the tutor cannot assess spoken fluency
- Self-narration homework provides spoken practice the tutor cannot directly offer
- Speechling provides human pronunciation feedback the tutor cannot give
- The system is most accurate for grammar and vocabulary assessment, less accurate for pronunciation and spoken fluency

### 12.3 Minimum Viable Commitment

- **Light:** 15-minute micro-session + 10 minutes Anki = 25 minutes/day
- **Typical:** 30-minute session + 20-30 minutes homework = 50-60 minutes/day
- **Full:** 45-minute session + 45-60 minutes homework = 90-105 minutes/day

---

## 13. File Inventory

### 13.1 New Files to Create (89)

| Category | Directory | Count | Notes |
|----------|-----------|-------|-------|
| Onboarding sessions | curriculum/onboarding/ | 10 | Sessions 1-10, including 2 consolidation |
| Grammar A | curriculum/grammar/A-foundation/ | 8 | Concepts 00-07 |
| Grammar B | curriculum/grammar/B-conversational/ | 11 | Concepts 01-11 |
| Grammar C | curriculum/grammar/C-intermediate/ | 9 | Concepts 01-09 |
| Grammar D | curriculum/grammar/D-advanced/ | 6 | Concepts 01-06 |
| Vocabulary tier 1 | curriculum/vocabulary/tier1-survival/ | 5 | 40-60 words each |
| Vocabulary tier 2 | curriculum/vocabulary/tier2-daily-life/ | 6 | 40-60 words each |
| Vocabulary tier 3 | curriculum/vocabulary/tier3-social/ | 6 | 40-60 words each |
| Vocabulary tier 4 | curriculum/vocabulary/tier4-abstract/ | 5 | 40-60 words each |
| Pronunciation | curriculum/pronunciation/ | 12 | Lightweight guide files |
| Activity templates | curriculum/activities/ | 11 | Reusable activity formats |

### 13.2 Existing Files to Modify

| File | Changes |
|------|---------|
| state/skill-map.yaml | Add context performance fields, receptive_skills section, cultural awareness structure, new grammar/pronunciation concepts |
| state/schedule.yaml | Add carryover_concepts, move Anki config from system-health |
| state/system-health.yaml | Remove Anki config (moved to schedule) |
| CLAUDE.md | Targeted updates per Section 11 |
| docs/system-design.md | Update schemas, decision engine, architecture tree, onboarding, file formats, phase transition rules |
| curriculum/l1-interference.yaml | Update gustar preempt_at, add 5 new patterns |
| curriculum/dialect-notes.yaml | Add voseo imperatives, progressive frequency, diminutive variation |
| curriculum/topic-bank.yaml | Add 5 new topics, update existing alignments |
| curriculum/tutor-guides/onboarding-guide.md | Update to reflect 10-session sequence with midpoint consolidation |

### 13.3 Content Verification

Every curriculum file is verified against authoritative sources during creation:
- Grammar: paradigm tables and example sentences checked against SpanishDict and RAE
- Vocabulary: gender, translations, and dialect variations verified against SpanishDict
- L1 interference: patterns cross-referenced against published SLA literature
- Pronunciation: articulation descriptions verified against phonetics references

---

## 14. Implementation Order

The implementation plan (separate document) should follow this order:

1. **Infrastructure first:** Modify state schemas, CLAUDE.md, system-design.md, supporting YAML files
2. **Phase A + Onboarding:** Grammar A concepts (8), tier-1 vocabulary (5), onboarding sessions (10), core activity templates, Phase A pronunciation guides (vowel-sounds, stress-rules) — makes the system usable
3. **Phase B:** Grammar B concepts (11), tier-2 vocabulary (6), Phase B pronunciation guides (rr-trill, r-single, b-v-equivalence, d-soft, linking)
4. **Phases C-D:** Grammar C-D concepts (15), tier-3/4 vocabulary (11), Phase C pronunciation guides (g-soft, j-sound, ny-sound, ll-y-sound, intonation), remaining activity templates

Each phase is independently valuable. Phase A completion makes the system functional for a new learner. Later phases can be built as the learner approaches them.

### 14.1 Pronunciation Files (12)

| File | Phase | Sound |
|------|-------|-------|
| vowel-sounds.md | A | Pure Spanish vowels (a, e, i, o, u) |
| stress-rules.md | A | Stress patterns, accent marks, syllable emphasis |
| rr-trill.md | B | Alveolar trill (perro, carro) |
| r-single.md | B | Single tap r (pero, caro) |
| b-v-equivalence.md | B | B and V are the same sound in Spanish |
| d-soft.md | B | Soft/fricative d between vowels (dado, nada) |
| linking.md | B | Connected speech between words |
| g-soft.md | C | Soft g before e/i (gente, girar) |
| j-sound.md | C | Jota sound (jugar, gente) |
| ny-sound.md | C | Palatal nasal (espanol, nino) |
| ll-y-sound.md | C | Lateral/palatal merger and regional variation |
| intonation.md | C | Question, statement, and exclamation patterns |

### 14.2 Activity Templates (11)

| File | Purpose |
|------|---------|
| conversation-prompts.md | Guided and free conversation formats |
| translation-exercises.md | English-to-Spanish and Spanish-to-English drills |
| listening-comprehension.md | Formats for processing audio/video homework |
| reading-exercises.md | Comprehension, discussion, and vocabulary extraction |
| writing-exercises.md | Journal, composition, and structured writing formats |
| fluency-drills.md | Timed monologues, speed translation, shadowing, retelling |
| dictation.md | Listening and transcription exercises |
| storytelling.md | Narrative production in past tenses |
| role-play-scenarios.md | Situational practice (restaurant, directions, shopping) |
| error-correction.md | How to structure error review during and after activities |
| grammar-in-context.md | Integration exercises combining multiple grammar concepts |
