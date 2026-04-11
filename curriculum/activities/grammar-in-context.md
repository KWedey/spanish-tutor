# Grammar in Context

## Purpose

Integration testing — determines whether concepts that are individually solid remain accurate when
used simultaneously. Assesses the `integration_tested_with` field in the skill map. A concept is not
ready to be marked "acquired" if it breaks down when cognitive load increases.

Use after two or more concepts have each reached `performance_scaffolded: competent`. The question
this activity answers: "Does accuracy drop when they're combined?"

## Phase Suitability

All phases. The combinations change as new concepts are introduced. The format stays the same:
design an activity that **requires** using multiple concepts at once, without scaffolding individual
ones.

## Setup

1. Identify which concepts to combine. Use concepts that are individually at `scaffolded: competent`
   but have an empty `integration_tested_with` list.
2. Choose a topic or task that naturally requires ALL selected concepts — don't force it.
3. Give clear task instructions without reminding the learner which grammar rules apply. If they
   need a reminder, the integration test isn't valid yet.
4. Choose between written, oral, or timed mode depending on what you want to assess (see
   Variations).

## How to Run

1. Frame the task clearly: "Describe your house to me. Tell me what's in each room."
2. Do NOT say "remember to use gender agreement" or "make sure you use present tense" — the
   point is to observe without scaffolding.
3. Note errors that were absent in isolated practice. These are integration failures.
4. After the activity, debrief specifically: "When you described the blue chairs — you said 'sillas
   azul' — that's the kind of agreement slip we're looking for."

**Assessment logic:**
- Accuracy on Concept A alone: competent
- Accuracy on Concept A while also managing Concept B: if errors appear → do not add to
  `integration_tested_with`. Continue combined practice.
- If no new errors emerge in 2-3 integration attempts → add tested concept IDs to `integration_tested_with`

## Example Combinations by Phase

### Phase A

| Task | Concepts Combined | What to Watch |
|------|------------------|---------------|
| "Describe your house — rooms, furniture, colors" | A-01 (present) + A-03 (gender agreement) | Does gender agreement slip on adjectives? |
| "Describe three people you know" | A-02 (ser/estar) + A-03 (agreement) + A-04 (articles) | Ser/estar distinction under load; article gender |
| "Tell me about your morning routine — use at least 5 verbs" | A-01 + A-05 (questions/negation) | Negation with irregular verbs; question word accuracy |
| "What do you like and dislike about your city?" | A-06 (gustar) + A-03 (agreement) | Gustar number agreement (gustan vs gusta) |

### Phase B

| Task | Concepts Combined | What to Watch |
|------|------------------|---------------|
| "Tell me about a childhood memory" | B-01 (preterite) + B-03 (imperfect) + B-04 (aspect) | Preterite/imperfect distinction in free production |
| "Describe what you were doing when something happened" | B-03 (imperfect) + B-08 (progressive) | Progressive overuse for habitual actions |
| "Give me directions from here to your home" | B-09 (imperatives) + A-04 (prepositions) | Pronoun placement with commands |

### Phase C

| Task | Concepts Combined | What to Watch |
|------|------------------|---------------|
| "Tell me what your friend said to you last week" | C-08 (indirect speech) + B-04 (preterite/imperfect) | Tense shifting in indirect speech |
| "Compare two places you've lived" | B-10 (comparatives) + C-05 (por/para) + C-06 (compound) | De vs que; por/para under load |

## What to Assess

Record after the activity:

```yaml
observations:
  - concept: "A-01-present-regular"
    context: unscaffolded
    assessment: competent
  - concept: "A-03-gender-agreement"
    context: unscaffolded
    assessment: struggling  # was fine in isolation — integration failure
```

Update skill map:
- If both concepts are competent under integration: add each concept's ID to the other's `integration_tested_with` list
- If one or both slip: do not update `integration_tested_with`, add targeted note on what combination
  caused the breakdown

## Variations

- **Written version:** Learner types their response. More processing time — tests knowledge, not
  automaticity. Good for first integration check on a new combination.
- **Oral version:** Learner speaks without pause for writing. Reveals whether the concept is
  automatic enough to survive real-time demands. Use after written version passes.
- **Timed version:** Give the learner 60 seconds to produce as much as possible on a topic.
  Stress test — cognitive load is highest. Use only after oral version passes consistently.

## Common Failure Patterns

- **Regression under load:** Learner uses correct gender agreement in isolation but drops endings
  when managing verb conjugation at the same time. → More integrated drilling before updating
  `integration_tested_with`.
- **Concept avoidance:** Learner uses simpler vocabulary or sentence structures to avoid the
  difficult combination. → Maneuver the topic to require the avoided structure.
- **Serial correctness:** Learner gets one concept right per sentence but not both. → Not yet
  automatic. Continue integration practice.
- **False integration test:** Task was possible without using one of the target concepts.
  → Redesign the task.
