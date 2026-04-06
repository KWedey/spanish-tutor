# Phase A + Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create all Phase A curriculum content — grammar concepts, tier-1 vocabulary, onboarding sessions, core activity templates, and Phase A pronunciation guides — making the system usable for a new learner.

**Architecture:** 29 new markdown files across 5 directories. Grammar and vocabulary files follow templates defined in the design spec (Section 7). Onboarding sessions reference grammar/vocabulary files. Activity templates are reusable formats. All Spanish content is verified for accuracy.

**Spec:** `docs/superpowers/specs/2026-04-06-curriculum-and-infrastructure-design.md`
**Templates:** Spec Sections 7.1 (grammar), 7.2 (vocabulary), 7.3 (activity), 7.4 (onboarding), 7.5 (pronunciation)

**Content standard:** All Spanish grammar explanations, paradigm tables, example sentences, and vocabulary must be accurate. The subagent uses its Spanish language knowledge to generate content, then self-verifies critical items (conjugation tables, example sentences, gender assignments) against standard references.

---

## File Map

| Directory | Files | Count |
|-----------|-------|-------|
| `curriculum/grammar/A-foundation/` | 00 through 07 | 8 |
| `curriculum/vocabulary/tier1-survival/` | 5 cluster files | 5 |
| `curriculum/onboarding/` | session-01 through session-10 | 10 |
| `curriculum/activities/` | 4 core templates | 4 |
| `curriculum/pronunciation/` | 2 Phase A guides | 2 |
| **Total** | | **29** |

## Task Dependencies

Grammar files must be created before onboarding sessions (sessions reference them). Vocabulary files must be created before onboarding sessions. Activity templates should exist before onboarding sessions reference them. Pronunciation guides are independent.

**Order:** Tasks 1-4 (grammar) → Tasks 5-6 (vocabulary) → Task 7 (activity templates) → Task 8 (pronunciation) → Tasks 9-10 (onboarding sessions)

---

### Task 1: Grammar Files A-00 and A-01

**Files:**
- Create: `curriculum/grammar/A-foundation/00-communication-repair.md`
- Create: `curriculum/grammar/A-foundation/01-present-regular.md`

- [ ] **Step 1: Create A-00 communication repair**

Follow the grammar concept template from spec Section 7.1. This is concept #0 — survival phrases, not a grammar rule.

