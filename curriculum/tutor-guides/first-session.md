# First Session Guide

Loaded when: No session logs exist in `state/sessions/`.

## Goal

This session is NOT about teaching Spanish. It's about building the learner profile. Everything you learn here informs every future session.

**This session also delivers onboarding session 1.** `curriculum/onboarding/session-01-discovery.md` is the full session-1 plan and treats the discovery flow below as its sub-protocol. For **true-beginner and Early-A** learners, after the discovery/placement flow, also deliver that file's A-00 communication-repair portion (the 6 repair phrases, 5 basic greetings, vowel pronunciation check-in, and Anki setup) — A-00 is memorized chunks, not grammar, so it fits this profile-building session. **Late-A and Early-B+** placements skip onboarding session 1 per the Onboarding Skip Rules below (their counter starts past it). After this session, advance `current_onboarding_session` per §7 — without that, onboarding never progresses.

## Flow

### 1. Welcome & Program Orientation (5-7 min)
Welcome them warmly. Walk through how the program works — not just a quick intro, but enough that they understand what they're signing up for:

**The basics:**
- "I'm your personal Spanish tutor. We'll meet daily for 30-45 minutes — you just open a session here and we talk."
- "I remember everything across sessions — what you've learned, where you struggle, what homework you've done. Every session picks up where we left off."

**The daily rhythm:**
- "A typical day has three parts: homework before our session (15-30 min of flashcards and listening), the session itself, and a bit more practice after."
- "I'll assign specific homework each day — nothing generic. It's always targeted at what you need."

**The tools:**
- "We'll use a few external tools — flashcards, videos, maybe a pronunciation coach — but I'll introduce them gradually. Today we'll just set up one: Anki for flashcards."
- "You'll also get a visual study companion called Obsidian where you can browse your progress, see what's ahead, and track everything."

**The parking lot:**
- "Between sessions, if you hear a word you want to learn, have a question, or get stuck in a real-world situation — jot it in your parking lot file. I check it every session."

**What to expect:**
- "The first 10 sessions are structured — I'll introduce the core building blocks one at a time. After that, I adapt to you: what you need, what interests you, how fast you're moving."
- "There's a full student guide at `STUDENT-GUIDE.md` you can read anytime for the complete picture."

**Set expectations honestly:**
- "This is text-based, so I can't hear you speak. For pronunciation, we'll use a tool called Speechling that gives you human feedback — I'll set that up in a few sessions."
- "The system works best with daily practice. Even 10-minute micro-sessions on busy days are better than skipping."

### 2. Goals Discovery (5 min)
Ask about their goals:
- Why Spanish? Any specific milestones? (trip, job, relationship, curiosity?)
- Is there a target date for any of these?
- What does "success" look like for them?

### 3. Experience Assessment & Placement (~8 min for non-beginners)

Ask about their experience:
- Complete beginner, or some prior exposure?
- Any formal classes? Apps used? Time living in a Spanish-speaking country?

**If they say "complete beginner, never studied":** skip the entire assessment below. Proceed to section 4 (Schedule & Preferences). They enter normal onboarding from session 1. No placement needed.

**If they have any prior exposure:** run the full assessment below.

#### Self-Assessment Calibration

Before the grammar prompts, ask one question: "Before we try some Spanish — how would you rate your level? Beginner, intermediate, advanced?"

Record their answer. After assessment, compare self-report to actual performance to initialize the `calibration` fields in learner-profile.yaml:

| Self-report vs actual | calibration fields |
|---|---|
| Matches | self_report_accuracy: `reliable`, tendency: `accurate`, trust_weight: 0.7 |
| Self-report higher | self_report_accuracy: `unreliable`, tendency: `over-estimates`, trust_weight: 0.3 |
| Self-report lower | self_report_accuracy: `unreliable`, tendency: `under-estimates`, trust_weight: 0.5 |

Under-estimators get higher trust weight — "I'm worse than I think" is less dangerous for placement than "I'm better than I think."

#### Grammar Production — 3 Graded Prompts

These are conversational, not tests. Frame naturally:

1. "Can you introduce yourself in Spanish?"
2. "Tell me about your day yesterday."
3. "What would you do if you won the lottery?"

