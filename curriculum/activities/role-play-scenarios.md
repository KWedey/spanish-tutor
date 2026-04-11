# Role-Play Scenarios

## Purpose

Communicative practice where the focus is on **meaning**, not form. The learner must accomplish a
real-world goal using Spanish. Grammar accuracy is secondary — communication success is the primary
measure. Maps to Stage 4 (Communicative Practice) in the teaching sequence. Assesses whether
communication succeeds under real conditions.

## Phase Suitability

- **Phase A:** Controlled scenarios with concrete, predictable vocabulary. Tutor plays the other
  role generously (speaks slowly, gives hints if blocked).
- **Phase B:** More complex scenarios requiring past tense, object pronouns, reflexives. Tutor plays
  the role more realistically — doesn't slow down unless asked.
- **Phase C-D:** High-stakes or socially complex scenarios. Tutor plays the role at natural speed.
  Misunderstandings are part of the exercise.

## Setup

1. Name the scenario and assign roles clearly before starting.
2. State the learner's communicative goal: "Your goal is to order a meal and ask for the check."
3. Briefly establish context: "You're at a restaurant in Mexico City. I'm the server."
4. Do NOT pre-teach vocabulary — the learner should manage gaps using repair strategies (A-00).
5. Stay in Spanish throughout. If the learner switches to English mid-scenario, gently redirect:
   "En español — ¿cómo lo dices?"

## How to Run

1. Start the scenario: tutor opens with the first line in their role.
2. React authentically to what the learner says. If their Spanish is unclear, respond as a
   real speaker would — ask for clarification in Spanish, not English.
3. Let the learner make mistakes without stopping them. Note errors for post-scenario review.
4. If the learner completely freezes, offer one prompt in Spanish: "¿Qué quieres decir?"
5. Run until the communicative goal is achieved (or 5-7 minutes, whichever comes first).
6. Step out of the role: "Okay, let's debrief."

**Assessment after the scenario:**
- Did the learner accomplish the goal? (Yes / Partially / No)
- Grammar accuracy on session-focus concepts (secondary)
- Vocabulary range — did they manage gaps well?
- Repair strategy use — did they use A-00 phrases when stuck?

## Phase A Scenarios

| Scenario | Communicative Goal | Key Vocabulary |
|----------|--------------------|---------------|
| Ordering at a restaurant | Order food and drinks, ask for the check | food-restaurant cluster |
| Asking for directions | Get directions to a nearby location | directions-transportation cluster |
| Introducing yourself at a party | Exchange names, jobs, origins, interests | greetings-introductions cluster |
| Buying something at a store | Ask for a product, negotiate/confirm price, pay | numbers-time cluster |
| Checking into a hotel | Confirm reservation, ask about amenities | basic-descriptions + numbers |

## Phase C-D Scenarios

| Scenario | Communicative Goal | Key Concepts |
|----------|--------------------|-------------|
| Job interview | Answer questions, ask about the role | formal register, subjunctive |
| Polite disagreement | Express opposing view without being rude | conditional, C-04 |
| Explaining to a doctor | Describe symptoms accurately | reflexives, duration expressions |
| Negotiating a price | Reach agreement on a price | comparatives, B-10 |
| Arranging plans with a friend | Agree on time, place, activity | ir + a, B-11; imperatives, B-09 |

## What to Assess

Record after the activity:

```yaml
role_play_assessment:
  scenario: "ordering at a restaurant"
  goal_achieved: true  # true, partial, false
  repair_strategies_used: true
  notes: "Managed the order but forgot to use 'quisiera' — used 'quiero' throughout (acceptable). Used 'No entiendo' correctly when I spoke quickly."
```

Also note for the skill map:
- `performance_unscaffolded` for any active concepts exercised in free production
- Update `integration_tested_with` with tested concept IDs if multiple concepts were combined successfully

## Variations

- **Scaffolded version:** Give the learner a vocabulary card before starting ("Here are 5 words
  you might need"). Reduces anxiety for new scenarios. Phase A only.
- **Realistic difficulty:** Play the role with some natural speech features — connected speech,
  slight speed increase. Tests comprehension alongside production.
- **Repeat scenario:** Run the same scenario twice in the same session. First pass = learning run.
  Second pass = assess. Compare fluency and accuracy between attempts.

## Example Implementation

**Scenario: Ordering at a Restaurant | Phase A**

**Setup (tutor, in English):** "You're at a restaurant in Guadalajara. I'm the server. Your goal:
order food and drinks for yourself, and ask for the check at the end. Ready? — Buenas tardes."

---

**Tutor (as server):** Buenas tardes. ¿Qué le puedo traer?

**Learner:** Buenas tardes. Mmm... quiero... el pollo, por favor.

**Tutor:** ¿Con arroz o con ensalada?

**Learner:** Con... arroz. Y... agua, por favor.

**Tutor:** ¿Agua mineral o natural?

**Learner:** Uh... ¿Qué significa "mineral"?
*(uses A-00 repair phrase — note positively)*

**Tutor:** Con gas o sin gas — con burbujas o sin burbujas.

**Learner:** Ah, sin gas, por favor.

**Tutor:** Perfecto. *(pauses — waits for learner to ask for check)*

**Learner:** Mmm... la cuenta... ¿me trae la cuenta?

**Tutor:** Claro que sí. Un momento.

---

**Debrief (tutor steps out of role):**

Goal achieved: yes. Key observations:

- Used "quiero" throughout — grammatically fine, though "quisiera" is more polite in a restaurant
  (make a note for Phase B when conditionals are introduced).
- Correctly used "¿Qué significa...?" when stuck — excellent repair strategy use.
- "La cuenta, ¿me trae la cuenta?" — slight self-correction and restructuring, but it worked.
- Hesitated on asking for the check at the end — needed a pause. Practice using it as a
  fixed phrase: "La cuenta, por favor" or "¿Me trae la cuenta, por favor?"

Record in session log: `goal_achieved: true`, `repair_strategies_used: true`.
