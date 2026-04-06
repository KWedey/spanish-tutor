# Translation Exercises

## Purpose

Builds accuracy through controlled production. Assesses `performance_scaffolded` for the target
concept. Used in the Main Lesson block during Stage 2 (Controlled Practice) of the teaching
sequence. Also used for warm-up verification or quick regression checks.

## Phase Suitability

- **Phase A-B:** Primary controlled practice tool. High frequency. Sentence-level exercises.
- **Phase C-D:** Used selectively for introducing complex new structures. Paragraph mode preferred
  over individual sentences once concepts are stable.

## Setup

Select 8-10 sentences (basic) or 1 paragraph (advanced) that specifically target the active
concept. All sentences should require the learner to use the target structure. Avoid sentences that
can be avoided — if the learner can answer without using the target concept, redesign the sentence.

Two modes:
- **English → Spanish (production):** Tests active recall and accuracy.
- **Spanish → English (comprehension):** Tests recognition. Use for exposure-level concepts or when
  introducing new vocabulary.

## How to Run

### Basic Version (Phase A-B)

1. Announce the mode: "I'll give you English sentences. You translate each one into Spanish."
2. Deliver sentences one at a time — do not give the full list upfront.
3. Wait for the learner's response before providing feedback.
4. After each response: give immediate, brief feedback. Model the correct form if wrong.
5. Move on. Do not dwell on errors — they are being logged for the session review.
6. After all 8-10 sentences, give a brief summary: accuracy on target concept, one pattern to
   notice.

**Tracking (record after activity):**
```yaml
observations:
  - concept: "[concept-id]"
    context: scaffolded
    attempts: 10
    errors: 2
```

### Advanced Version (Phase C-D)

1. Give the learner a full paragraph in English to translate in writing (or orally for advanced).
2. Do not provide per-sentence feedback during the exercise.
3. After the learner finishes, review holistically: overall accuracy, register, naturalness.
4. Highlight 2-3 structural issues. Explain the pattern if it's a new error type.
5. Reverse translation (optional): learner translates their own Spanish output back to English
   to catch unnatural constructions.

## What to Assess

- Accuracy on the target concept (count errors vs attempts — feeds `error_rate_recent`)
- Response latency: long pauses on target structure = concept not yet automatic
- Self-corrections: learner catches own error before feedback = good monitor awareness
- Which sentence types trigger errors (e.g., plural subjects but not singular)

## Variations

- **Speed round:** 30 seconds per sentence. Learner must commit to an answer. Tests automaticity.
  Do not use for new concepts — only for consolidation check.
- **Written vs spoken:** Written gives learner more processing time. Spoken reveals automaticity.
  Use spoken mode to simulate unscaffolded conditions.
- **Reverse translation:** Give the learner back their own Spanish translation and ask them to
  re-translate it to English. Surfaces unnatural constructions they didn't notice during production.

## Example Implementation

**Concept: A-01 Present Tense Regular | Mode: English → Spanish**

Target structures: -ar, -er, -ir regular verbs; no subject pronoun overuse.

| # | English prompt | Expected Spanish | Notes |
|---|---------------|-----------------|-------|
| 1 | I eat breakfast at home. | Como en casa. | Drop subject pronoun |
| 2 | She works in a hospital. | Trabaja en un hospital. | Drop subject pronoun |
| 3 | We live in the city. | Vivimos en la ciudad. | -ir nosotros ending |
| 4 | Do you drink coffee? | ¿Bebes café? | -er tú, question inversion |
| 5 | They study Spanish every day. | Estudian español todos los días. | -ar ellos ending |
| 6 | He writes emails all morning. | Escribe correos toda la mañana. | -ir él ending |
| 7 | I don't understand the question. | No entiendo la pregunta. | Negation + -er |
| 8 | You (formal) speak very well. | Habla muy bien. / Usted habla muy bien. | Usted = 3rd person |
| 9 | We open the store at nine. | Abrimos la tienda a las nueve. | -ir nosotros |
| 10 | They sell fresh bread here. | Venden pan fresco aquí. | -er ellos; adjective post-noun |

**Sample feedback flow:**

Sentence 1: Learner says "Yo como en casa."
→ "Almost — 'Como en casa' is more natural. In Spanish, the pronoun is usually dropped unless
   you're emphasizing contrast. We'll come back to this pattern."

Sentence 4: Learner says "¿Tú bebes café?"
→ "Correct — and you can also say just '¿Bebes café?' without 'tú.' Both are fine here."

Sentence 8: Learner says "Hablas muy bien."
→ "I said 'formal you' — that's usted, which takes the same ending as él/ella. 'Habla muy bien.'
   This catches a lot of people."

**Post-exercise summary:** "8 out of 10 correct on the verb endings — that's strong for a first
pass. The main pattern to watch: Spanish drops subject pronouns much more often than English uses
them. You used 'yo' or 'tú' in 4 sentences where it wasn't needed."
