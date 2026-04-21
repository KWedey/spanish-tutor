# Phase Transition Assessment Guide

Loaded when: All prerequisites for the next phase show "acquired" for 2+ consecutive sessions.

## Framing — Critical

- **Never** say "I'm going to assess you" or "this is a test."
- Frame as natural conversation: "Let's talk about your week."
- If learner shows anxiety, back off and retry next session embedded in normal conversation.
- If learner clearly fails, don't label it — note gaps, continue in current phase, retry in 2 weeks.

## A → B Assessment (15-20 min)

**Production (10 min):** "Tell me about your typical week — what you do, where you go, what you like and don't like."
- Tests: present regular + irregular, ser/estar, gender agreement, gustar-type, questions

**Receptive (5 min):** Play 60-sec Dreaming Spanish clip at Beginner level. Ask: "¿De qué habló?"
- Tests: listening comprehension + production

**Repair check:** Tutor deliberately uses one unfamiliar word mid-conversation.
- Tests: automatic repair phrase deployment

**Pass criteria:**
- A-01, A-02, A-04 at <10% production error
- Repair phrases automatic
- Can sustain 3+ minutes of guided conversation

**Borderline:** Extend 1-2 weeks, focus on weakest prerequisite.

**Core prerequisites (must be acquired — gate advancement):**
- A-01 (present regular)
- A-02 (ser vs estar)
- A-04 (articles/prepositions)

**Secondary prerequisites (may carry over — do NOT gate advancement):**
- A-03 (gender agreement) — see Critical dependency note below
- A-05 (basic questions)
- A-06 (gustar-type verbs)
- A-07 (present irregular)
- A-08 (numbers/quantifiers)
- A-09 (accent/stress)

*Note: A-00 (communication repair phrases) is not listed here. A-00 is a first-session exit requirement governed by the CLAUDE.md Guardrail "Communication repair phrases are the highest-priority concept through session 5" — it is not a phase A→B transition gate.*

**Critical dependency note:** While A-03 (Gender Agreement) is not a hard prerequisite for Phase B entry, it IS a prerequisite for B-06 (Direct Object Pronouns) and B-10 (Comparatives/Superlatives). If A-03 is carried over, it must reach "acquired" status before B-06 is introduced. The decision engine enforces this via prerequisite filtering, but the tutor should prioritize A-03 consolidation in early Phase B sessions.

## B → C Assessment (25-30 min)

**Production (12 min):** "Tell me about something that happened last week, and what you're planning for this weekend."
- Tests: preterite/imperfect contrast, future (ir+a), object pronouns, reflexives

**Writing (5 min):** Brief narration task. "Write me a short paragraph about what you did last weekend — 4-6 sentences."
- Tests: written accuracy under time pressure, spelling conventions, accent marks
- Compare written error rate to spoken error rate — divergence reveals whether errors are knowledge gaps (appear in both) or production pressure artifacts (spoken only)

**Receptive (8 min):** Listen to 2-min podcast excerpt at natural speed. Answer comprehension questions in Spanish.

**Pass criteria:**
- B-01, B-04 at <10% production error
- Appropriate past tense selection >80% of the time
- Can narrate event sequence without reverting to present tense
- Writing sample shows functional accuracy (minor errors acceptable; systematic grammar errors = not ready)

**Borderline:** Extend 2-3 weeks. If only one prerequisite weak, focused sprint.

**Core prerequisites (must be acquired — gate advancement):**
- B-01 (preterite regular)
- B-04 (preterite vs imperfect)

**Secondary prerequisites (may carry over — do NOT gate advancement):**
- B-02 (preterite irregular)
- B-03 (imperfect)
- B-05 (reflexives)
- B-06 (direct object pronouns)
- B-07 (indirect object pronouns)
- B-08 (estar + gerund)
- B-09 (imperatives)
- B-10 (comparatives/superlatives)
- B-11 (future ir+a)

## C → D Assessment (30-38 min)

**Production (15 min):** "What would change about your city if you were mayor? I disagree with your first point — convince me."
- Tests: subjunctive triggers, conditional, por/para, compound tenses, opinion defense

**Writing (8 min):** Opinion piece. "Write a short response to this question: '¿Es mejor vivir en una ciudad grande o un pueblo pequeño?' Give your opinion with at least two reasons."
- Tests: written argumentation, connector usage, subjunctive in writing, register consistency
- At C→D, writing should show paragraph structure, opinion markers (creo que, me parece, aunque), and at least one subjunctive trigger used correctly
- Compare to spoken production — if writing is significantly weaker, the learner may need more writing practice before Phase D

**Receptive (10 min):** Read short opinion article (~300 words). Summarize argument and state agreement/disagreement in Spanish.

**Pass criteria:**
- C-01, C-04, C-06 at <10% production error
- Uses subjunctive unprompted in at least 2 contexts
- Can sustain an argument with connectors
- Writing sample demonstrates structured argumentation with appropriate connectors and at least one correct subjunctive usage

**Borderline:** Extend 2-4 weeks. Subjunctive is the usual blocker — if that's the gap, dedicated subjunctive sprint.

**Core prerequisites (must be acquired — gate advancement):**
- C-01 (present subjunctive)
- C-04 (conditional)
- C-06 (compound tenses)

**Secondary prerequisites (may carry over — do NOT gate advancement):**
- C-02 (subjunctive triggers)
- C-03 (formal future)
- C-05 (por vs para)
- C-07 (relative clauses)
- C-08 (indirect speech)
- C-09 (diminutives/augmentatives)

## Recording Results

Record the assessment outcome in a milestone file (`state/milestones/YYYY-MM-DD-phase-transition.yaml`) using the unified milestone schema with `type: phase-transition`. Include `phase_transition.assessment.production_task`, `receptive_task`, and `decision`.
