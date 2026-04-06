# Conversation Prompts

## Purpose

Develops spontaneous production and fluency. Assesses `performance_unscaffolded` for active grammar
concepts. Used in the Conversation Practice block of every standard session (5-10 min). Also used
for warm-up diagnostics and post-homework verification.

## Phase Suitability

- **Phase A:** Heavily scaffolded. Tutor asks specific questions, learner answers. Simple topics,
  short turns, frequent comprehension checks.
- **Phase B:** Tutor opens topic, asks follow-ups. Learner expected to volunteer information, not
  just answer.
- **Phase C:** Learner takes more initiative. Tutor challenges and redirects. Mix of open and
  targeted prompts.
- **Phase D:** Fully open. Learner leads. Tutor functions as a native speaker would — reacts,
  disagrees, asks for clarification.

## Setup

No materials needed. Choose a topic that naturally elicits the session's active grammar concepts.
Check `curriculum/topic-bank.yaml` for grammar_alignment and vocabulary_alignment.

Decide the mode before starting:
- **Guided** — tutor drives with questions (Phase A default)
- **Partner** — both sides contribute equally (Phase B-C default)
- **Open** — learner leads (Phase D default)

## How to Run

### Basic Version (Phase A-B)

1. Name the topic clearly: "Let's talk about your daily routine."
2. Open with a simple question: "¿Qué haces por la mañana?"
3. After the learner responds, ask one follow-up. Don't jump to a new question immediately.
4. If the learner stalls, offer a scaffold: "Do you wake up early or late?" / "¿Temprano o tarde?"
5. Note errors silently — do NOT correct mid-conversation. Mark them for post-conversation review.
6. Run 8-12 exchanges. End before the learner runs out of language.
7. Post-conversation: Give 2-3 targeted corrections from your notes. Highlight 1-2 things done well.

### Advanced Version (Phase C-D)

1. Announce the topic but let the learner open: "Hablemos de tu trabajo — tú empiezas."
2. Respond as a conversational partner, not an interviewer. Add your own opinions.
3. Correct only when meaning is genuinely impeded. Let other errors pass.
4. If the learner avoids a structure, maneuver the conversation to require it naturally.
5. Run 10-20 exchanges. Allow natural pauses.
6. Post-conversation: 2 corrections maximum. Focus on fossilized errors or session-focus concept.

## What to Assess

Record after the activity in the session log:

```yaml
observations:
  - concept: "[concept-id]"
    context: unscaffolded
    assessment: competent  # struggling or competent
```

Also note:
- Vocabulary gaps (words they reach for but don't have)
- Repair strategy use (do they use A-00 phrases when stuck?)
- Fluency indicators: hesitation length, self-correction rate, turn length
- Subject matter avoidance (consistently dodging certain verb tenses?)

## Variations

- **Low energy / short session:** Use yes/no scaffolding ("¿Tienes hermanos? ¿Uno o dos?").
  Reduce to 5-minute version with 6 exchanges max.
- **High energy / debate format:** Choose a mildly controversial topic ("¿Mejor la ciudad o el
  campo?"). Tutor takes the opposing side. Requires Phase B minimum.
- **Rapid-fire Q&A (5 min):** Tutor fires 10 short questions without follow-up. Learner answers
  in 1-2 sentences each. Good for warm-up diagnostics.

## Example Implementation

**Phase A | Topic: Daily Routine | Focus: A-01 present regular, A-02 ser/estar**

---

**Tutor:** ¿A qué hora te despiertas normalmente?

**Learner:** Mmm... I wake up at seven.

**Tutor:** En español — ¿A las siete? ¿O diferente?
*(Gentle redirect to Spanish, not a correction)*

**Learner:** Ah, sí. Me despierto a las siete.

**Tutor:** ¿Y qué haces primero — café o ducha?

**Learner:** Hmm... café primero. I like coffee a lot.

**Tutor:** *(notes internally: should use gustar construction but hasn't learned it yet — skip)*
Ah, ¿sí? ¿Qué tipo de café?

**Learner:** Café con leche. Es... ¿rico?

**Tutor:** Exacto, "es rico" — muy bien. ¿Desayunas mucho o poco?

**Learner:** Poco. Yo como... solo pan.

**Tutor:** *(notes internally: "Yo como" — subject pronoun overuse, A-01 target error)*
¿Nada más? ¿Solo pan?

**Learner:** Sí, solo pan. Después trabajo.

**Tutor:** ¿A qué hora empiezas a trabajar?

**Learner:** A las nueve. Trabajo en casa — es... conveniente.

**Tutor:** *(notes: "es conveniente" — correct ser usage!)*
Sí, trabajar desde casa es muy conveniente. ¿Te gusta?

**Learner:** Sí, me gusta mucho.
*(learner produced this naturally — flag as positive sign)*

---

**Post-conversation review (tutor):**

"Muy buen trabajo. Te entendí perfectamente. Dos cosas pequeñas:

1. 'Yo como solo pan' — in Spanish we usually drop the subject pronoun. Just 'Como solo pan.'
   You said 'Yo' three times. It sounds a bit emphatic when every sentence has it.
2. You said 'I like coffee' in English — next session we'll learn the Spanish way to say that.

And something you did really well: 'Es rico' and 'es conveniente' — perfect ser usage. You're
applying that without thinking."
