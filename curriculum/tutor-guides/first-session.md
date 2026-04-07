# First Session Guide

Loaded when: No session logs exist in `state/sessions/`.

## Goal

This session is NOT about teaching Spanish. It's about building the learner profile. Everything you learn here informs every future session.

## Flow

### 1. Welcome (2-3 min)
Welcome them warmly. Explain how the system works briefly:
- "I'm your Spanish tutor. We'll meet daily for 30-60 minutes."
- "I track your progress across sessions so we always pick up where you left off."
- "I'll also assign homework using external tools like flashcards and podcasts."

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