Score each with this 4-column rubric:

| Prompt | Can't attempt | Fragments / heavy errors | Gets point across with errors | Mostly correct, minor errors |
|--------|--------------|------------------------|-------------------------------|------------------------------|
| "Introduce yourself" | Pre-A | Early A | Late A | Acquired A-01 |
| "Tell me about yesterday" | Below B | Early B (knows some forms, can't sustain) | Mid B (past tense functional but messy) | Acquired B-01–B-04 |
| "What would you do if..." | Below C | Early C (recognizes structure, can't produce) | Mid C (attempts with errors) | Acquired through C |

The two middle columns distinguish "has seen this" from "can use this."

#### Embedded Vocabulary Observation (No Extra Time)

No standalone vocabulary prompt. During the grammar prompts, actively note:

- **Introduce yourself:** Do they name their job, city, hobbies? "Me llamo" (formulaic) vs constructed sentences with adjectives? How many domains — just name and origin, or family, work, interests?
- **Tell me about yesterday:** What verbs — just "fui" and "comí," or a range? Can they name times, places, activities? Do they circumlocute or just stop?
- **What would you do if:** Abstract vocabulary — wishes, reasons, opinions? Or only concrete nouns?

After the grammar prompts, one natural follow-up: take something they mentioned and ask them to expand. "You mentioned you like cooking — tell me more about that in Spanish. Use English for any words you don't know." The English fallback words reveal the vocabulary ceiling.

Log a vocabulary observation at one of four levels:

| Observation | Level |
|---|---|
| Only formulaic phrases (me llamo, buenos días) | Minimal |
| Functional within 1-2 familiar topics | Narrow |
| Can discuss varied topics, reaches for specific words | Broad |
| Uses nuanced vocabulary, near-synonyms, low-frequency words | Deep |

Also log: domains demonstrated, and production gap indicators (topics where they understood the concept but lacked the Spanish word).

#### Reading Comprehension Check (~2 min)

After the grammar prompts, transition: "Let me try something — I'm going to write you a short passage in Spanish. Don't worry about responding in Spanish, just tell me what it says."

Calibrate the passage one half-step above demonstrated production:
- **Placed at A:** 2-3 simple present tense sentences with some unfamiliar vocabulary
- **Placed at B:** Short paragraph mixing past tenses, some B-level structures they didn't produce
- **Placed at C+:** Passage with subjunctive, conditional, or compound tenses

Score:

| Comprehension | Signal |
|---|---|
| Gets the gist, misses details | Reception ≈ production (typical) |
| Understands nearly everything | Reception ahead of production — assign ambitious reading/listening homework |
| Understands less than expected | Possible over-placement — flag for heavier validation |

**This tests reading, not listening.** Listening baseline is deferred: assign a Dreaming Spanish video at estimated level, review comprehension in session 2.

**Listening baseline fallback:** If the learner does not complete the listening homework by session 3 (skipped homework, extended gap, or session 2 delayed), conduct an in-session listening exercise: play a 2-minute Dreaming Spanish clip at estimated level and assess comprehension directly. Do not leave listening_baseline_set as false beyond session 3.

### Placement Protocol

#### Placement Level Determination

Grammar production is the primary signal. Vocabulary and reading are secondary — they adjust confidence and vocabulary pre-population but do not override grammar-based phase placement.

| Grammar result | Secondary signals | Placement | Confidence |
|---|---|---|---|
| Can't attempt prompt 1 | (skipped) | True beginner — enter onboarding | N/A |
| Early A | Any | Early A — onboarding from session 2 | N/A (onboarding calibrates) |
| Late A | Any | Late A — onboarding from session 5 | N/A (onboarding calibrates) |
| Early B+ | Vocab Broad/Deep, reading at or above expected | Phase as assessed | High |
| Early B+ | Vocab Narrow, reading at expected | Phase as assessed | Medium |
| Early B+ | Vocab Minimal, or reading below expected | Phase as assessed | Low — front-load validation |

#### Grammar Concept Pre-Population

**Below placement level:** `acquired` with `performance_unscaffolded: null` (untested). Grammar is hierarchical — producing above a level implies mastery of that level, but unscaffolded performance has not actually been observed for these concepts. Setting the field to null signals "inferred, not verified." If the inference is wrong, the validation protocol catches it.

**Guardrail exception:** Placement-acquired concepts are exempt from the "practiced in 3+ separate sessions" acquisition requirement. The validation protocol serves as verification in lieu of observed practice sessions.

**At placement level:**
- Concepts directly demonstrated (even with errors) → `practicing`, error rates estimated from the sample
- Concepts at the same phase level but not directly demonstrated → `practicing`, error rates `null` (signals "needs assessment, not introduction")

**Above placement level:** `unseen`.

#### Vocabulary Cluster Pre-Population

Vocabulary is domain-specific — grammar-to-vocabulary inference is weak. Use the vocabulary observation:

| Vocab observation | Clusters below placement | Clusters at placement |
|---|---|---|
| Minimal | Demonstrated → `acquired`, undemonstrated → `practicing` | `unseen` |
| Narrow | Demonstrated → `acquired`, undemonstrated → `acquired` | Demonstrated → `practicing`, undemonstrated → `unseen` |
| Broad / Deep | `acquired` | `practicing` |

**Concurrent concept gate:** If Minimal observation at B+ placement creates more than 2-3 vocabulary clusters in "practicing," limit to the 2-3 clusters most likely weakest (topics the learner avoided) and leave the rest `acquired`.

#### Receptive Skills Initialization

| Reading check result | `receptive_skills.reading.current_level` |
|---|---|
| Below expected | One sub-level below grammar placement (e.g., Early B → Late A) |
| Gets the gist | Matches grammar placement |
| Understands nearly everything | One sub-level above grammar placement |

`receptive_skills.listening`: null until session 2 Dreaming Spanish review.

#### Onboarding Skip Rules

- **True beginner or Early A:** `onboarding_complete: false`. Normal onboarding from session 1 or 2.
- **Late A:** `onboarding_complete: false`. Onboarding from session 5. Set A-00, A-01 to `practicing`. Log skipped sessions (01-04) under `placement_skipped_sessions` in session log.
- **Early B or above:** `onboarding_complete: true`. Log all 10 onboarding sessions as skipped. Initialize `placement_validation` in schedule.yaml (see State Initialization below).
- **Always:** Note placement level and evidence in both the session log (`assessment` block) and `learner-profile.yaml` (`initial_placement` block).

### 4. Schedule & Preferences (3 min)
- Capture the learner's `study_time_budget` (all five sub-fields written into `state/schedule.yaml`). Ask conversationally — do NOT turn this into a form:
  - `daily_minimum` — "On your worst day, what's the smallest amount of time you'll do?" (strawman default: 15 min)
  - `daily_target` — "On a normal day, how much time do you plan to spend on Spanish outside our session?" (strawman default: 30 min)
  - `daily_maximum` — "What's the most you'd ever want in a day — the ceiling past which it feels like too much?" (strawman default: 60 min)
  - `weekly_goal` — "And over a week, what total feels right?" (strawman default: 180 min — builds in one rest day)
  - `today_stretch` — initialize to 0; this is an ephemeral "I have extra today" opt-in that the learner sets only on specific days
  - If the learner is unsure, offer the strawman defaults 15 / 30 / 60 / 180 / 0 as a starting point and let them adjust. Invariant: `daily_minimum <= daily_target <= daily_maximum` (the tutor confirms this holds before writing).
- Morning, afternoon, or evening preference?
- Which day works for a weekly review session?

### 5. Dialect Preference (2 min)
- Any preference for Mexican, Colombian, Castilian, or other?
- If they have a specific country/region in mind, note it.
- If no preference, recommend Mexican Spanish (most widely understood, abundant media).

**Dialect impact on grammar:** The learner's dialect choice affects which pronoun forms are actively taught:
- **Mexico/most of Latin America:** tú (informal) + usted (formal) + ustedes (plural). Vosotros is skipped entirely.
- **Spain (Castilian):** tú + usted + vosotros (informal plural) + ustedes (formal plural). Vosotros conjugation forms are added to all verb paradigms.
- **Argentina/Uruguay:** vos (informal) + usted (formal) + ustedes (plural). Vos conjugation forms replace tú forms in active practice from Phase A. Tú is taught for recognition.
- **Central America:** Mixed — some countries use vos, others tú. Ask the learner's specific target and adjust accordingly.

Record the choice in `learner-profile.yaml` under `target_dialect` — this drives conditional content in grammar files and dialect-notes.yaml throughout the program.

### 6. First Assignment (3 min)
End with something achievable that builds momentum. Calibrate to placement level:

**True beginner / Early A:**
- Walk them through setting up Anki if they don't have it.
- Give them their first 10 vocabulary cards to create (greetings and survival phrases).
- Assign one short Dreaming Spanish video at Superbeginner level.
- Mention SpanishDict as a reference tool.

**Late A:**
- Set up Anki. Give them 10 cards from the vocabulary cluster currently in focus (per pre-population).
- Assign a Dreaming Spanish video at Superbeginner level.
- Mention SpanishDict as a reference tool.

**Early B+:**
- Set up Anki. Give them 8 cards from the vocabulary cluster marked `practicing` in skill-map.
- Assign a Dreaming Spanish video at Beginner level (or Intermediate for Mid B+). This establishes the listening baseline reviewed in session 2.
- Suggest a graded reader at the reading level established by the reading comprehension check (A2 for Early B, B1 for Mid B+).
- Mention SpanishDict as a reference tool.

### 7. State Initialization

Also write the session log to `state/sessions/YYYY-MM-DD.yaml` with
`session_type: first-session`. **`docs/first-session-log-example.yaml` is the
copy-from template** — `check-session-log.py` requires (for first-session)
`session_number`, `duration_minutes`, `session_status`, `learner_energy`,
`session_activities`, `learner_observations.mood`/`.engagement`, an `assessment`
block, and `skill_map_updates`. Populate `study_time_budget` (below) BEFORE
running `post-session.sh`, or the homework-budget check FAILs the commit.

After the session, create and populate:
- `state/learner-profile.yaml` — all identity, goals, schedule fields, calibration, and initial_placement
- `state/skill-map.yaml` — mark concepts per placement rules above
- `state/schedule.yaml` — set initial phase, onboarding_complete
  - Populate `study_time_budget` map with the five sub-fields captured in §4 (daily_minimum, daily_target, daily_maximum, weekly_goal, today_stretch).
  - Populate `consecutive_too_much_count: 0` and `consecutive_just_right_count: 0` (fresh counters).
  - Set `current_onboarding_session` to the placement-determined start (session 1 has just been delivered): **true beginner / Early A → `2`**; **Late A → `5`** (onboarding sessions 2-4 skipped — log them under `placement_skipped_sessions`); **Early B+ → set `onboarding_complete: true`** and leave the counter unused (onboarding skipped entirely, placement validation runs instead). Each subsequent onboarding session advances this counter by 1 (per CLAUDE.md State Updates step 4) until session 10 sets `onboarding_complete: true`.
- `state/system-health.yaml` — initialize all counters
- `state/resource-tracker.yaml` — add Anki as first resource

**For Early B+ placements (onboarding skipped), also initialize placement validation:**
- Set `placement_validation.active: true` in schedule.yaml
- Set `placement_validation.confidence` to the confidence level from placement determination
- Build `placement_validation.queue` with concepts to validate, ordered by priority:
  1. Highest-level acquired concepts first (top-down: if B-04 is solid, B-01/B-02/B-03 are likely solid too)
  2. Prerequisites for current work
  3. Concepts at placement level with null error rates (undemonstrated)
  4. Remaining acquired concepts, low confidence first
- Queue entry format: `{concept_id, priority, status: pending, checked_in_session: null, notes: ""}`
- More concepts queued for low confidence; fewer for high confidence

Commit: `session YYYY-MM-DD: first session — learner profile established`

### 8. Vault Setup
After state initialization, set up the learner's Obsidian vault:
1. Run the generation script: `python3 scripts/generate-vault.py --full`
2. Tell the learner: "I've set up your study companion. Open Obsidian, point it at this project folder, and install the community plugins listed in vault/Getting Started.md. This is where you'll find your homework, track progress, and write your journal."
3. Commit vault/ alongside initial state files.
4. The first session's daily note will be generated as part of normal post-session vault updates.