**Key content requirements:**
- Overview: These are the most immediately useful phrases. They transform a learner who freezes when stuck into one who can navigate uncertainty.
- The Pattern: No paradigm table — these are memorized phrases, not grammar.
- Core phrases (must be automatic by session 5):
  - "¿Puedes repetir, por favor?" / "¿Puede repetir, por favor?" (Can you repeat?)
  - "¿Qué significa [word]?" (What does [word] mean?)
  - "¿Cómo se dice [English word]?" (How do you say [word]?)
  - "No entiendo" (I don't understand)
  - "Más despacio, por favor" (More slowly, please)
  - "¿Puedes hablar más lento?" (Can you speak slower?)
- Circumlocution strategies (introduced sessions 3-5):
  - "Es como..." (It's like...)
  - "Es una cosa que..." (It's a thing that...)
  - "Es el lugar donde..." (It's the place where...)
- No L1 Interference section (not applicable)
- Teaching Sequence: memorization through role-play, not noticing activities
- Signs of Acquisition: uses phrases without hesitation when confused in conversation
- Connection Points: enables all future learning by giving the learner a safety net

- [ ] **Step 2: Create A-01 present tense regular**

Follow the grammar concept template. This is the foundational grammar concept.

**Key content requirements:**
- Overview: Present tense regular conjugation is the foundation for all verb usage.
- Prerequisites: None
- L1 interference: subject-pronoun-overuse (English requires pronouns, Spanish drops them)
- The Pattern: Full conjugation paradigm for -ar (hablar), -er (comer), -ir (vivir). Show all 6 persons.
- Include "hay" (there is/there are) as a key irregular in the notes section
- Examples: 8-10 sentences using a mix of -ar/-er/-ir verbs in natural contexts. Include subject-dropped examples ("Vivo en la ciudad" not "Yo vivo en la ciudad").
- Common Errors: subject pronoun overuse, -er/-ir confusion (comemos vs vivimos), stem stress errors
- Teaching Sequence Stage 1: Show 6 sentences using the same -ar verb with different subjects. Ask "What pattern do you see in the endings?"
- Stage 2: Fill-in conjugation drills, English→Spanish translation with subject pronoun dropping
- Stage 3: "Tell me about your typical day" using at least 5 different verbs
- Stage 4: "Describe what your family members do on a typical weekday"
- Dialect Notes: vosotros (Spain only) — skip for Latin American learners
- Signs of Acquisition: Scaffolded = correctly conjugates in drills without hesitation. Unscaffolded = uses correct endings in free conversation, drops subject pronouns naturally. Integrated = maintains correct conjugation when combining with adjectives, prepositions.
- Connection Points: Foundation for A-02 (ser/estar uses same conjugation concept but irregular), A-06 (gustar reverses the subject pattern learned here), all Phase B concepts.

- [ ] **Step 3: Verify files**

Check both files exist and are well-formed markdown:
```bash
ls -la curriculum/grammar/A-foundation/00-communication-repair.md curriculum/grammar/A-foundation/01-present-regular.md
```

Verify A-01 contains conjugation paradigm:
```bash
grep -c "habl" curriculum/grammar/A-foundation/01-present-regular.md
```
Should be > 5 (multiple conjugated forms).

- [ ] **Step 4: Commit**

```
git add curriculum/grammar/A-foundation/00-communication-repair.md curriculum/grammar/A-foundation/01-present-regular.md
git commit -m "feat: add grammar concepts A-00 (communication repair) and A-01 (present regular)"
```

---

### Task 2: Grammar Files A-02 and A-03

**Files:**
- Create: `curriculum/grammar/A-foundation/02-ser-vs-estar.md`
- Create: `curriculum/grammar/A-foundation/03-gender-agreement.md`

- [ ] **Step 1: Create A-02 ser vs estar**

**Key content requirements:**
- Prerequisites: A-01-present-regular
- L1 interference: ser-estar-confusion (HIGH severity — English has one "to be")
- The Pattern: Full conjugation for both ser and estar. Clear categorization:
  - SER: identity, origin, profession, characteristics, time, material, possession
  - ESTAR: location, temporary states, emotions, progressive tense, results of actions
  - Mnemonic aids welcome (e.g., DOCTOR/PLACE or similar)
- Examples: 8-10 contrast pairs showing the same subject with ser vs estar (e.g., "Es aburrido" = He's boring vs "Está aburrido" = He's bored)
- L1 Interference preemption: "In English you say 'I am tired' with the same verb as 'I am a teacher.' In Spanish, being tired is a state (estar) but being a teacher is identity (ser)."
- Common Errors: "Soy cansado" (should be Estoy), "Está un profesor" (should be Es), location with ser
- Teaching Sequence Stage 1: Show 6 sentences with ser and 6 with estar. Ask learner to sort them — what's different about the two groups?
- Dialect Notes: Some regional variations in estar usage (Caribbean uses estar more broadly)
- Connection Points: Reinforces A-01 conjugation. Enables A-04 (descriptions need ser/estar). Foundation for B-08 (progressive uses estar).

- [ ] **Step 2: Create A-03 gender and number agreement**

**Key content requirements:**
- Prerequisites: None
- L1 interference: adjective-placement (English puts adjectives before nouns)
- The Pattern:
  - Noun gender rules: -o/-a patterns, common exceptions (el día, la mano, el agua)
  - Number: -s after vowel, -es after consonant
  - Adjective agreement: must match noun in gender and number
  - Adjective placement: most adjectives AFTER the noun (unlike English)
  - **Demonstratives subsection:** este/esta/estos/estas, ese/esa/esos/esas, aquel/aquella/aquellos/aquellas
  - **Possessives subsection:** mi/mis, tu/tus, su/sus, nuestro/nuestra/nuestros/nuestras
- Examples: Include adjective placement contrasts ("una casa roja" not "una roja casa"), demonstrative usage, possessive usage
- Common Errors: adjective before noun (English transfer), forgetting agreement on adjectives, wrong gender on common exceptions
- Teaching Sequence Stage 1: Show pairs (el gato negro / la gata negra, los gatos negros / las gatas negras). Ask what pattern they see.
- Signs of Acquisition: Correct gender/number agreement in free production without self-correction pauses
- Connection Points: Enables A-04 (articles require gender knowledge), A-06 (gustar objects need articles with correct gender). Common regression trigger: gender agreement slips when cognitive load increases (past tenses, complex sentences).

- [ ] **Step 3: Verify and commit**

```bash
ls -la curriculum/grammar/A-foundation/02-ser-vs-estar.md curriculum/grammar/A-foundation/03-gender-agreement.md
grep -c "ser\|estar" curriculum/grammar/A-foundation/02-ser-vs-estar.md
```

```
git add curriculum/grammar/A-foundation/02-ser-vs-estar.md curriculum/grammar/A-foundation/03-gender-agreement.md
git commit -m "feat: add grammar concepts A-02 (ser vs estar) and A-03 (gender agreement)"
```

---

### Task 3: Grammar Files A-04 and A-05

**Files:**
- Create: `curriculum/grammar/A-foundation/04-articles-prepositions.md`
- Create: `curriculum/grammar/A-foundation/05-basic-questions.md`

- [ ] **Step 1: Create A-04 articles, prepositions, personal 'a'**

**Key content requirements:**
- Prerequisites: A-03-gender-agreement
- L1 interference: preposition-mapping (prepositions don't translate 1:1)
- The Pattern:
  - Definite articles: el, la, los, las (+ el before feminine words starting with stressed a: el agua)
  - Indefinite articles: un, una, unos, unas
  - Contractions: a + el = al, de + el = del
  - Common prepositions: a, de, en, con, por, para (basic usage only — por/para distinction is Phase C), sin, sobre, entre, hacia
  - **Personal 'a' subsection:** Required before human direct objects. "Veo a mi madre" not "Veo mi madre." No English equivalent.
- Key preposition contrasts with English: pensar en (think about), soñar con (dream about), depender de (depend on)
- Common Errors: omitting personal 'a', using "en" for "on" (English transfer), missing contractions
- Teaching Sequence Stage 1: Show sentences with and without personal 'a'. "Veo la mesa. Veo a María." Ask what's different.
- Connection Points: Personal 'a' becomes critical in B-06 (direct object pronouns). Prepositions revisited in C-05 (por vs para).

- [ ] **Step 2: Create A-05 basic questions and negation**

**Key content requirements:**
- Prerequisites: A-01-present-regular
- L1 interference: negative-double-negative (English avoids double negatives; Spanish requires them)
- The Pattern:
  - Question words: qué, quién/quiénes, dónde, cuándo, cómo, por qué, cuánto/cuánta/cuántos/cuántas, cuál/cuáles
  - Question formation: inversion (¿Hablas español?) or intonation (¿Tú hablas español?)
  - Negation: no before the verb. "No hablo español."
  - Double negatives: "No tengo nada" (not "No tengo algo"), "No veo a nadie" (not "No veo a alguien"), "Nunca como nada" = valid
  - Negative words: nada, nadie, nunca, ninguno/ninguna, tampoco, ni...ni
- Common Errors: avoiding double negatives (English transfer), wrong question word (qué vs cuál), forgetting accent marks on question words
- Teaching Sequence Stage 1: Show 5 questions and their answers. Ask learner to identify the question word pattern.
- Stage 4: "Interview me — ask me 10 questions about my life using different question words"
- Connection Points: Questions enable all conversation practice going forward. Negation patterns recur throughout all phases.

- [ ] **Step 3: Verify and commit**

```
git add curriculum/grammar/A-foundation/04-articles-prepositions.md curriculum/grammar/A-foundation/05-basic-questions.md
git commit -m "feat: add grammar concepts A-04 (articles/prepositions) and A-05 (questions/negation)"
```

---

### Task 4: Grammar Files A-06 and A-07

**Files:**
- Create: `curriculum/grammar/A-foundation/06-gustar-type-verbs.md`
- Create: `curriculum/grammar/A-foundation/07-present-irregular-common.md`

- [ ] **Step 1: Create A-06 gustar-type verbs**

**Key content requirements:**
- Prerequisites: A-01-present-regular
- L1 interference: gustar-construction (HIGH severity, HIGH fossilization risk)
- The Pattern: FUNDAMENTALLY different from English. The thing liked is the SUBJECT, the person is the INDIRECT OBJECT.
  - "Me gusta el café" = Coffee pleases me (NOT "I like coffee")
  - Structure: indirect object pronoun + gustar (3rd person) + subject
  - Pronouns: me, te, le, nos, os, les
  - Singular vs plural: "Me gusta el café" vs "Me gustan los perros" (verb agrees with the subject, not the person)
  - Verbs that follow this pattern: gustar, encantar, molestar, importar, interesar, fascinar, doler, faltar, parecer
  - Emphasis/clarification: "A mí me gusta..." / "A ti te gusta..."
- L1 Interference preemption: "In English you say 'I like coffee' — you are the subject. In Spanish, it's reversed: 'Coffee pleases me.' The coffee is doing the action. This feels backwards, and your brain will fight it for weeks. That's normal."
- Common Errors: "Yo gusto el café" (treating gustar like English "like"), wrong number agreement ("Me gusta los perros" — should be gustan), omitting "a" in emphasis construction
- Teaching Sequence Stage 1: Show "Me gusta el café. Me gustan los libros." Ask why the verb changes — it's NOT because of "me."
- Signs of Acquisition: Uses gustar construction without reverting to English word order. Correctly uses singular/plural agreement with the subject.
- Connection Points: First exposure to indirect object pronouns (formalized in B-07). The reversed structure is a major conceptual shift that, once internalized, makes B-07 much easier.

- [ ] **Step 2: Create A-07 common irregular present**

**Key content requirements:**
- Prerequisites: A-01-present-regular
- The Pattern: Full conjugations for these high-frequency irregular verbs:
  - ir (voy, vas, va, vamos, vais, van)
  - tener (tengo, tienes, tiene, tenemos, tenéis, tienen)
  - querer (quiero, quieres, quiere, queremos, queréis, quieren)
  - poder (puedo, puedes, puede, podemos, podéis, pueden)
  - hacer (hago, haces, hace, hacemos, hacéis, hacen)
  - decir (digo, dices, dice, decimos, decís, dicen)
  - saber (sé, sabes, sabe, sabemos, sabéis, saben)
  - conocer (conozco, conoces, conoce, conocemos, conocéis, conocen)
  - hay (there is/there are — invariable for singular and plural)
- Group by irregularity type: stem-changing (e→ie: querer, tener; o→ue: poder), yo-irregular (hacer→hago, saber→sé, conocer→conozco), fully irregular (ir, decir)
- Saber vs conocer distinction: saber = know facts/how to; conocer = know/be familiar with people/places
- Common Errors: regularizing irregulars ("haco" for "hago"), saber/conocer confusion, "hay" pluralized ("hayen")
- Teaching Sequence: Group verbs by pattern, teach one group at a time. Start with stem-changing (most predictable), then yo-irregular, then fully irregular.
- Connection Points: These verbs appear in nearly every conversation. Ir enables B-11 (ir + a + infinitive for future). Tener in common expressions (tener hambre, tener sueño, tener razón).

- [ ] **Step 3: Verify and commit**

Verify A-06 has the gustar pattern clearly:
```bash
grep -c "gusta\|gustan" curriculum/grammar/A-foundation/06-gustar-type-verbs.md
```

Verify A-07 has all irregular verbs:
```bash
grep -c "voy\|tengo\|quiero\|puedo\|hago\|digo\|conozco" curriculum/grammar/A-foundation/07-present-irregular-common.md
```

```
git add curriculum/grammar/A-foundation/06-gustar-type-verbs.md curriculum/grammar/A-foundation/07-present-irregular-common.md
git commit -m "feat: add grammar concepts A-06 (gustar-type verbs) and A-07 (irregular present)"
```

---

### Task 5: Vocabulary Clusters — Greetings and Numbers

**Files:**
- Create: `curriculum/vocabulary/tier1-survival/greetings-introductions.md`
- Create: `curriculum/vocabulary/tier1-survival/numbers-time-dates.md`

- [ ] **Step 1: Create greetings-introductions cluster**

Follow vocabulary cluster template (spec Section 7.2).

**Key content requirements:**
- Cluster Meta: Phase A, core ~30, exposure ~15, grammar reinforcement [A-00, A-01, A-02]
- Core subtopics: Basic greetings (hola, buenos días/tardes/noches, ¿qué tal?, ¿cómo estás?), Introductions (me llamo, soy, mucho gusto, encantado/a), Farewells (adiós, hasta luego, hasta mañana, nos vemos, chao), Courtesy (por favor, gracias, de nada, perdón, disculpe, lo siento)
- Example sentences for: ¿Cómo estás? vs ¿Cómo está? (tú vs usted), mucho gusto (context of use), lo siento vs perdón (distinction)
- Collocations: mucho gusto en conocerte, ¿de dónde eres?, ¿a qué te dedicas?
- Dialect: chao (common in Latin America, less in Spain), ¿qué onda? (Mexico informal)
- Cultural notes: kissing on cheek, handshake norms, tú vs usted in greetings
- Pronunciation alerts: buenos (diphthong ue), gracias (stress on first syllable)

- [ ] **Step 2: Create numbers-time-dates cluster**

**Key content requirements:**
- Cluster Meta: Phase A, core ~30, exposure ~20, grammar reinforcement [A-01, A-02]
- Core subtopics: Numbers 0-100 (with patterns for 16-19, 21-29, 30-99), Time (¿Qué hora es?, Son las tres, Es la una, de la mañana/tarde/noche, mediodía, medianoche), Days of the week (lunes-domingo, lowercase in Spanish), Months (enero-diciembre, lowercase), Dates (el [number] de [month] — "el 5 de mayo")
- Example sentences for: time expressions with ser ("Son las dos y media"), date expressions ("Hoy es martes, el 15 de abril"), age with tener ("Tengo treinta años")
- Cultural notes: 24-hour clock usage, date format (dd/mm/yyyy), Monday as first day of week
- Common errors: "Son la una" (should be "Es la una" — singular), numbers agreement (doscientos vs doscientas)
- Pronunciation: stress patterns on numbers (dieciséis, veintitrés)

- [ ] **Step 3: Verify and commit**

```
git add curriculum/vocabulary/tier1-survival/greetings-introductions.md curriculum/vocabulary/tier1-survival/numbers-time-dates.md
git commit -m "feat: add tier-1 vocabulary clusters — greetings and numbers/time/dates"
```

---

### Task 6: Vocabulary Clusters — Food, Directions, Descriptions

**Files:**
- Create: `curriculum/vocabulary/tier1-survival/food-restaurant.md`
- Create: `curriculum/vocabulary/tier1-survival/directions-transportation.md`
- Create: `curriculum/vocabulary/tier1-survival/basic-descriptions.md`

- [ ] **Step 1: Create food-restaurant cluster**

**Key content requirements:**
- Cluster Meta: Phase A, core ~30, exposure ~20, grammar reinforcement [A-01, A-06]
- Core subtopics: Restaurant basics (mesa, menú, mesero/camarero, cuenta, propina), Ordering (quiero/quisiera, me gustaría, para mí, ¿me trae...?), Common foods (pollo, carne, pescado, arroz, ensalada, sopa, pan, huevos), Drinks (agua, café, cerveza, vino, jugo/zumo, leche), Descriptions (caliente, frío, dulce, salado, picante, rico/delicioso)
- Example sentences for: ordering with gustar ("Me gusta el pollo"), ordering with querer, asking for the check ("La cuenta, por favor"), tipping customs
- Dialect variations: mesero (Latin America) vs camarero (Spain), jugo vs zumo
- Cultural notes: meal times (comida/almuerzo is the big meal, cena is lighter), tipping customs vary by country
- Gender surprises: el agua (feminine with el)

- [ ] **Step 2: Create directions-transportation cluster**

**Key content requirements:**
- Cluster Meta: Phase A, core ~25, exposure ~15, grammar reinforcement [A-04, A-05]
- Core subtopics: Directions (derecha, izquierda, recto/derecho, arriba, abajo, cerca, lejos), Locations (esquina, cuadra/manzana, calle, avenida, semáforo, puente), Transportation (carro/coche, autobús/camión, metro, taxi, avión, tren, bicicleta), Useful phrases (¿Dónde está...?, ¿Cómo llego a...?, Está a dos cuadras, Queda cerca/lejos)
- Dialect variations: carro vs coche vs auto, camión vs autobús vs colectivo
- Cultural notes: address systems vary by country, cuadra usage

- [ ] **Step 3: Create basic-descriptions cluster**

**Key content requirements:**
- Cluster Meta: Phase A, core ~30, exposure ~15, grammar reinforcement [A-02, A-03]
- Core subtopics: Physical appearance (alto/bajo, grande/pequeño, gordo/delgado, joven/viejo, guapo/feo, rubio/moreno), Personality (simpático/antipático, inteligente, divertido/aburrido, amable, tranquilo, serio), States/feelings (contento/triste, cansado, enfermo, ocupado, preocupado), Colors (rojo, azul, verde, amarillo, blanco, negro, gris, marrón/café)
- Example sentences showing ser vs estar contrast: "Es alto" (permanent) vs "Está cansado" (temporary)
- Gender agreement examples throughout: "La chica alta, el chico alto, las chicas altas"
- Common errors: adjective placement, aburrido ser vs estar ("Es aburrido" = boring person vs "Está aburrido" = bored)

- [ ] **Step 4: Verify and commit**

```
git add curriculum/vocabulary/tier1-survival/food-restaurant.md curriculum/vocabulary/tier1-survival/directions-transportation.md curriculum/vocabulary/tier1-survival/basic-descriptions.md
git commit -m "feat: add tier-1 vocabulary clusters — food, directions, descriptions"
```

---

### Task 7: Core Activity Templates

**Files:**
- Create: `curriculum/activities/conversation-prompts.md`
- Create: `curriculum/activities/translation-exercises.md`
- Create: `curriculum/activities/role-play-scenarios.md`
- Create: `curriculum/activities/grammar-in-context.md`

Follow the activity template format from spec Section 7.3.

- [ ] **Step 1: Create conversation-prompts.md**

Used in every session for guided and free conversation practice.

**Key content:**
- Purpose: Develop spontaneous production, build fluency, assess unscaffolded performance
- Phase suitability: All phases (A=heavily scaffolded, D=fully open)
- How to Run (Basic): Tutor provides a topic and 3-4 starter questions. Learner responds. Tutor asks follow-up questions to extend. Errors noted silently, reviewed after.
- How to Run (Advanced): Learner chooses topic. Tutor participates as conversation partner, not interviewer. Errors only corrected if they impede meaning.
- What to assess: performance_unscaffolded for active grammar concepts, fluency metrics, vocabulary gaps
- Variations: Low energy = simpler topic with yes/no scaffolding. High energy = debate format. Time-limited = 5-minute rapid-fire Q&A.
- Example implementation: Full sample dialogue for a Phase A "daily routine" conversation showing tutor questions, learner responses, error handling.

- [ ] **Step 2: Create translation-exercises.md**

Used for controlled practice (Stage 2 in teaching sequence).

**Key content:**
- Purpose: Build accuracy through controlled production, assess performance_scaffolded
- Two modes: English→Spanish (production) and Spanish→English (comprehension)
- How to Run (Basic): Tutor gives 8-10 English sentences targeting the current concept. Learner translates. Immediate feedback per sentence.
- How to Run (Advanced): Full paragraph translation. No sentence-by-sentence feedback — review holistically.
- What to assess: accuracy on target concept, time to respond (fluency indicator), self-corrections
- Variations: Speed round (30 seconds per sentence), written vs spoken, reverse translation
- Example: 10 sample sentences targeting A-01 present regular with expected translations.

- [ ] **Step 3: Create role-play-scenarios.md**

Used for communicative practice (Stage 4).

**Key content:**
- Purpose: Apply grammar/vocabulary in realistic situations where focus is on MEANING, not form
- How to Run: Tutor sets a scenario, assigns roles, provides a goal. Learner must accomplish the goal using Spanish. Tutor plays the other role.
- Phase A scenarios: Ordering at a restaurant, asking for directions, introducing yourself at a party, buying something at a store, checking into a hotel
- Phase C-D scenarios: Job interview, disagreeing politely about a topic, explaining a problem to a doctor, negotiating a price
- What to assess: communication success (did they accomplish the goal?), grammar accuracy as secondary, vocabulary range, repair strategy use
- Example: Full role-play of "ordering at a restaurant" with sample dialogue, tutor prompts, and assessment notes.

- [ ] **Step 4: Create grammar-in-context.md**

Used for integration testing (combining multiple concepts).

**Key content:**
- Purpose: Test whether concepts that are individually solid remain accurate when combined with other active concepts. Assess integration_tested field.
- How to Run: Design an activity that REQUIRES using 2-3 grammar concepts simultaneously. No scaffolding for individual concepts — learner must manage all at once.
- Examples:
  - A-01 + A-03: "Describe your house — use adjectives with correct gender agreement and present tense verbs"
  - A-02 + A-03 + A-04: "Describe three people you know — use ser/estar correctly with adjective agreement and prepositions"
  - B-01 + B-03 + B-04: "Tell me about a childhood memory — you'll need both preterite and imperfect"
- What to assess: Does accuracy drop when concepts are combined? If yes, mark integration_tested=false and continue targeted practice.
- Variations: Written version (gives learner time to think), oral version (reveals automaticity), timed version (stress test).

- [ ] **Step 5: Verify and commit**

```
git add curriculum/activities/conversation-prompts.md curriculum/activities/translation-exercises.md curriculum/activities/role-play-scenarios.md curriculum/activities/grammar-in-context.md
git commit -m "feat: add core activity templates — conversation, translation, role-play, grammar-in-context"
```

---

### Task 8: Pronunciation Guides

**Files:**
- Create: `curriculum/pronunciation/vowel-sounds.md`
- Create: `curriculum/pronunciation/stress-rules.md`

Follow pronunciation guide template from spec Section 7.5.

- [ ] **Step 1: Create vowel-sounds.md**

**Key content requirements:**
- Phase: A (from day 1)
- The Sound: Spanish has 5 pure vowels. Unlike English, they are short, consistent, and never "glided."
  - a = "ah" (father, never "ay")
  - e = "eh" (pet, never "ee")
  - i = "ee" (feet, never "eye")
  - o = "oh" (go, but shorter/purer)
  - u = "oo" (food, never "you")
- Common English errors: diphthongizing vowels (saying "oh-oo" for o, "eh-ee" for e), reducing unstressed vowels to schwa (English reduces vowels in unstressed syllables, Spanish doesn't)
- Minimal pairs: peso/paso, mesa/misa, pero/puro, todo/tudo (Portuguese — shows consistent vowel importance)
- Practice assignments: Record 10 words with each vowel on Speechling, listen to Forvo for target vowels
- Signs of acquisition: Speechling coach reports clean vowel production in 3+ consecutive sessions

- [ ] **Step 2: Create stress-rules.md**

**Key content requirements:**
- Phase: A (from day 1)
- The Rules:
  - Words ending in vowel, n, or s → stress on second-to-last syllable (HABlo, coMEN, LIbros)
  - Words ending in consonant (not n or s) → stress on last syllable (haBLAR, ciuDAD, coMER)
  - Accent marks override both rules (teléFOno, café, inglés)
  - Accent marks on question words (qué, cómo, dónde — always)
  - Accent marks distinguish meaning (si/sí, el/él, tu/tú, como/cómo)
- Common English errors: stressing wrong syllable (applying English stress patterns), ignoring accent marks, not pronouncing accent marks differently
- Minimal pairs: papa/papá, como/cómo, si/sí, el/él, tu/tú
- Practice: Speechling recordings focusing on words with and without accent marks
- Signs of acquisition: Consistently stresses correct syllable in multi-syllable words

- [ ] **Step 3: Verify and commit**

```
git add curriculum/pronunciation/vowel-sounds.md curriculum/pronunciation/stress-rules.md
git commit -m "feat: add Phase A pronunciation guides — vowel sounds and stress rules"
```

---

### Task 9: Onboarding Sessions 1-5

**Files:**
- Create: `curriculum/onboarding/session-01-discovery.md`
- Create: `curriculum/onboarding/session-02-present-tense.md`
- Create: `curriculum/onboarding/session-03-gender-agreement.md`
- Create: `curriculum/onboarding/session-04-articles-prepositions.md`
- Create: `curriculum/onboarding/session-05-ser-vs-estar.md`

Follow the onboarding session template from spec Section 7.4. Each session references the grammar concept file and vocabulary cluster for its content.

- [ ] **Step 1: Create session-01-discovery.md**

**Key content:**
- Concept: A-00 Communication Repair (introduced as memorized phrases, not grammar)
- Prerequisites: None (first session)
- Session Plan:
  - Review: N/A (first session)
  - New Material: Discovery protocol (goals, experience, schedule, dialect) per first-session.md tutor guide. Then: introduce 6 core repair phrases. Practice each through repetition and role-play. "I'm going to speak some Spanish. When you don't understand, use one of these phrases."
  - Practice: Role-play stuck scenarios — tutor says something in Spanish, learner uses repair phrases
  - Checkout: Set up Anki. First 10 cards = repair phrases + basic greetings from tier1-greetings. Assign: memorize repair phrases, create Anki cards.
- Vocabulary: Begin tier1-greetings-introductions (hola, buenos días, adiós, gracias, por favor)
- Tool setup: Anki
- Observation targets: Prior Spanish knowledge, energy level, correction preference, tech comfort with Anki

- [ ] **Step 2: Create session-02-present-tense.md**

**Key content:**
- Concept: A-01 Present Tense Regular
- Prerequisites: A-00 repair phrases should be memorized
- Session Plan:
  - Review (5 min): Drill repair phrases. Verify Anki setup. "If I said something you didn't understand right now, what would you say?"
  - New Material (20 min): Load grammar/A-foundation/01-present-regular.md. Follow teaching sequence: Stage 1 (noticing with -ar verbs), then explicit explanation, then Stage 2 (conjugation drill). Preempt subject pronoun overuse.
  - Practice (10 min): "Tell me about your typical day" — guided conversation using present tense. Note which verbs they attempt, which they avoid.
  - Checkout: 8 new Anki cards (high-frequency -ar/-er/-ir verbs). Assign: Anki review, SpanishDict bookmark. Optional: Dreaming Spanish superbeginner 10 min.
- Vocabulary: Continue tier1-greetings (add daily routine verbs: trabajar, comer, vivir, estudiar, cocinar)
- Tool setup: SpanishDict
- Observation targets: Learning speed (how quickly do they pick up the pattern?), grammar preference (rules-first or examples-first?)

- [ ] **Step 3: Create session-03-gender-agreement.md**

**Key content:**
- Concept: A-03 Gender, Number, Agreement (including demonstratives and possessives)
- Prerequisites: A-01 at minimum "introduced" (can conjugate basic verbs)
- Session Plan:
  - Review: Homework check. Quick present tense warm-up (5 verbs, different subjects). Verify Dreaming Spanish engagement.
  - New Material: Load grammar/A-foundation/03-gender-agreement.md. Stage 1: show noun-adjective pairs, ask what pattern they see. Explain gender rules, then number, then adjective agreement, then demonstratives (este/ese), then possessives (mi/tu/su). Preempt adjective placement.
  - Practice: "Describe this room" / "Describe your family" — must use adjectives with correct agreement.
  - Checkout: 8 Anki cards (common nouns with genders, key adjectives). Assign: Anki, Dreaming Spanish superbeginner 10-15 min.
- Vocabulary: Begin tier1-basic-descriptions (colors, sizes, personality adjectives)
- Tool setup: Dreaming Spanish
- Observation targets: How quickly do they grasp gender? Do they self-correct on agreement?

- [ ] **Step 4: Create session-04-articles-prepositions.md**

**Key content:**
- Concept: A-04 Articles, Prepositions, Personal 'a'
- Prerequisites: A-03 (gender knowledge needed for articles)
- Session Plan:
  - Review: Gender agreement warm-up (tutor says noun, learner gives el/la). Homework verification.
  - New Material: Load grammar/A-foundation/04-articles-prepositions.md. Articles → contractions → common prepositions → personal 'a'. Stage 1: Show sentences with/without personal 'a', ask what's different.
  - Practice: Describe locations and directions using prepositions. "Where is your phone? Where do you work?"
  - Checkout: 8 Anki cards. Assign: Anki, Dreaming Spanish.
- Vocabulary: Continue tier1-basic-descriptions
- Observation targets: Preposition transfer errors from English, personal 'a' adoption

- [ ] **Step 5: Create session-05-ser-vs-estar.md**

**Key content:**
- Concept: A-02 Ser vs Estar
- Prerequisites: A-01 (present tense), A-03 (gender — for descriptions), A-04 (articles — for noun phrases)
- Note: This is the first HIGH-severity L1 interference concept. Load l1-interference-protocol.md.
- Session Plan:
  - Review: Quick warm-up covering sessions 2-4. Ask a question requiring articles + adjective agreement. Homework check.
  - New Material: Load grammar/A-foundation/02-ser-vs-estar.md AND tutor-guides/l1-interference-protocol.md. Explicitly preempt: "In English, 'to be' is one verb. In Spanish, there are TWO, and using the wrong one changes meaning." Stage 1: Sort sentences into ser/estar groups. Teach categorization. Drill with contrast pairs.
  - Practice: "Tell me about yourself AND how you're feeling right now" — forces mixing ser (identity) and estar (state).
  - Checkout: 8 Anki cards with ser/estar contrast pairs. Assign: Anki, Language Transfer episodes 1-3, obtain graded reader.
- Vocabulary: Begin tier1-numbers-time-dates
- Tool setup: Language Transfer, graded reader
- Observation targets: How severe is the ser/estar confusion? First data point for this high-risk L1 pattern.

- [ ] **Step 6: Verify and commit**

```bash
ls curriculum/onboarding/session-0[1-5]*.md | wc -l
```
Should be 5.

```
git add curriculum/onboarding/session-01-discovery.md curriculum/onboarding/session-02-present-tense.md curriculum/onboarding/session-03-gender-agreement.md curriculum/onboarding/session-04-articles-prepositions.md curriculum/onboarding/session-05-ser-vs-estar.md
git commit -m "feat: add onboarding sessions 1-5 (discovery through ser/estar)"
```

---

### Task 10: Onboarding Sessions 6-10

**Files:**
- Create: `curriculum/onboarding/session-06-consolidation-midpoint.md`
- Create: `curriculum/onboarding/session-07-questions-negation.md`
- Create: `curriculum/onboarding/session-08-gustar-type.md`
- Create: `curriculum/onboarding/session-09-irregular-present.md`
- Create: `curriculum/onboarding/session-10-consolidation-final.md`

- [ ] **Step 1: Create session-06 midpoint consolidation**

**Key content:**
- Concept: Consolidation — no new grammar
- Session Plan:
  - Review: All homework from sessions 2-5. Targeted verification questions for each concept.
  - Consolidation (20 min): Review A-01 (present tense), A-03 (gender), A-04 (articles), A-02 (ser/estar) through conversation. Use grammar-in-context activity to test combinations. Note which concepts are strong vs weak.
  - Practice: Open conversation using ALL learned concepts: "Tell me about your family, your home, what you do, and how you're feeling today."
  - Checkout: Reduced homework (consolidation, not expansion). Anki review only + one Dreaming Spanish video.
- Observation targets: Error rates on each concept, learning speed baseline, energy patterns over the week
- Adjustment notes: "If the learner has been consolidating due to pacing adjustments and is ready for new material, use this session to introduce A-05 instead."

- [ ] **Step 2: Create session-07 questions and negation**

**Key content:**
- Concept: A-05 Basic Questions and Negation
- Prerequisites: A-01, and concepts from sessions 2-5 should be at least "introduced"
- Session Plan:
  - Review: Quick review of sessions 2-5 (the consolidation assessment from session 6 informs what to focus on)
  - New Material: Load grammar/A-foundation/05-basic-questions.md. Question words, formation, negation, double negatives. Preempt double negative avoidance.
  - Practice: "Interview me" — learner asks 10 questions using different question words.
  - Checkout: 8 Anki cards (question words, negative words). Assign: Anki, Speechling setup and first recording.
- Vocabulary: Begin tier1-directions-transportation
- Tool setup: Speechling

- [ ] **Step 3: Create session-08 gustar-type verbs**

**Key content:**
- Concept: A-06 Gustar-type Verbs
- Prerequisites: A-01
- Note: HIGH-severity L1 interference. Load l1-interference-protocol.md.
- Session Plan:
  - Review: Questions warm-up (learner asks 5 questions). Speechling homework check.
  - New Material: Load grammar/A-foundation/06-gustar-type-verbs.md. Preempt immediately: "This structure is completely backwards from English. Your brain will resist it. That's normal." Stage 1: Show "Me gusta el café. Me gustan los libros." Ask why verb changes. Build understanding of reversed structure.
  - Practice: Likes/dislikes conversation. "Tell me 5 things you like and 3 things that bother you."
  - Checkout: 8 Anki cards with gustar constructions. Assign: Write 8 sentences about likes/dislikes.
- Vocabulary: Begin tier1-food-restaurant (natural pairing with gustar)

- [ ] **Step 4: Create session-09 irregular present**

**Key content:**
- Concept: A-07 Common Irregular Present
- Prerequisites: A-01
- Session Plan:
  - Review: Gustar check. "What do you like about learning Spanish?" (tests gustar in authentic context). Homework review.
  - New Material: Load grammar/A-foundation/07-present-irregular-common.md. Group verbs by pattern: stem-changing first (querer, poder, tener), then yo-irregular (hacer, saber, conocer), then fully irregular (ir, decir). Teach saber vs conocer distinction.
  - Practice: "What do you want to do this weekend? What can you do? Where do you go on Saturdays?"
  - Checkout: 8-10 Anki cards (irregular forms). Assign: Anki, Language Transfer 2 more episodes, Dreaming Spanish.
- Vocabulary: Continue tier1-food-restaurant

- [ ] **Step 5: Create session-10 final consolidation**

**Key content:**
- Concept: Final Consolidation + Transition
- Session Plan:
  - Review: All homework. Comprehensive concept check.
  - Consolidation (20 min): Extended conversation covering ALL Phase A concepts. Use grammar-in-context to test integration. Specifically test: present regular, ser/estar, gender agreement, questions, gustar, irregular verbs in combination.
  - Assessment: Note status of each concept (introduced, practicing, or approaching acquired). Populate skill-map context performance fields for first time. Record error rates.
  - Transition: Finalize learner-profile fields. Summarize what tutor has learned about learner's style, speed, and preferences. Preview what's ahead: "From now on, I'll tailor each session to what you need most."
  - Checkout: Full resource rotation homework. Set `onboarding_complete: true`.
- Observation targets: Comprehensive baseline for ALL concepts. Learner readiness for decision engine.
- Journal: If writing track hasn't started yet, assign first journal entry (3-5 sentences about anything).

- [ ] **Step 6: Verify and commit**

```bash
ls curriculum/onboarding/ | wc -l
```
Should be 10 (plus any .gitkeep).

```
git add curriculum/onboarding/
git commit -m "feat: add onboarding sessions 6-10 (midpoint consolidation through transition)"
```

---

## Post-Plan Verification

After all 10 tasks are complete, verify:

1. **File count:** 29 files created (8 grammar + 5 vocabulary + 10 onboarding + 4 activities + 2 pronunciation)
2. **Grammar files reference check:** Each grammar file's Prerequisites match the skill-map entries
3. **Onboarding sessions reference the right concept files:** Session 2→A-01, Session 3→A-03, etc.
4. **Vocabulary clusters have correct cluster_meta phase_alignment and grammar_reinforcement**
5. **No .gitkeep files remain in directories that now have content** (curriculum/onboarding/, curriculum/grammar/A-foundation/, curriculum/vocabulary/tier1-survival/, curriculum/activities/, curriculum/pronunciation/)
