# Fluency Drills

## Purpose

Builds automaticity, reduces hesitation, and increases speaking pace. The goal is to shift
known language from deliberate retrieval to automatic production. Used in the Conversation
Practice block or as a warm-up for Phase C+ sessions. These drills do not teach new concepts —
they accelerate the internalization of concepts already at "practicing" or "competent" status.

## Phase Suitability

- **Phase A-B:** Not recommended. The learner is still building the underlying language. Pushing
  speed before accuracy is established reinforces errors.
- **Phase C:** Primary home for fluency drills. Enough language is in place that automaticity
  work is productive. Use timed monologues and speed translation.
- **Phase D:** Shadowing and retelling with authentic, unscripted native audio. Full real-time
  production at near-native speed.

## Setup

Fluency drills require the learner to be in the right frame of mind. They can feel uncomfortable
— the goal is to push past the comfort zone of careful, error-free speech. Warn the learner:
"This one is about speed, not perfection. Errors are fine. Don't stop to self-correct."

Select active concepts for the drill — only structures the learner has been practicing. Do not
use fluency drills to introduce or consolidate a struggling concept.

## How to Run

### Basic Version (Phase C)

**Timed Monologue:**
1. Give the learner a topic: "Talk about your morning routine" or "Describe your ideal vacation."
2. The rule: speak for 2 minutes without stopping. No editing, no silence exceeding 5 seconds.
3. Tutor does not interrupt. Note hesitations, self-corrections, and circumlocutions silently.
4. After 2 minutes: brief debrief — 1-2 observations on fluency, 1 thing done well.
5. Optionally repeat the same topic immediately. Second attempt is almost always smoother.

**Speed Translation:**
1. Deliver 8-10 simple English sentences at a steady clip (one every 10-12 seconds).
2. Learner translates each one immediately — no time to plan.
3. Move on after each sentence whether the answer was right or not.
4. After all sentences: review 2-3 that the learner struggled with. Identify why (speed vs
   gap).

### Advanced Version (Phase D)

**Shadowing:**
1. Find a 1-2 minute clip of a native speaker on a familiar topic (Dreaming Spanish advanced,
   a short podcast segment).
2. Learner listens once for comprehension.
3. Learner plays the clip again, speaking along simultaneously at the speaker's pace.
4. Do not stop for errors — the goal is synchronization.
5. Debrief: "What parts were hardest to keep up with? Any sounds or connections you noticed?"

**Retelling:**
1. Learner listens to a 1-2 minute story or explanation in Spanish.
2. Learner retells it from memory in their own words (2 minutes).
3. Listen again.
4. Learner retells it a second time. Compare first and second attempt.
5. The improvement between attempts is the learning. Highlight what was added or smoother.

## What to Assess

Fluency metrics are qualitative — do not count like scaffolded accuracy. Estimate from
observation:

```yaml
fluency_metrics:
  pace: moderate          # slow, moderate, near-native
  hesitation_frequency: occasional  # frequent, occasional, rare
  self_correction_rate: high  # high (stops to fix), moderate, low (keeps going)
  circumlocution_use: effective  # avoided (freezes instead), effective, overused
```

Note: these are lower-confidence observations because production is typed in session. Spoken
fluency is better assessed through Speechling reports and italki feedback when available.

## Variations

- **Low energy version:** Skip timed monologue. Use speed translation only (5 sentences, slow
  pace). Lower stakes, still builds retrieval automaticity.
- **Topic ladder:** Start with a concrete, easy topic (daily routine), then pivot mid-monologue
  to a harder topic (an opinion on something). Tests whether fluency holds when the difficulty
  increases.
- **Second-attempt retelling:** Especially powerful as homework — learner records themselves
  retelling the same story twice, 10 minutes apart. The difference is the learning. Ask them to
  note what improved.

## Example Implementation

**Phase C | Timed Monologue | Topic: A recent trip or outing**

---

**Tutor:** Esta actividad es de fluidez — no de perfección. Habla durante dos minutos sobre
un viaje o salida reciente. No importan los errores. ¿Listo?

**Learner:** Okay. Mmm... el fin de semana pasado fui a... a la montaña con mi familia.
   Fuimos en coche, tardamos... uh... dos horas. La montaña era muy bonita. Había mucha nieve.
   Mis hijos... mis hijos estaban... uh... emocionados. Jugaron en la nieve y... y nosotros...
   nosotros caminamos un poco. El aire era... muy fresco. *(5-second pause)* Comimos en un
   restaurante pequeño cerca de... de la montaña. El menú tenía platos... platos típicos de
   la región. Pedí... pedí un caldo de pollo porque hacía mucho frío. *(pause)* Mmm...
   creo que eso es todo.

*(1 minute 45 seconds — close to target)*

---

**Tutor debrief:**

"Muy bien — casi dos minutos, y no paraste. Dos observaciones:

1. La fluidez en la primera mitad fue buena. Te costó más cuando describiste lo que hicieron
   los niños — la próxima vez no busques la palabra exacta, describe con lo que tienes.
2. El preterito e imperfecto: los usaste bien — 'la montaña *era* muy bonita,' 'el aire *era*
   fresco,' pero 'jugaron,' 'comimos,' 'pedí' — los tiempos están bien distribuidos.

¿Quieres intentarlo de nuevo con el mismo tema? La segunda vez siempre es más fácil."
