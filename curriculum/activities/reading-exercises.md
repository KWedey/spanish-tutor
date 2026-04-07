# Reading Exercises

## Purpose

Builds reading comprehension and expands vocabulary through context. Used to verify reading
homework and assess `receptive_skills.reading` fields in the skill map. Deployed during the
Review block (homework check) or as a Main Lesson activity when the reading level has just been
stepped up and the tutor needs to gauge comprehension.

## Phase Suitability

- **Phase A:** Graded readers at A1-A2 (e.g., Español en marcha readers). Simple sentence
  structures, familiar vocabulary. Discussion in English allowed.
- **Phase B:** Graded readers at B1, adapted articles. Discuss in a mix of English and Spanish.
  Extract and analyze vocabulary.
- **Phase C-D:** Authentic articles, news, short stories, essays. Full Spanish discussion.
  Debate the argument. Analyze style and register.

## Setup

Confirm the learner completed the reading before starting. If not, do a brief in-session read
(5 minutes max) of one section, then debrief on that section only.

Know the resource:
- Source and level (graded-A1, graded-B1, adapted, authentic-simple, authentic)
- Topic and estimated vocabulary load
- Whether the goal is extensive (pleasure/gist) or intensive (analysis/accuracy)

Two reading modes to decide in advance:
- **Extensive** — read for pleasure or broad comprehension. No stopping for unknown words.
  Used for fluency and habit building.
- **Intensive** — analyze every sentence, extract vocabulary, discuss structure. Used for
  targeted skill development.

## How to Run

### Basic Version (Phase A-B)

1. Ask the learner to summarize the chapter or passage in 2-3 sentences. English is fine in
   Phase A; Spanish preferred in Phase B.
2. Comprehension probe — 2-3 questions scaling from gist to detail:
   - "What happened in this chapter?"
   - "Why did the character do X?"
   - "What was the outcome at the end?"
3. Vocabulary extraction: "What were 3-5 words you looked up or didn't recognize?" Review them
   together. Decide which ones are worth adding to Anki.
4. Brief discussion: "Did you enjoy it? Was it too easy, too hard, or about right?"

### Advanced Version (Phase C-D)

1. Learner summarizes unprompted in Spanish (3-5 sentences).
2. Ask one inference or analysis question: "What is the author's argument?" / "What assumptions
   is the author making that you agree or disagree with?"
3. Invite debate: present a counter-argument or opposing viewpoint. Learner defends or
   reconsiders.
4. Vocabulary focus: select 2-3 high-value words from the text and explore their collocations
   and usage. Do not just translate — show how the word behaves in context.
5. If written response was assigned: review it now (see writing-exercises.md for correction
   protocol).

## What to Assess

Update `receptive_skills.reading` in the skill map after the activity:

```yaml
receptive_skills:
  reading:
    current_level: graded-B1    # graded-A1, graded-A2, graded-B1, adapted, authentic-simple, authentic
    comprehension_quality: main-ideas  # gist, main-ideas, detailed, near-native
    lookup_frequency: occasional       # constant, frequent, occasional, rare
    notes: "Understood main plot; vocabulary gaps in figurative language"
```

Also note:
- Whether the learner is ready to level up (lookup_frequency = "rare" → consider stepping up)
- Whether the level is too hard (lookup_frequency = "constant" → step down)
- Vocabulary clusters that need reinforcement based on gaps surfaced

## Variations

- **Extensive reading:** Assign a chapter with no comprehension questions. Just ask "Did you
  enjoy it?" and check in briefly. Build the habit of reading for pleasure. Use for Phase B+
  when fluency is the goal over accuracy.
- **Intensive reading:** Pick one dense paragraph. Read it together. Analyze every sentence:
  structure, word choice, grammar. Time-consuming — use selectively.
- **Jigsaw reading:** Assign two different sections to cover in one session. Learner summarizes
  their section in Spanish; tutor summarizes the other. Learner must ask questions to fill their
  knowledge gap. Builds production alongside comprehension. Phase C+.

## Example Implementation

**Phase B | Resource: Graded reader chapter, B1 level | Topic: A trip to Buenos Aires**

---

**Tutor:** ¿Leíste el capítulo esta semana?

**Learner:** Sí, lo leí. Fue interesante.

**Tutor:** ¿De qué trataba el capítulo?

**Learner:** Mmm... la protagonista llegó a Buenos Aires por primera vez. Estaba muy... emocionada?
   Y buscaba a su amiga, pero su amiga no estaba en su apartamento.

**Tutor:** Muy bien. ¿Por qué no estaba la amiga?

**Learner:** Creo que... salió a trabajar? No estoy seguro. Había una nota en la puerta.

**Tutor:** Exacto — dejó una nota. ¿Qué palabras buscaste o no reconociste?

**Learner:** "Madrugada" — no sabía qué significaba.

**Tutor:** "Madrugada" — las horas entre medianoche y el amanecer. Muy diferente de "mañana,"
   que empieza a las 6:00 más o menos. Es una palabra muy útil en narrativa. ¿Algo más?

**Learner:** "Portero" — pensé que era algo como "goalkeeper" en fútbol.

**Tutor:** ¡Buen instinto! "Portero" puede ser un portero de fútbol, pero en este contexto es
   el encargado del edificio — el doorman o super. El contexto cambia el significado.

---

**Post-activity assessment:**

Update `comprehension_quality: main-ideas`. Learner following plot well. "Madrugada" and
"portero" both worth adding to Anki. Lookup frequency is occasional — current level is
well-matched. Consider authentic-simple material in 4-6 weeks if progress continues.
