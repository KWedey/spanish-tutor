# Listening Comprehension

## Purpose

Develops receptive skills and trains the ear for natural Spanish. Used to verify audio/video
homework and assess `receptive_skills.listening` fields in the skill map. Most commonly deployed
at the start of the Main Lesson block as homework verification, or as a standalone activity when
consolidating receptive input.

## Phase Suitability

- **Phase A:** Graded, slow-speed audio (Dreaming Spanish Comprehensible Input, Language Transfer).
  Tutor comprehension checks use simple yes/no and short-answer questions in English or Spanish.
- **Phase B:** Moderate-speed audio. Learner summarizes in Spanish. Some inference expected.
- **Phase C-D:** Authentic native-speed material. Deep comprehension, theme discussion, inference
  about unstated meaning, debate the content.

## Setup

Confirm the learner has completed the listening homework before starting. If not, adapt to an
in-session listen (3-5 minutes max) rather than skipping the activity entirely.

Know the resource in advance:
- Title and source (Dreaming Spanish, podcast, film clip, etc.)
- Level (beginner CI / intermediate CI / native speed)
- Topic and key vocabulary load
- What specifically to assess: gist only, or main ideas, or detailed comprehension?

## How to Run

### Basic Version (Phase A-B)

1. Ask the learner to summarize what the audio was about in 2-3 sentences. Spanish if Phase B,
   English allowed in Phase A.
2. Probe with 2-3 targeted comprehension questions:
   - Gist: "What was the main topic?"
   - Main ideas: "What were the two or three main points?"
   - Detail (if appropriate): "What specific example did they give for X?"
3. If the learner missed key content, note whether this is a vocabulary issue, speed issue, or
   topic-familiarity issue. Do not re-assign the same resource — adjust level or suggest a
   second listen with a specific focus.
4. Ask one connection question: "Did anything surprise you? Did it match what you expected?"

### Advanced Version (Phase C-D)

1. Learner gives a full summary unprompted. Tutor listens and notes gaps.
2. Ask 1-2 inference questions: "The speaker didn't say it directly, but what do you think they
   meant by X?" / "What was the speaker's attitude toward this topic?"
3. Invite a discussion or mild debate: "Do you agree with what they said? Why or why not?"
4. If the learner encountered unknown words: "What word or phrase did you not recognize? Can you
   infer the meaning from context?"
5. Assign follow-up: second listen with a specific focus, or a related resource one level up.

## What to Assess

Update `receptive_skills.listening` in the skill map after the activity:

```yaml
receptive_skills:
  listening:
    comprehension_quality: main-ideas  # gist, main-ideas, detailed, near-native
    speed_tolerance: moderate          # slow, moderate, natural
    notes: "Understood plot but missed the key contrast between X and Y"
```

Also note:
- Vocabulary gaps that surface during the debrief
- Whether the learner is under-reporting difficulty (claiming comprehension without evidence)
- Repair strategies when the learner summarizes — do they circumlocute gaps or freeze?

## Variations

- **Gist-then-detail:** First listen for overall meaning, second listen for specific details. Good
  for stepping the learner up to a harder resource without overwhelming them on first exposure.
- **Unknown-word log:** Learner notes 3-5 words they heard but didn't understand. Review in
  session: look them up, add Anki cards if core vocabulary.
- **Predict-then-listen:** Before playing, give the learner the title and 30 seconds to predict
  what it will be about. Compare prediction to actual content. Activates vocabulary and builds
  engagement.

## Example Implementation

**Phase B | Resource: Dreaming Spanish — Intermediate video on Mexican food**

---

**Tutor:** ¿Miraste el video de Dreaming Spanish esta semana?

**Learner:** Sí, lo vi.

**Tutor:** Bien. ¿De qué trataba? Cuéntame en español.

**Learner:** Mmm... hablaba de... comida mexicana. Diferentes tipos de... tacos, creo.
   Y también algo sobre... regiones? Diferentes regiones tienen diferentes comidas.

**Tutor:** Muy bien — captaste la idea principal. ¿Mencionó alguna región específica?

**Learner:** Creo que dijo Oaxaca. Y tal vez... Yucatán? No estoy seguro del segundo.

**Tutor:** *(confirms internally: Oaxaca and Veracruz were the two regions mentioned)*
Oaxaca sí, exacto. ¿Entendiste todo a esa velocidad, o fue difícil seguirlo?

**Learner:** Un poco difícil al principio, pero después más fácil.

**Tutor:** ¿Hubo alguna palabra que no reconociste?

**Learner:** Sí, dijo algo como... ¿"mole"? No sé qué es.

**Tutor:** ¡Mole! Es una salsa muy importante en la cocina mexicana — muy compleja, con chile y
chocolate entre otros ingredientes. Es una palabra importante si te interesa la comida mexicana.

---

**Post-activity assessment:**

Update `comprehension_quality: main-ideas`, `speed_tolerance: moderate`. Add "mole" to vocabulary
note. Learner is ready for native-speed short clips (2-3 minutes) next week if current trajectory
holds. Assign one more intermediate CI video before stepping up.
