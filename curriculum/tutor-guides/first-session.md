# First Session Guide

Loaded when: No session logs exist in `state/sessions/`.

## Goal

This session is NOT about teaching Spanish. It's about building the learner profile. Everything you learn here informs every future session.

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

### 3. Experience Assessment (5 min)
Ask about their experience:
- Complete beginner, or some prior exposure?
- Any formal classes? Apps used? Time living in a Spanish-speaking country?

If they have any prior Spanish, do a quick informal assessment. Don't frame these as tests — make it conversational:
- "Can you introduce yourself in Spanish?" (tests basic present tense)
- "Tell me about your day yesterday." (tests if they know past tense)
- "What would you do if you won the lottery?" (tests conditional/subjunctive)

Note what they can and can't do. This determines their starting phase.

### Placement Protocol (for learners with prior Spanish)

If the learner has any prior exposure, use the three graded prompts above as a structured diagnostic. Score each:

| Prompt | Tests | Can't attempt | Attempts with many errors | Mostly correct |
|--------|-------|---------------|---------------------------|----------------|
| "Introduce yourself" | Basic present tense | Below A | Practicing A-01 | Acquired A-01 |
| "Tell me about yesterday" | Past tenses | Below B | Practicing B-01/B-03 | Acquired B-01 through B-04 |
| "What would you do if..." | Conditional/subjunctive | Below C | Practicing C-01/C-04 | Acquired through C |

**Placement mapping:**

| Result | Starting Point | Action |
|--------|---------------|--------|
| Can't introduce self | True beginner | Follow normal onboarding from session 1 |
| Basic present tense only | Late A | Skip to onboarding session 5; mark A-00, A-01 as `practicing` |
| Present + some past tense | Early B | Set `onboarding_complete: true`, enter decision engine |
| Past tense + subjunctive attempts | Mid C | Set `onboarding_complete: true`, enter decision engine |

**Skill-map pre-population by placement level:**

- **Late A** — Set A-00 (communication-repair), A-01 (present-regular) to `practicing`. Set tier1-greetings-introductions to `practicing`. All other concepts remain `unseen`. Onboarding resumes at session 5 (ser-vs-estar).
- **Early B** — Set all A-xx grammar concepts to `acquired` (performance_unscaffolded: competent). Set tier1 vocabulary clusters to `acquired`. Set B-01 through B-04 to `practicing`. Set tier2 vocabulary clusters to `practicing` as demonstrated.
- **Mid C** — Set all A-xx and B-xx grammar concepts to `acquired`. Set tier1 and tier2 vocabulary to `acquired`. Set C-01 (present-subjunctive), C-02 (subjunctive-triggers), C-04 (conditional) to `practicing`. Set tier3 vocabulary clusters to `practicing` as demonstrated.

**Onboarding skip rules:**
- If placing at Late A: set `onboarding_complete: false`, log skipped sessions (01-04) in the session file under `placement_skipped_sessions`.
- If placing at Early B or above: set `onboarding_complete: true` in schedule.yaml. The decision engine handles all subsequent session planning. Log all 10 onboarding sessions as skipped.
- Always note placement level and evidence in the session log and learner-profile.yaml under `initial_placement`.

### 4. Schedule & Preferences (3 min)
- How much time per day can they realistically commit? (including homework)
- Morning, afternoon, or evening preference?
- Which day works for a weekly review session?

### 5. Dialect Preference (2 min)
- Any preference for Mexican, Colombian, Castilian, or other?
- If they have a specific country/region in mind, note it.
- If no preference, recommend Mexican Spanish (most widely understood, abundant media).

### 6. First Assignment (3 min)
End with something achievable that builds momentum:
- Walk them through setting up Anki if they don't have it.
- Give them their first 10 vocabulary cards to create (greetings and survival phrases).
- Assign one short Dreaming Spanish video at Superbeginner level.

### 7. State Initialization
After the session, create and populate:
- `state/learner-profile.yaml` — all identity, goals, and schedule fields
- `state/skill-map.yaml` — mark any demonstrated concepts as appropriate status
- `state/schedule.yaml` — set initial phase, `onboarding_complete: false`
- `state/system-health.yaml` — initialize all counters
- `state/resource-tracker.yaml` — add Anki as first resource
- Commit: `session YYYY-MM-DD: first session — learner profile established`

### 8. Vault Setup
After state initialization, set up the learner's Obsidian vault:
1. Run the generation script: `python3 scripts/generate-vault.py --full`
2. Tell the learner: "I've set up your study companion. Open Obsidian, point it at this project folder, and install the community plugins listed in vault/Getting Started.md. This is where you'll find your homework, track progress, and write your journal."
3. Commit vault/ alongside initial state files.
4. The first session's daily note will be generated as part of normal post-session vault updates.
