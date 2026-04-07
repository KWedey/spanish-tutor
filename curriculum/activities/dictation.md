# Dictation

## Purpose

Connects listening to writing. Tests spelling, accent mark awareness, and word boundary
perception simultaneously. Reveals gaps between what the learner hears and what they can
reproduce. Used in the Main Lesson block as a controlled practice activity, or as a homework
verification tool to assess whether listening improvement is transferring to accurate transcription.

## Phase Suitability

- **Phase A-B:** Tutor dictates 5 short sentences slowly, with a brief pause between words.
  Familiar vocabulary only. Focus on basic spelling and accent marks.
- **Phase C:** Moderate speed, longer sentences. Learner transcribes without replay. Accent
  marks and word boundaries are assessed rigorously.
- **Phase D:** Authentic audio clip (30-60 seconds). Learner transcribes in full. No speed
  reduction. Natural connected speech features (linking, reduction) are part of the challenge.

## Setup

Select sentences or a passage that includes:
- The current session's focus concept (for targeted assessment)
- At least 2-3 words with accent marks
- A mix of familiar and recently-introduced vocabulary

In Phase A-B: the tutor reads aloud (in text format, simulate by writing clearly). In Phase C-D:
use an audio clip from a known resource (Dreaming Spanish, a podcast, or a short news clip).

State the rules before starting:
- How many times will the audio/sentence be given? (Basic: twice. Advanced: once.)
- Should the learner write every word, or fill gaps in a partial transcript?

## How to Run

### Basic Version (Phase A-B)

1. Announce: "I'll read each sentence twice. Write exactly what you hear — spelling and accent
   marks count."
2. Deliver the first sentence at a slightly reduced pace. Pause between clauses.
3. Repeat the sentence once at normal speed.
4. Allow 20-30 seconds for the learner to write.
5. After all 5 sentences, ask the learner to share their transcription.
6. Compare to the original. Give immediate feedback on each sentence:
   - Correct accent marks? (¿qué vs que, él vs el, etc.)
   - Word boundaries correct? (e.g., "también" written as "tam bien" or "tambien")
   - Spelling errors that reflect a pronunciation gap?
7. Record accuracy:

```yaml
observations:
  - concept: "[focus-concept-id]"
    context: scaffolded
    attempts: 5
    errors: 2
dictation_notes: "Missed accent on 'estás' twice; 'también' written without accent. Word
  boundaries strong. No spelling errors on content words."
```

### Advanced Version (Phase C-D)

1. Play the audio clip once. Learner listens without writing.
2. Play again. Learner writes everything they hear.
3. Play a third time for checking only.
4. Review together: compare learner transcript to the source text (share the transcript after
   the exercise, not before).
5. Focus feedback on:
   - Connected speech gaps ("del" written as "de el," "al" as "a el")
   - Elided sounds in rapid speech (missing syllables in fast native speech)
   - Accent marks on question words, stressed syllables

## What to Assess

- **Accent mark accuracy:** Are the required accent marks present? (This is the most commonly
  neglected area in learner writing.)
- **Spelling accuracy:** Distinguish sound-based errors (wrote "aser" for "hacer") from
  careless errors (wrote "haer" for "hacer"). Sound-based = gap. Careless = slip.
- **Word boundary perception:** Are multi-syllable words being heard as separate units? This
  often reveals connected speech blindness.
- **Comprehension:** If the learner transcribed a wrong word entirely, was it because they
  misheard or because they don't know the word? Ask: "What did you think that word was?"

## Variations

- **Partial dictation (fill-gaps):** Give the learner the passage with key words or phrases
  blanked out. They fill in what they hear. Lower cognitive load than full transcription.
  Good for Phase A-B introduction to the format.
- **Running dictation (memory challenge):** Write the sentences on a card. Learner reads one
  sentence, walks away from the card, and writes it from memory. Tests retention alongside
  transcription. Good energy activity for Phase B.
- **Peer dictation (homework variant):** Learner records themselves reading 5 sentences aloud
  and transcribes the recording. Self-correction exercise — they hear their own accent
  reflected in a transcription task.

## Example Implementation

**Phase B | 5 sentences | Focus: B-04 preterite vs imperfect**

Sentences dictated:

1. Cuando era niño, vivía en una ciudad pequeña.
2. Ayer comí tacos por primera vez en mi vida.
3. Llovía mucho cuando salimos del trabajo.
4. ¿Dónde estabas anoche? No te vi en la reunión.
5. De repente, el perro empezó a ladrar.

---

**Learner's transcription:**

1. Cuando era niño, vivia en una ciudad pequeña.
   *(missing accent on "vivía" — accent error)*
2. Ayer comí tacos por primera vez en mi vida.
   *(correct)*
3. Llovía mucho cuando salimos del trabajo.
   *(correct)*
4. ¿Donde estabas anoche? No te vi en la reunion.
   *(missing accent on "Dónde" and "reunión")*
5. De repente, el perro empezo a ladrar.
   *(missing accent on "empezó")*

---

**Tutor feedback:**

"Muy bien con el contenido — entendiste las cinco frases perfectamente. El patrón que veo:
los acentos en los verbos ('vivía,' 'empezó') y en las palabras interrogativas ('dónde').
Estos acentos cambian el significado o el tiempo verbal, así que son importantes.

'Vivía' sin acento se leería igual, pero 'empezó' sin acento se ve como una forma diferente.
Practica escribir esos acentos — te recomiendo buscar en Anki reglas de acento la próxima vez."
