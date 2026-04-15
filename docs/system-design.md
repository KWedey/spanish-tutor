# Spanish Fluency Tutor — System Design

## Overview

A daily, AI-driven private tutoring system that guides a native English speaker to Spanish fluency. The learner launches a Claude Code session each day, and the agent acts as a personal tutor — assessing current state, conducting a live lesson, assigning homework using external tools, and updating a persistent learner model for the next session.

The system's core insight: **the tutor doesn't deliver all the content — it orchestrates the right resources at the right time and provides the one thing apps can't: adaptive, conversational practice with real-time feedback.**

---

## Design Principles

1. **State lives in files, not memory.** Every new session boots from structured state files. The agent is stateless; the repo is the brain.
2. **The tutor adapts to the learner, not the reverse.** Session length, difficulty, activity type, and pacing all flex based on the learner's actual performance and energy.
3. **Assessment is woven into practice.** The learner rarely takes "tests." The tutor evaluates naturally through conversation, translation, and comprehension exercises.
4. **External tools do what they do best.** Anki handles spaced repetition. Speechling handles pronunciation feedback. Italki provides human conversation. The tutor coordinates all of them.
5. **Transparency.** The learner can inspect any state file and see exactly what the system thinks about their progress. No black boxes.
6. **Consistency over intensity.** The system is designed for daily 30-60 minute sessions. It degrades gracefully to 10-minute micro-sessions rather than skipping entirely.
7. **Fluency and accuracy in balance.** Early phases lean toward building correct habits; later phases shift toward speed, spontaneity, and natural expression.
8. **Anticipate, don't just react.** The tutor preemptively addresses predictable English→Spanish transfer errors before they fossilize.
9. **Teach autonomy.** The system gradually hands control to the learner as they advance, with a defined graduation path.
10. **Minimize agent cognitive load.** The CLAUDE.md stays concise. Detailed protocols live in reference docs that are loaded conditionally based on session type. A fresh agent should process the minimum needed to run today's session correctly.
11. **Curriculum files are guardrails, not scripts.** Concept files provide structure, sequencing, and known pitfalls. The tutor uses its own knowledge of Spanish for explanations, examples, and conversation. Files prevent drift; the agent provides natural teaching.

---

## System Architecture

```
language/
├── CLAUDE.md                        # Core tutor instructions (concise, loaded every session)
├── SETUP.md                         # Prerequisites, dependency installation, script usage
├── requirements.txt                 # Python dependencies (PyYAML)
├── parking-lot.md                   # Learner-editable list of questions and gaps
├── docs/
│   ├── system-design.md             # This document
│   ├── resource-ecosystem.md        # External tools catalog
│   ├── session-log-example.yaml     # Annotated session log with all fields
│   └── progress-report-template.md  # Template for weekly progress reports
├── curriculum/
│   ├── tutor-guides/                # Conditional reference docs (loaded per session type)
│   │   ├── first-session.md         # Read only on session 1
│   │   ├── onboarding-guide.md      # Read during sessions 2-10
│   │   ├── weekly-review-guide.md   # Read on weekly review day
│   │   ├── decision-engine.md       # Read on standard sessions (concept selection + routing)
│   │   ├── emotional-intelligence.md # Read when motivation low or emotional signal
│   │   ├── l1-interference-protocol.md # Read when introducing new concepts
│   │   ├── fluency-activities.md    # Read in Phase B+ on fluency days
│   │   ├── sprint-mode.md           # Read when sprint is active
│   │   ├── real-world-debrief.md    # Read when learner reports real-world encounter
│   │   ├── placement-validation.md  # Read during placement validation (sessions 2-4, Early B+)
│   │   ├── phase-transition-guide.md # Read when phase prerequisites are met
│   │   ├── return-session.md        # Read when 3+ day gap since last session
│   │   ├── session-variety.md       # Read occasionally for alternative session formats
│   │   ├── maintenance-mode.md      # Read when autonomy_level is maintenance (post-Phase D)
│   │   └── error-recovery.md        # Read when state validation fails
│   ├── onboarding/                  # Fixed starter sequence (sessions 1-10)
│   │   ├── session-01-discovery.md
│   │   ├── session-02-present-tense.md
│   │   ├── session-03-gender-agreement.md
│   │   └── ...through session-10-consolidation-final.md
│   ├── grammar/                     # Grammar concept definitions
│   │   ├── A-foundation/
│   │   │   ├── 00-communication-repair.md  # FIRST concept: survival phrases for when you're stuck
│   │   │   ├── 01-present-regular.md
│   │   │   ├── 02-ser-vs-estar.md
│   │   │   ├── 03-gender-agreement.md
│   │   │   ├── 04-articles-prepositions.md
│   │   │   ├── 05-basic-questions.md
│   │   │   ├── 06-gustar-type-verbs.md
│   │   │   ├── 07-present-irregular-common.md
│   │   │   ├── 08-numbers-quantifiers.md
│   │   │   └── 09-accent-stress-rules.md
│   │   ├── B-conversational/
│   │   │   ├── 01-preterite-regular.md
│   │   │   ├── 02-preterite-irregular.md
│   │   │   ├── 03-imperfect.md
│   │   │   ├── 04-preterite-vs-imperfect.md
│   │   │   ├── 05-reflexive-verbs.md
│   │   │   ├── 06-direct-object-pronouns.md
│   │   │   ├── 07-indirect-object-pronouns.md
│   │   │   ├── 08-estar-gerund-progressive.md
│   │   │   ├── 09-imperatives.md
│   │   │   ├── 10-comparatives-superlatives.md
│   │   │   └── 11-future-ir-a.md
│   │   ├── C-intermediate/
│   │   │   ├── 01-present-subjunctive.md
│   │   │   ├── 02-subjunctive-triggers.md
│   │   │   ├── 03-formal-future.md
│   │   │   ├── 04-conditional.md
│   │   │   ├── 05-por-vs-para.md
│   │   │   ├── 06-compound-tenses.md
│   │   │   ├── 07-relative-clauses.md
│   │   │   ├── 08-indirect-speech.md
│   │   │   └── 09-diminutives-augmentatives.md
│   │   └── D-advanced/
│   │       ├── 01-past-subjunctive.md
│   │       ├── 02-si-clauses.md
│   │       ├── 03-subjunctive-all-tenses.md
│   │       ├── 04-passive-voice.md
│   │       ├── 05-register-shifting.md
│   │       └── 06-nuanced-connectors.md
│   ├── vocabulary/                  # Themed vocabulary clusters
│   │   ├── tier1-survival/
│   │   │   ├── greetings-introductions.md
│   │   │   ├── numbers-time-dates.md
│   │   │   ├── food-restaurant.md
│   │   │   ├── directions-transportation.md
│   │   │   └── basic-descriptions.md
│   │   ├── tier2-daily-life/
│   │   │   ├── home-household.md
│   │   │   ├── work-office.md
│   │   │   ├── family-relationships.md
│   │   │   ├── shopping-money.md
│   │   │   ├── weather-seasons.md
│   │   │   └── health-body.md
│   │   ├── tier3-social/
│   │   │   ├── opinions-agreement.md
│   │   │   ├── emotions-feelings.md
│   │   │   ├── plans-future.md
│   │   │   ├── storytelling-narration.md
│   │   │   ├── hobbies-interests.md
│   │   │   └── travel-culture.md
│   │   └── tier4-abstract/
│   │       ├── politics-society.md
│   │       ├── philosophy-ideas.md
│   │       ├── hypotheticals-debate.md
│   │       ├── humor-idioms.md
│   │       └── professional-specialized.md
│   ├── pronunciation/               # Pronunciation guide files by target sound
│   │   ├── vowel-sounds.md
│   │   ├── stress-rules.md
│   │   └── ...12 files total
│   ├── cultural/                    # Pragmatic competence guides
│   │   ├── politeness-formulas.md
│   │   ├── conversational-rhythm.md
│   │   ├── regional-awareness.md
│   │   ├── humor-and-idioms.md
│   │   └── register-shifting.md
│   ├── l1-interference.yaml         # Predicted English→Spanish transfer errors
│   ├── dialect-notes.yaml           # Vocabulary, grammar, pronunciation by dialect
│   ├── topic-bank.yaml              # Available weekly narrow topics with tags
│   ├── journal-prompts.yaml         # Writing prompts keyed to grammar/vocabulary
│   ├── media-bank.yaml              # External content recommendations by phase/topic
│   ├── listening-progression.yaml   # Listening level definitions and advancement criteria
│   ├── reading-progression.yaml     # Reading level definitions and advancement criteria
│   └── activities/                  # Activity type templates
│       ├── conversation-prompts.md
│       ├── translation-exercises.md
│       ├── listening-comprehension.md
│       ├── reading-exercises.md
│       ├── writing-exercises.md
│       ├── fluency-drills.md        # Timed monologues, speed translation, shadowing
│       ├── dictation.md
│       ├── storytelling.md
│       ├── role-play-scenarios.md
│       ├── error-correction.md
│       ├── pronunciation-practice.md
│       └── grammar-in-context.md
```

Activity templates in `curriculum/activities/` are **supplementary reference material**, not primary routing targets. The decision engine routes to grammar concept files (which contain stage-specific practice instructions). Activity templates provide additional exercise formats the tutor can draw from when a concept file's built-in activities need variety or when the session-variety guide calls for an alternative format (e.g., Game Day, Storytelling).

```
├── state/
│   ├── learner-profile.yaml         # Who the learner is, goals, preferences
│   ├── skill-map.yaml               # Per-concept mastery tracking
│   ├── schedule.yaml                # Current plan, active tracks, upcoming
│   ├── resource-tracker.yaml        # Which external resources are in rotation
│   ├── system-health.yaml           # Meta-metrics on system effectiveness
│   ├── sessions/                    # Daily session logs (kept 60 days)
│   │   └── YYYY-MM-DD.yaml
│   ├── summaries/                   # Weekly compressed summaries (kept 6 months)
│   │   └── YYYY-WNN.yaml
│   ├── milestones/                  # Phase transitions and achievements (permanent)
│   │   └── phase-X-completion.yaml
│   └── offline-guides/              # Exported study guides for offline days
│       └── YYYY-MM-DD.md
├── journal/                         # Learner's Spanish writing (permanent)
│   └── YYYY-MM-DD.md
├── progress-reports/                # Human-readable weekly progress summaries
│   └── YYYY-WNN.md
├── resources/
│   └── resource-catalog.yaml        # Structured catalog of all external tools
├── schemas/                         # YAML schema definitions for state files
│   ├── learner-profile.schema.yaml
│   ├── skill-map.schema.yaml
│   ├── schedule.schema.yaml
│   ├── session-log.schema.yaml
│   ├── resource-tracker.schema.yaml
│   └── system-health.schema.yaml
├── scripts/                         # Automation and maintenance
│   ├── setup.py                     # One-command setup for new users
│   ├── init-student.py              # Reset learner state to blank templates
│   ├── validate-state.py            # State file integrity checks
│   ├── generate-vault.py            # Generate/update Obsidian vault
│   ├── migrate-state.py             # Schema version migrations
│   ├── snapshot-state.py            # Backup/restore state snapshots
│   └── shared.py                    # Shared utilities for scripts
├── tests/                           # Test suite for scripts
│   ├── conftest.py
│   ├── test_init_student.py
│   ├── test_validate_state.py
│   ├── test_generate_vault.py
│   ├── test_migrate_state.py
│   ├── test_snapshot_state.py
│   └── test_shared.py
├── transcripts/                     # Full session conversation logs
├── STUDENT-GUIDE.md                 # Learner-facing program overview
└── vault/                           # Obsidian knowledge base (auto-generated)
    ├── Home.md, Roadmap.md, Getting Started.md
    ├── Daily/                       # Session notes
    ├── Grammar/                     # Concept notes by phase
    ├── Vocabulary/                  # Cluster notes by tier
    ├── Pronunciation/               # Sound guides
    ├── Progress/                    # Dashboards and reports
    └── Templates/                   # Note templates
```

---

## Component Design

### 1. CLAUDE.md — Tutor Operating Instructions

The CLAUDE.md is kept concise (~200 lines) to minimize agent cognitive load. It contains only what every session needs:

- **Session startup protocol** — what to read and in what order before responding
- **State validation checks** — detect and recover from corrupted or inconsistent state
- **Tutor persona and core methodology** — the essential teaching philosophy
- **Session routing logic** — which session type to run and which reference doc to load
- **Standard session flow** — the default session structure (abbreviated)
- **State update protocol** — what to write at session end
- **Guardrails** — the non-negotiable rules

Detailed protocols live in `curriculum/tutor-guides/` and are loaded conditionally:

| Reference Doc | Loaded When |
|--------------|-------------|
| `first-session.md` | No session logs exist |
| `onboarding-guide.md` | `onboarding_complete` is false (sessions 2-10) |
| `weekly-review-guide.md` | Today is the designated weekly review day |
| `emotional-intelligence.md` | Motivation is low/at-risk or emotional signal detected |
| `l1-interference-protocol.md` | Introducing a new grammar concept |
| `fluency-activities.md` | Phase B+ and today includes a fluency activity |
| `sprint-mode.md` | `sprint.active` is true in schedule.yaml |
| `real-world-debrief.md` | Learner mentions a real-world Spanish encounter |
| `placement-validation.md` | `placement_validation.active` is true (sessions 2-4, Early B+ placement) |
| `error-recovery.md` | State validation fails during startup |
| `input-orchestration.md` | Standard sessions (post-onboarding) — comprehensible input selection and debrief |
| `session-variety.md` | Occasionally on standard sessions — alternative formats (Game Day, Storytelling, etc.) |
| `phase-transition-guide.md` | All prerequisites for next phase show "acquired" for 2+ consecutive sessions |

This split means a standard session loads CLAUDE.md (~200 lines) + relevant state files. Only on special session types does the agent load additional protocol docs.

**Note on large state files:** As the learner progresses, `skill-map.yaml` grows significantly. The tutor should read the full file during startup but can selectively focus on active-phase concepts and concepts in "practicing" or "regressed" status for decision-making. Concepts in "automatic" status only need attention during spot-check scheduling.

See the CLAUDE.md draft (separate document) for full specification.

### 2. Learner Profile (`state/learner-profile.yaml`)

Slow-changing facts about the learner. Updated rarely — maybe once a month or when something significant changes.

```yaml
# Learner identity
name: ""
native_language: English
target_dialect: ""  # e.g., Mexican, Colombian, Castilian — chosen in first session
started: ""         # date of first session

# Goals
primary_goal: ""    # e.g., "conversational fluency for travel and social situations"
target_level: ""    # e.g., B2, C1
milestone_goals:    # concrete motivations
  - description: ""
    target_date: ""
graduation_criteria: ""  # what "done" looks like for this learner

# Schedule and capacity
typical_weekday_minutes: 0    # total learning time including homework
typical_weekend_minutes: 0
preferred_session_time: ""    # morning, afternoon, evening
max_new_concepts_per_week: 0  # adjusted over time based on absorption rate
weekly_review_day: ""         # e.g., Sunday

# Learning style (discovered over time, updated by tutor)
grammar_preference: ""        # rules-first, examples-first, or mixed
error_correction_preference: "" # inline, batched-at-end, or gentle-inline
vocabulary_retention_method: "" # visual, contextual, auditory, kinesthetic
motivation_style: ""          # challenge-driven, encouragement-driven, data-driven
energy_pattern: ""            # e.g., "high energy Mon-Wed, lower Thu-Fri"

# Calibration — how much to trust self-reports
calibration:
  self_report_accuracy: null   # correlation between self-reports and observed performance
  tendency: ""                 # overestimates, accurate, underestimates
  trust_weight: 0.5           # 0.0-1.0, how much to weight self-reports in decisions

# Motivation tracking
motivation:
  current_level: ""            # high, medium, low, at-risk
  streak_days: 0               # consecutive days with a session
  longest_streak: 0
  total_sessions: 0
  days_since_last_milestone: 0 # how long since something felt like "progress"
  plateau_risk: false          # true if no advancement in 3+ weeks
  high_motivation_triggers: [] # what energizes this learner (discovered over time)
  low_motivation_triggers: []  # what deflates them
  preferred_recovery: ""       # what helps when motivation dips

# External tools in use
tools:
  srs: ""                    # e.g., Anki
  pronunciation: ""          # e.g., Speechling
  conversation_partner: ""   # e.g., italki tutor named Carlos, meets Thursdays
  listening_primary: ""      # e.g., Dreaming Spanish
  reading_current: ""        # e.g., "Short Stories in Spanish (Olly Richards) - ch 5"

# Comprehensible input tracking
input_hours:
  listening_total: 0.0         # cumulative hours of Spanish listening
  reading_total: 0.0           # cumulative hours of Spanish reading
  last_updated: null           # date of last update

# Notes
notes: ""                    # anything else relevant

# Initial placement (populated in first session for non-beginners)
initial_placement:
  level: ""                 # pre-A / early-A / late-A / early-B / mid-B / early-C / mid-C
  date: null
  self_report: ""           # beginner / intermediate / advanced (learner's self-assessment)
  grammar_result: ""        # placement level derived from grammar prompts
  vocabulary_observation: "" # minimal / narrow / broad / deep
  reading_result: ""        # below-expected / at-expected / above-expected
  confidence: ""            # high / medium / low
  evidence_summary: ""      # tutor's rationale for placement decision
```

### 3. Skill Map (`state/skill-map.yaml`)

The core tracking document. Every grammar concept, vocabulary cluster, and skill dimension has a state entry.

```yaml
# Status values:
#   unseen     — not yet introduced
#   introduced — seen once, not yet practiced
#                (transitions to 'practicing' when the tutor conducts structured practice:
#                 drills, exercises, or scaffolded production — not incidental exposure)
#   practicing — actively working on it, error rate > 15%
#   acquired   — consistent in drills AND free production, error rate < 10%
#   automatic  — used without thinking, only spot-checked periodically
#   regressed  — was acquired/automatic, but errors resurfaced
#
# Context performance values (per grammar concept):
#   null       — untested in this context
#   struggling — errors frequent, needs more practice
#   competent  — consistent correct usage
#
# Acquisition requirement: status cannot be 'acquired' unless
# performance_unscaffolded is 'competent'.

grammar:
  A-01-present-regular:          # keys use phase prefix: A-01, B-04, etc.
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0           # total times actively practiced
    error_rate_drills: null     # rolling avg over last 5 drill instances
    error_rate_production: null # rolling avg over last 5 free production instances
    error_trend: null           # improving, stable, declining (based on production rate)
    performance_scaffolded: null    # null (untested), struggling, competent
    performance_unscaffolded: null  # null (untested), struggling, competent
    integration_tested_with: []    # List of concept IDs tested in combination (e.g., [A-01-present-regular, A-03-gender-agreement])
                                    # Resets to [] if the concept regresses. Otherwise persists until 'automatic'.
                                    # A concept is not fully consolidated until it has been combined with at least one other active concept.
    prerequisites: []
    notes: ""
    learner_interest:             # D-01/D-03: tutor-inferred interest (stale after 28 days)
      score: 0                    # 0-3. Out-of-range = validator FAIL.
      last_inferred: null         # YYYY-MM-DD. > 28 days = stale, scored as 0.
      signal_source: null         # parking-lot / debrief / spontaneous-q / engagement / stale
    recast_uptake_stats:          # D-07: aggregate from session-log recasts[]. Grammar only.
      recasts_given: 0            # Total recasts issued for this concept
      landed: 0                   # Learner incorporated corrected form
      missed: 0                   # Learner did not incorporate
      partial: 0                  # Learner partially incorporated
      last_updated: null          # YYYY-MM-DD of last aggregation
    regression_session_count: 0   # D-09/ENGINE-05: consecutive sessions in regression. Grammar only.

  # ... (one entry per grammar concept in curriculum/grammar/)

**Error rate calculation rules:**
- Rates are rolling averages over the last 5 practice instances per context (drill or production)
- If `practice_count < 3`, rates remain `null` — use `performance_scaffolded` / `performance_unscaffolded` qualitative assessments instead
- `error_trend` is derived from `error_rate_production` trajectory over last 3 sessions
  **Calculation:** Compare the 3-session rolling average of `error_rate_production` for the most recent 3 sessions against the previous 3 sessions:
  - `improving`: current 3-session average is 5+ percentage points lower than previous 3-session average
  - `declining`: current 3-session average is 5+ percentage points higher than previous 3-session average
  - `stable`: difference is less than 5 percentage points in either direction
  - If fewer than 6 sessions of data exist, use the available sessions and note lower confidence in the session log.
- If `last_practiced` is more than 60 days ago, consider stored error rates **stale** — collect fresh data before using them for advancement decisions. Note staleness in the session log.

**Decision engine usage of error rates:**
| Drills | Production | Interpretation | Activity Route |
|--------|-----------|----------------|-------|
| High | High | Early learning | Stage 2 (controlled practice) |
| Low | High | Transfer gap | Stage 3-4 (communicative practice) |
| Low | Low | Near-acquired | Spot-check only |
| High | Low | Unusual — investigate | Review methodology |

**Spot-check definition:** A brief (< 2 minute), low-pressure assessment of a near-acquired or automatic concept, embedded within another activity (e.g., "By the way, how would you say X?"). Goal: detect regression without disrupting flow. If error rate > 20% during spot-check, escalate to Stage 3 practice in the next session.

**Updated advancement rule:** "Acquired" requires `error_rate_production < 0.10` AND `error_rate_drills < 0.10` AND `performance_unscaffolded = "competent"` AND demonstrated in 3+ separate sessions.

**Minimum observation count:** Error rates should not be used for advancement decisions until at least 8-10 observations have been collected per context (drill and production counted separately). Below this threshold, rely on qualitative `performance_scaffolded` / `performance_unscaffolded` assessments. Small sample sizes can produce misleadingly low error rates (e.g., 0/2 correct looks like 0% but is not meaningful).

**Error rate recency weighting:** Not all observations are equally trustworthy. Apply confidence weighting based on how recently the data was collected:
- **Full confidence (within 7 days):** Use error rates directly for advancement decisions.
- **Moderate confidence (8-30 days):** Error rates are informative but should be confirmed with a fresh observation before triggering status changes (advancement or regression).
- **Low confidence (31-60 days):** Consider rates stale. Collect fresh data before any advancement decision. Flag during weekly review.
- **Expired (60+ days):** Rates are unreliable. Treat the concept as needing a fresh assessment. (This aligns with the staleness rule for `last_practiced` above.)

**Learner interest tracking (D-01/D-03):** `learner_interest` is a per-concept field on grammar, vocabulary, and cultural_awareness entries. The tutor infers a 0-3 score post-session from four signals: parking-lot mentions, real-world debrief content, spontaneous learner questions, and engagement notes. Stale after 28 days (`last_inferred` > 28 days ago = scored as 0). `validate-state.py` FAILs on `score > 3`; WARNs on stale entries. Missing field = backward-compatible default 0 (no FAIL).

**Recast uptake statistics (D-07):** `recast_uptake_stats` is a per-concept field on grammar entries only. Aggregated from session-log `recasts[]` entries by `post-session.sh` Step 5b. Invariant: `landed + missed + partial <= recasts_given`. `validate-state.py` FAILs on invariant violation. Missing field = backward-compatible all-zeros (no FAIL).

**Regression session count (D-09/ENGINE-05):** `regression_session_count` is a per-concept integer on grammar entries only. Tracks consecutive sessions where a concept's status is `regressed` or `practicing` after previously being `acquired` or `automatic`. Incremented by `post-session.sh`; read by `decision-engine.md` Step 0c regression escalation ladder to determine escalation stage (normal/flagged/approach_changed/sprint/surfaced). Reset to 0 when the concept re-acquires `acquired` status. Missing field = backward-compatible default 0 (no FAIL).

vocabulary:
  tier1-greetings-introductions:
    status: unseen
    words_total: 0              # populated from curriculum file
    words_introduced: 0
    passive_known: 0            # can recognize in reading/listening
    active_known: 0             # can produce in speaking/writing
    weak_production: []         # recognize but can't produce — need output practice
    weak_recognition: []        # can't recognize at all — need input exposure
    last_practiced: null
    notes: ""
    error_tracking:
      error_rate_production: null  # rolling avg, last 5 in-session observations (null = unobserved)
      common_errors: []            # e.g., "gender: 'el mano' → 'la mano'"
      last_observed: null          # date of last in-session production observation

  # ... (one entry per vocabulary cluster in curriculum/vocabulary/)

**Vocabulary ID to file path mapping:**
| Key prefix | Directory |
|-----------|-----------|
| tier1-* | curriculum/vocabulary/tier1-survival/ |
| tier2-* | curriculum/vocabulary/tier2-daily-life/ |
| tier3-* | curriculum/vocabulary/tier3-social/ |
| tier4-* | curriculum/vocabulary/tier4-abstract/ |

pronunciation:
  vowel-sounds:
    status: unseen
    last_practiced: null
    external_feedback: ""       # latest from Speechling or conversation partner
    notes: ""
  rr-trill:
    status: unseen
    last_practiced: null
    external_feedback: ""
    notes: ""
  # ... (b-v, d-soft, g-soft, j, ñ, ll, linking, intonation, stress)

### Pronunciation Status Updates from External Feedback

The tutor cannot assess pronunciation directly (text-based). Status changes come from:

1. **Speechling feedback:** When the learner reports Speechling coach feedback, update the pronunciation entry's `external_feedback` field with a dated note (e.g., "2026-04-08: coach says rr trill improving, still inconsistent in fast speech"). Advance status based on coach assessment:
   - "needs work" → `practicing`
   - "good" or "consistent" → `acquired`
   - "excellent" / "native-like" → `automatic`

2. **italki/conversation partner feedback:** If the partner comments on pronunciation, log it as lower-confidence data (partners aren't trained assessors). Use as a supporting signal, not primary evidence.

3. **Learner self-report:** Record but weight per `calibration.trust_weight`. Self-reports of pronunciation difficulty are more reliable than self-reports of pronunciation success.

4. **Whisper transcription accuracy:** If the learner uses local Whisper for self-checking, consistent transcription accuracy for target sounds is supporting evidence for advancement.

If no external feedback has been received for a pronunciation target in 30+ days, flag it during weekly review and suggest a Speechling session.

# Writing skill progression
writing:
  sentence_construction:
    status: unseen
    last_practiced: null
    notes: ""
  paragraph_coherence:
    status: unseen
    last_practiced: null
    notes: ""
  formal_register:
    status: unseen
    last_practiced: null
    notes: ""
  creative_expression:
    status: unseen
    last_practiced: null
    notes: ""

receptive_skills:
  listening:
    current_level: L1             # L1 (simplified speech) / L2 (slow structured) / L3 (moderate semi-structured) / L4 (natural with text support) / L5 (native, varied accents)
    comprehension_quality: null   # gist / main_ideas / details / inference
    hours_at_level: 0             # hours of input at current level (self-reported, cross-referenced with debrief quality)
    hours_total: 0                # cumulative listening input hours
    level_up_evidence: []         # dated observations, e.g., [{date: "2026-05-01", note: "summarized podcast details accurately, 3rd consecutive session"}]
    level_history: []             # e.g., [{level: L1, entered: "2026-04-10", hours_spent: 6}]
  reading:
    current_level: R1             # R1 (cognates, short texts) / R2 (short paragraphs, graded L1) / R3 (graded L2-3, simple articles) / R4 (authentic articles, short stories) / R5 (literature, journalism)
    comprehension_quality: null   # gist / main_ideas / details / inference
    lookup_frequency: frequent    # frequent / occasional / rare / none
    hours_at_level: 0
    hours_total: 0
    level_up_evidence: []
    level_history: []

# Cultural and pragmatic competence
cultural_awareness:
  register_shifting:            # tú/usted/vos appropriateness
    status: unseen
    introduced_at_phase: D
    assessed_through: "conversation behavior, role-play scenarios"
    signs_of_acquisition: "Shifts registers appropriately without prompting in role-play"
    notes: ""
  politeness_formulas:          # softening requests, disagreeing politely
    status: unseen
    introduced_at_phase: B
    assessed_through: "request formulation in conversation, role-play"
    signs_of_acquisition: "Uses softeners naturally without prompting"
    notes: ""
  conversational_rhythm:        # interrupting norms, back-channeling, silence
    status: unseen
    introduced_at_phase: C
    assessed_through: "conversation flow, back-channel usage"
    signs_of_acquisition: "Uses fillers and back-channels naturally in conversation"
    notes: ""
  regional_awareness:           # knowing that Spanish varies and adapting
    status: unseen
    introduced_at_phase: B
    assessed_through: "recognition of dialect differences, vocabulary choices"
    signs_of_acquisition: "Identifies regional variants and adapts vocabulary to target dialect"
    notes: ""
  humor_and_idioms:             # understanding and using humor appropriately
    status: unseen
    introduced_at_phase: C
    assessed_through: "comprehension of humor, appropriate idiom usage"
    signs_of_acquisition: "Uses idioms in context and recognizes humor in authentic content"
    notes: ""

# Fluency metrics (separate from accuracy)
fluency_metrics:
  speaking_pace: ""             # slow-deliberate, moderate, natural-flow
  hesitation_frequency: ""      # frequent, occasional, rare
  self_correction_rate: ""      # high (good awareness), low (automatic or unaware)
  circumlocution: ""            # how often they talk around words they don't know
  willingness_to_risk: ""       # avoids unfamiliar structures vs tries and fails
  thinking_language: ""         # still translating from English, or starting to think in Spanish

# Quantitative fluency benchmarks are defined in curriculum/tutor-guides/fluency-activities.md
# (oral WPM targets, typed production benchmarks, self-correction rate interpretation)

overall_estimates:
  cefr_estimate: A0
  estimated_active_vocabulary: 0    # words the learner can produce
  estimated_passive_vocabulary: 0   # words the learner can recognize (always >= active)
  production_gap: 0                 # passive - active; large gap = needs more output practice
  strongest_skill: null             # listening, reading, speaking, writing
  weakest_skill: null
  last_formal_assessment: null      # date of last placement test or equivalent
```

**Writing assessment rubric:**

Writing dimensions use the same status values as grammar. The rubric below defines what each status means for each dimension:

| Dimension | unseen | introduced | practicing | acquired |
|-----------|--------|-----------|------------|----------|
| sentence_construction | No writing attempted | Produces simple SVO sentences, frequent word order errors | Varies sentence length, attempts compound sentences, occasional structural errors | Consistently correct word order, subordinate clauses, varied sentence patterns |
| paragraph_coherence | — | Writes isolated sentences | Groups related sentences, basic transitions (y, pero, también) | Clear topic sentences, logical flow, varied connectors |
| formal_register | — | Only knows one register | Recognizes formal/informal distinction, inconsistent application | Shifts register appropriately for context (email vs. journal vs. letter) |
| creative_expression | — | Translates literally from English | Attempts idioms and culturally appropriate phrasing | Uses figurative language, humor, cultural references naturally |

Writing is assessed through journal entries and written exercises. Status advances follow the same error-rate thresholds as grammar (< 10% structural errors for 'acquired'), but the tutor also considers qualitative progression through the rubric.

### 4. Schedule (`state/schedule.yaml`)

The tutor's current plan. Updated at the end of each session.

```yaml
current_phase: A-foundation    # matches curriculum directory
current_week: 1
onboarding_complete: false     # true after session 10 (decision engine activates)
last_session_date: null          # Date of most recent session (YYYY-MM-DD). Updated at end of every session. Used for gap detection in return-session routing — avoids relying on filename parsing of session logs.
autonomy_level: guided         # guided, collaborative, learner-led, maintenance

# Active tracks — what's being worked on right now
active_grammar:
  primary: ""                  # the main concept being learned
  secondary: ""                # a reinforcement concept from a prior level
  maintenance: []              # acquired concepts due for spot-check

active_vocabulary:
  primary: ""                  # current cluster being built
  review: []                   # clusters in SRS maintenance

active_pronunciation:
  focus: ""                    # current target sound or pattern

active_writing:
  current_level: ""            # sentence, paragraph, structured, extended
  journal_active: false        # whether daily journal entries are assigned

# Narrow input — weekly topic for content immersion
weekly_topic:
  topic: ""                    # e.g., "immigration in Latin America"
  vocabulary_cluster: ""       # which vocab cluster this reinforces
  grammar_reinforcement: ""    # which grammar concept gets extra context
  started: ""                  # date this topic block started

topic_history: []    # List of {topic_id, week, date_started} — tracks which weekly narrow topics have been used and when, for FRESHNESS scoring in the decision engine

# Fluency vs accuracy emphasis
fluency_accuracy_balance: accuracy-leaning  # accuracy-leaning, balanced, fluency-leaning

# Fluency day tracking (Phase B+)
# Phase B: 1x/week, Phase C: 2x/week, Phase D: every session
fluency_days_this_week: 0
last_fluency_day: null

# Fluency day determination algorithm (checked during startup):
#   expected_this_week: 0 if Phase A, 1 if Phase B, 2 if Phase C, every session if Phase D
#   is_fluency_day: fluency_days_this_week < expected_this_week
#                   AND last_fluency_day != today
#                   AND (Phase D, OR enough non-fluency days remain this week for grammar work)

# Upcoming queue — what's next when current items are acquired
grammar_queue: []
vocabulary_queue: []

# Carryover — concepts from prior phase still in active practice
# Each entry tracks escalation state for stalled-concept intervention.
# Populated during phase transitions for concepts not yet "acquired".
carryover_concepts: []
  # Entry structure when populated:
  # - concept_id: A-05           # skill-map key
  #   carryover_date: ""         # date concept entered carryover
  #   sessions_in_carryover: 0   # incremented each session the concept is practiced
  #   current_approach: ""       # rule_based / example_based / communicative / context_shift
  #   is_prerequisite: false     # true if this concept blocks introduction of current-phase concepts
  #   escalation_stage: normal   # normal / flagged / approach_changed / sprint / surfaced

# SRS tuning (moved from system-health — these are config knobs, not health metrics)
anki_new_cards_per_session: 8
anki_retirement_threshold_days: 60

# Sprint mode — temporary reprioritization for a deadline
sprint:
  active: false
  goal: ""                     # e.g., "travel to Mexico City"
  target_date: ""
  focus_areas: []              # what to prioritize during sprint

# Adaptation notes
adjustment_log:
  - date: ""
    change: ""
    reason: ""

# Placement validation (active during sessions 2-4 for learners who skip onboarding)
placement_validation:
  active: false
  confidence: null          # high / medium / low / validated
  sessions_completed: 0
  listening_baseline_set: false
  total_downgrades: 0
  queue:                    # populated during session 1 for Early B+ placements
    - concept_id: ""
      priority: 1           # lower = check first
      status: pending       # pending / checked-pass / checked-fail / pending_downgrade
      checked_in_session: null  # date when this concept was spot-checked
      notes: ""
```

### 4b. Resource Tracker (`state/resource-tracker.yaml`)

Tracks input resource engagement and comprehension trends. Entries created on first assignment — not pre-populated from media-bank.

```yaml
schema_version: 1

input_summary:
  total_listening_hours: 0
  total_reading_hours: 0
  current_listening_level: L1    # mirrors skill-map.receptive_skills.listening.current_level
  current_reading_level: R1      # mirrors skill-map.receptive_skills.reading.current_level

resources: []
  # Entry structure when populated:
  # - name: "Dreaming Spanish"
  #   type: listening              # listening / reading / mixed
  #   level_range: [L2, L4]       # levels this resource spans
  #   sessions_assigned: 0
  #   sessions_completed: 0
  #   hours_logged: 0
  #   comprehension_trend: null    # improving / stable / declining
  #   vocabulary_extracted: 0      # count of words surfaced in debriefs
  #   last_assigned: null
  #   last_completed: null
  #   learner_engagement: null     # enthusiastic / neutral / reluctant
  #   notes: ""
```

### 5. Session Logs (`state/sessions/YYYY-MM-DD.yaml`)

Written at the end of every session. The primary handoff mechanism between agents. Kept for 60 days, then compressed into weekly summaries.

```yaml
date: ""
session_number: 0
duration_minutes: 0
learner_energy: ""              # high, medium, low (self-reported or inferred)
                                        # Inference signals: explicit self-report ("I'm tired"), slow response pace,
                                        # increased error rate vs recent sessions, request for shorter session.
                                        # When uncertain, ask: "How's your energy today?"
session_type: ""                # standard, micro, weekly-review, phase-transition, return
session_status: complete        # complete, partial, aborted — partial if session was cut short
gap_days: 0                     # days since last session (0 if consecutive)

# Assignment review — how did yesterday's homework go?
assignment_review:
  - task: ""
    resource: ""
    completed: false
    learner_report: ""          # what they said about it
    tutor_assessment: ""        # what the tutor inferred
    verification_result: ""     # what the tutor observed when testing the claim
    skill_updates: []           # any changes to make to skill-map

# Input comprehension debrief — what the learner consumed since last session
input_reviewed: []
  # Entry structure when populated:
  # - resource: ""                          # resource name
  #   type: listening                       # listening / reading
  #   duration_minutes: 0
  #   passes: 1                             # multi-pass count (L2-L3: recommend 2-3)
  #   comprehension_assessment: null        # gist / main_ideas / details / inference
  #   vocabulary_extracted: []              # words/phrases learner reported
  #   production_gaps_observed: []          # words learner reached for but couldn't produce
  #   difficulty_self_report: null          # too_easy / just_right / too_hard
  #   level_at_time: ""                     # learner's level when assigned

# Live session content
session_activities:
  - type: ""                    # conversation, grammar-drill, translation, fluency-drill, writing-review, etc.
    target_concepts: []         # grammar/vocab being practiced
    duration_minutes: 0
    performance: ""             # strong, good, mixed, struggling
    errors_noted:
      - error: ""               # what they said
        correction: ""          # what it should have been
        category: ""            # grammar, vocabulary, pronunciation, gender, fluency, cultural
        concept: ""             # which skill-map entry this maps to
        error_type: ""          # developmental, l1-interference, fossilized, slip
    observations: ""            # free-text summary of what the tutor observed (detailed data is in errors_noted)
    highlights: ""              # things they did well
    l1_interference_noted: false  # were any L1 interference errors observed? (specifics captured in errors_noted[].error_type)
    fluency_observations: ""    # pace, hesitation, risk-taking notes
    notes: ""

# Assessment updates to apply to skill-map
skill_map_updates:
  - concept: ""
    field: ""                   # status, error_rate_drills, error_rate_production, error_trend, etc.
    old_value: ""
    new_value: ""
    evidence: ""                # why this change

# Interleaving — prior concepts woven into today's primary concept practice
interleaved_concepts: []
  # Entry structure when populated:
  # - concept_id: ""                        # skill-map key
  #   interleave_context: ""                # e.g., "embedded ser/estar in preterite drills"
  #   errors_observed: 0

# Recast uptake log — per-event record of recasts and learner response (D-05)
# Required when session contains Stage 3/4, fluency, or conversation practice.
# Empty list (recasts: []) is a positive assertion that no recasts occurred.
recasts: []
  # Entry structure when populated:
  # - concept_id: ""              # grammar concept key (skill-map)
  #   error_form: ""              # what the learner said
  #   corrected_form: ""          # the recast
  #   uptake: landed              # landed / missed / partial
  #   activity_stage: stage-3     # stage-1 / stage-2 / stage-3 / stage-4 / fluency

# Assignments for before next session
assignments:
  - type: ""                    # pronunciation, listening, reading, vocabulary, speaking, writing, fluency
    resource: ""                # which external tool
    task: ""                    # specific instructions
    target_skill: ""            # which skill-map entry this supports
    estimated_minutes: 0
    priority: ""                # required, recommended, bonus
    narrow_topic_aligned: false # true if this assignment is part of the weekly topic block
    retrieval_target: ""        # prior concept to revisit in this assignment (e.g., "include 2 ser/estar sentences")
    input_minutes: 0            # listening or reading minutes for input tracking
    notes: ""

# Journal entry review (if applicable)
journal_review:
  entry_date: ""
  errors_found:
    - error: ""
      correction: ""
      concept: ""
  quality_notes: ""             # coherence, complexity, improvement from prior entries

# Learner state observations
learner_observations:
  mood: ""                      # motivated, neutral, frustrated, tired, excited, anxious
  engagement: ""                # high, medium, low
  emotional_state: ""           # confident, uncertain, embarrassed, breakthrough-joy, struggling
  self_assessment: ""           # what they said about how they're feeling about progress
  calibration_note: ""          # if self-assessment diverges from actual performance
  autonomy_readiness: ""        # observations about whether learner is ready for more control

# Initial assessment (session 1 only, for non-beginners)
assessment:
  self_report: ""           # learner's self-assessed level before prompts
  grammar_prompts:
    introduce_yourself:
      response_summary: ""  # what the learner said, abbreviated
      scoring: ""           # pre-A / early-A / late-A / acquired-A-01
    tell_about_yesterday:
      response_summary: ""
      scoring: ""           # below-B / early-B / mid-B / acquired-B-01-B-04
    what_would_you_do:
      response_summary: ""
      scoring: ""           # below-C / early-C / mid-C / acquired-through-C
  vocabulary_observation:
    level: ""               # minimal / narrow / broad / deep
    domains_demonstrated: []
    production_gap_indicators: []
    follow_up_topic: ""
    follow_up_notes: ""
  reading_check:
    passage_level: ""       # calibrated one half-step above demonstrated production
    comprehension: ""       # below-expected / gets-the-gist / understands-nearly-all
  placement_decision:
    level: ""               # final placement level
    confidence: ""          # high / medium / low
    rationale: ""           # tutor's reasoning

# Placement validation spot-checks (sessions 2-4 only, when placement_validation.active)
validation_checks:
  - concept_id: ""
    elicitation: ""         # how the tutor naturally prompted this (e.g., conversation topic)
    observation: ""         # what the learner produced
    result: ""              # checked-pass / checked-fail
    action: ""              # validated / downgrade-to-practicing / downgrade-to-introduced
    error_rate_estimate: null

# Decision engine trace — records why the tutor chose this session's focus
decision_engine_trace:
  candidates_scored: 0
  top_candidates:
    # Per-candidate shape: {id, NEED, GAP, DECAY, TOPIC, INTEREST, VARIETY, TOTAL}
    # INTEREST (int, 0-3): D-04 learner_interest dimension. Recorded for every
    # top candidate always (not conditional). Full 6-dimension trace.
    - id: ""                    # concept ID
      NEED: 0
      GAP: 0
      DECAY: 0
      TOPIC: 0
      INTEREST: 0              # D-04: 0-3 learner_interest dimension
      VARIETY: 0
      TOTAL: 0
  selected_primary: ""
  selected_secondary: ""
  override_reason: null           # null unless manual override; record reason if so

session_difficulty_rating: null   # learner self-report at checkout: too-easy | just-right | too-hard | null

# Next session recommendation
next_session:
  recommended_focus: ""
  reason: ""
  avoid: ""                     # what NOT to do tomorrow and why
  session_type: ""              # normal, consolidation, light-review, push-forward, fun-day
  estimated_duration: 0
  l1_interference_to_preempt: [] # predicted transfer errors to address proactively
```

**Session difficulty rating:** `session_difficulty_rating` is captured during checkout ("How did today feel — too easy, about right, or too hard?"). It feeds into `system-health.yaml` counters (`sessions_rated_too_easy_30d`, `sessions_rated_too_hard_30d`) and influences next-session calibration: two consecutive `too-easy` ratings → increase challenge; two consecutive `too-hard` ratings → reduce load.

**Session recovery:** If `session_status` is `partial`, the next session's agent should:
1. Note that the previous session was incomplete
2. Check what was and wasn't covered by reading `session_activities`
3. Resume from where the previous session left off rather than starting fresh
4. Do not count a partial session toward advancement criteria (e.g., "practiced in 3 sessions")

### 6. Weekly Summaries (`state/summaries/YYYY-WNN.yaml`)

Generated during weekly review sessions. Compresses 5-7 daily logs into trends. Kept for 6 months.

```yaml
week: ""                        # e.g., 2026-W13
dates: ""                       # e.g., 2026-03-23 to 2026-03-29
sessions_completed: 0
total_session_minutes: 0
homework_completion_rate: 0.0

grammar_progress:
  - concept: ""
    start_status: ""
    end_status: ""
    error_trend: ""
    notes: ""

vocabulary_progress:
  - cluster: ""
    words_added: 0
    retention_issues: []

writing_progress: ""            # summary of journal quality and writing skill movement
fluency_progress: ""            # summary of fluency metric changes
pronunciation_progress: ""      # summary of pronunciation work and external feedback

notable_events: []              # achievements, regressions, breakthroughs, life events
energy_pattern: ""              # observed pattern for the week
motivation_level: ""            # overall motivation assessment
weekly_topic: ""                # what the narrow input topic was
narrow_input_effectiveness: ""  # did the topic cycling help with vocabulary retention?

system_health_snapshot:
  concepts_requiring_reteach: 0
  homework_difficulty_avg: 0.0
  session_frequency: 0.0        # sessions per 7 days
```

### 7. Milestones (`state/milestones/YYYY-MM-DD-milestone-id.yaml`)

Permanent records of achievements and major transitions. Useful for long-term progress review and motivation.

```yaml
type: ""                        # phase-transition | first-real-world | first-self-correction | vocabulary-milestone | streak-milestone | fluency-milestone | cultural-milestone | first-dream-in-spanish
date: ""
session_number: 0
title: ""                       # short human-readable label
description: ""                 # what happened, in plain language
evidence: ""                    # what the tutor observed that triggered this

# Populated only when type: phase-transition
phase_transition:
  from_phase: ""
  to_phase: ""
  started: ""
  completed: ""
  total_sessions: 0
  total_days: 0
  assessment:
    production_task: ""         # e.g., "Tell a story about a trip using past tenses"
    receptive_task: ""          # e.g., "Summarize this audio clip"
    performance_summary: ""
    gaps_identified: []
    decision: ""                # advance | extend | partial
  carryover_concepts: []        # concepts entering the new phase still in "practicing"
  learner_reflection: ""

# Snapshot of learner state at the time of this milestone
snapshot:
  cefr_estimate: ""
  active_vocabulary: 0
  grammar_acquired: 0
  total_sessions: 0
  days_since_start: 0
```

### 8. System Health (`state/system-health.yaml`)

Meta-metrics on whether the tutoring system itself is effective. Reviewed during weekly sessions.

```yaml
# Decision engine effectiveness
concepts_requiring_reteach_total: 0      # high = bad sequencing or premature advancement
average_sessions_to_acquire: 0           # trending up = something wrong
reteach_rate_30d: 0.0                    # % of concepts that regressed after being acquired

# Homework calibration
homework_completion_rate_30d: 0.0        # below 60% = overloaded or wrong type
homework_reported_difficulty_avg: 0.0    # should hover around 3/5
assignment_skip_patterns: []             # which types get skipped most?

# Pacing
days_in_current_phase: 0
concepts_acquired_per_month: 0           # trending down = plateau or pacing issue
concepts_in_practicing_simultaneously: 0 # should stay <= 2

# Engagement
average_session_duration_30d: 0
session_frequency_30d: 0.0              # sessions per week
learner_initiated_topics_30d: 0          # are they bringing their own questions?
sessions_rated_too_easy_30d: 0
sessions_rated_too_hard_30d: 0

# SRS health
# Note: anki_new_cards_per_session and anki_retirement_threshold_days moved to schedule.yaml
anki_estimated_deck_size: 0
anki_estimated_daily_review_minutes: 0

# Placement validation effectiveness (populated after validation period closes)
placement_validation_metrics:
  placement_level: null     # where the learner was placed
  initial_confidence: null  # high / medium / low
  total_concepts_validated: 0
  total_downgrades: 0
  final_assessment: null    # placement-confirmed / placement-adjusted
  validation_completed: null  # date validation period closed

# Goal tracking
goal_tracking:
  primary_goal_progress: ""       # qualitative: on-track | behind | ahead | at-risk
  estimated_weeks_remaining: null  # rough estimate based on current acquisition rate and remaining concepts
  concepts_remaining_for_next_phase: 0
  concepts_remaining_for_target_level: 0
  current_acquisition_rate: 0.0   # concepts acquired per week (30-day rolling average)
  last_goal_review: null          # date of last weekly review goal check
  milestone_progress: []          # list of {goal, status: pending|achieved|at-risk, target_date, notes}

# Last reviewed
last_system_review: null
```

### 9. L1 Interference Map (`curriculum/l1-interference.yaml`)

Predicted English→Spanish transfer errors, organized by when they typically appear.

```yaml
# Errors the tutor should preemptively address.
# When the "preempt_at" concept is being introduced, the tutor
# should explicitly address the English habit BEFORE it fossilizes.

interference_patterns:
  - id: ser-estar-confusion
    english_cause: "English has one verb 'to be'"
    common_errors:
      - wrong: "Soy cansado"
        right: "Estoy cansado"
        explanation: "Temporary states use estar"
      - wrong: "Está un profesor"
        right: "Es un profesor"
        explanation: "Identity/profession uses ser"
    preempt_at: A-02-ser-vs-estar
    severity: high
    persistence: "Can fossilize permanently if not caught early"

  - id: adjective-placement
    english_cause: "English puts adjectives before nouns"
    common_errors:
      - wrong: "una roja casa"
        right: "una casa roja"
    preempt_at: A-03-gender-agreement
    severity: medium
    persistence: "Usually self-corrects with enough input"

  - id: subject-pronoun-overuse
    english_cause: "English requires subject pronouns"
    common_errors:
      - wrong: "Yo voy al mercado y yo compro..."
        right: "Voy al mercado y compro..."
        explanation: "Spanish drops subject pronouns when clear from conjugation"
    preempt_at: A-01-present-regular
    severity: medium
    persistence: "Common for months, resolves with immersion"

  - id: false-cognates
    english_cause: "Words that look similar but mean different things"
    common_errors:
      - wrong: "Estoy embarazada" (meaning: I'm pregnant)
        intended: "I'm embarrassed"
        right: "Estoy avergonzada"
      - wrong: "Quiero introducir mi amigo" (meaning: I want to insert)
        intended: "I want to introduce"
        right: "Quiero presentar a mi amigo"
      - wrong: "Estoy constipado" (meaning: I have a cold)
        intended: "I'm constipated"
        right: "Estoy estreñido"
    preempt_at: vocabulary-introduction
    severity: high
    persistence: "Memorable once learned, but embarrassing if not"

  - id: preposition-mapping
    english_cause: "Prepositions don't map 1:1"
    common_errors:
      - wrong: "pensar sobre" (think about)
        right: "pensar en"
      - wrong: "soñar sobre" (dream about)
        right: "soñar con"
      - wrong: "depender de" used as "depende en"
        right: "depender de"
    preempt_at: A-04-articles-prepositions
    severity: medium
    persistence: "Long-lasting — requires memorization per verb"

  - id: hacer-for-weather
    english_cause: "English uses 'it is' for weather"
    common_errors:
      - wrong: "Es caliente afuera"
        right: "Hace calor afuera"
    preempt_at: tier2-weather-seasons
    severity: low
    persistence: "Corrects quickly once taught"

  - id: negative-double-negative
    english_cause: "English avoids double negatives"
    common_errors:
      - wrong: "No tengo algo" (applying English 'not...something')
        right: "No tengo nada" (Spanish requires double negative)
    preempt_at: A-05-basic-questions
    severity: medium
    persistence: "Moderate — feels wrong to English speakers"

  - id: gustar-construction
    english_cause: "English 'I like X' vs Spanish 'X pleases me'"
    common_errors:
      - wrong: "Yo gusto el café"
        right: "Me gusta el café"
    preempt_at: A-06-gustar-type-verbs
    severity: high
    persistence: "Fossilizes quickly if not addressed immediately"

  - id: preterite-imperfect-overuse
    english_cause: "English past tense doesn't distinguish aspect"
    common_errors:
      - wrong: "Cuando fui niño..." (when I was a child — should be imperfect)
        right: "Cuando era niño..."
    preempt_at: B-04-preterite-vs-imperfect
    severity: high
    persistence: "The hardest B1 concept — takes months to internalize"

  - id: subjunctive-avoidance
    english_cause: "English rarely uses subjunctive"
    common_errors:
      - wrong: "Quiero que tú vienes" (indicative instead of subjunctive)
        right: "Quiero que tú vengas"
    preempt_at: C-01-present-subjunctive
    severity: high
    persistence: "Very persistent — the biggest C1 hurdle"
```

---

## The Decision Engine

### Onboarding Period (Sessions 1-10)

During the first 10 sessions, the decision engine is **not active**. Instead, the tutor follows a fixed onboarding sequence defined in `curriculum/onboarding/`. The sequence is structured as 1 discovery session + 7 concept introductions + 2 consolidation sessions (midpoint at session 6, final at session 10).

**Concept sequence:**

| Session | Grammar Concept | Notes |
|---------|----------------|-------|
| 1 | A-00 communication repair phrases | Discovery session |
| 2 | A-01 present tense regular | |
| 3 | A-03 gender, agreement, demonstratives, possessives | |
| 4 | A-04 articles, prepositions, personal 'a' | |
| 5 | A-02 ser vs estar | Delayed to build implicit intuition from sessions 1-4 |
| 6 | **Midpoint consolidation** | Review sessions 2-5, collect baseline data |
| 7 | A-05 questions and negation | |
| 8 | A-06 gustar-type verbs | |
| 9 | A-07 common irregular present (including hay) | |
| 10 | **Final consolidation** | All-concept review, transition assessment, set `onboarding_complete` |

**Post-onboarding Phase A concepts:** A-08 (numbers/quantifiers) and A-09 (accent/stress rules) are not part of the onboarding sequence. They are introduced post-onboarding via the decision engine, typically in sessions 11-15. Numbers are encountered naturally during onboarding (telling time, counting) but formalized later. Accent rules are reinforced throughout all phases.

**Pacing escape valve:** If the learner is struggling, consolidate instead of introducing the next concept. Remaining concepts get introduced post-onboarding via the decision engine.

This period:

- Establishes the learner profile through observation
- Introduces core Phase A concepts in a dependency-aware order
- Collects baseline performance data (error rates, learning speed, energy patterns)
- Sets up external tools (Anki, Speechling, etc.) distributed across sessions
- Discovers the learner's preferences (grammar approach, correction style, etc.)

At session 11, the decision engine activates with ~10 data points per concept. The learner shouldn't notice the transition — sessions just gradually become more tailored.

### Daily Focus Selection (Session 11+)

At the start of each session, the tutor selects today's focus by scoring candidate activities:

```
For each candidate concept/activity:

  NEED (0-10)
    How important is this for the learner's current phase?
    Foundation grammar scores higher than niche vocabulary.

  GAP (0-10)
    How far is the learner from "acquired" on this?
    "practicing" with high error rate = high gap.
    "acquired" with no recent practice = moderate gap (decay risk).
    "unseen" with met prerequisites = opportunity.

    Considers context performance:
    - Regressed: highest urgency
    - Scaffolded struggling: high gap (fundamental issue)
    - Scaffolded competent, unscaffolded struggling: moderate gap (transfer gap)
    - Both competent, integration untested: low gap (needs testing)
    - Fully competent and integration tested: maintenance only

  DECAY (0-10)
    How long since last practiced?
    Uses a simplified forgetting curve:
      < 1 day: 0
      1-3 days: 2
      4-7 days: 5
      8-14 days: 7
      15+ days: 9
    Only applies to items with status >= introduced.

  READINESS (binary gate)
    Are all prerequisites met?
    If not, this concept is excluded from candidates entirely.

  VARIETY_PENALTY (0-5)
    Has the learner done this activity TYPE too many times recently?
    3 consecutive grammar-heavy days → penalize grammar, boost listening/speaking.

  TOPIC_BOOST (0-3)
    Does this concept align with the current weekly narrow topic?
    Strong alignment: +3. Partial alignment: +1. No alignment: 0.

  ENERGY (modifier)
    If learner reports low energy or the tutor infers fatigue:
      Boost passive activities (listening, reading).
      Reduce active production and new concept introduction.
    If high energy:
      Boost challenging activities and new material.

  MOTIVATION (modifier)
    If motivation.current_level is "low" or "at-risk":
      Boost fun activities, easy wins, and progress celebration.
      Reduce challenging new material.
    If motivation.plateau_risk is true:
      Boost novel activity types and immersion content.
      Consider a "stretch" challenge to break the plateau.

  FLUENCY_BALANCE (modifier)
    If fluency_accuracy_balance is "accuracy-leaning" (Phase A-B):
      Slightly boost grammar drills and error correction.
    If "balanced" (Phase C):
      Equal weight.
    If "fluency-leaning" (Phase D):
      Boost timed speaking, free conversation, spontaneous production.

  PARKING_LOT (modifier)
    If parking-lot.md contains an item directly related to this concept:
      +3 priority. Real learner need — address it.

  SPRINT_OVERRIDE (gate)
    If sprint.active is true in schedule.yaml:
      Only sprint-tagged concepts are eligible for selection.
      All other scoring is suspended for non-sprint items.

  MAINTENANCE_DECAY (modifier)
    If concept status is "automatic" and last_practiced > 30 days:
      Add +3 to DECAY to trigger a spot-check.
      Do not treat as a primary focus — embed in conversation or warm-up.

  PRIORITY = NEED + GAP + DECAY + TOPIC_BOOST - VARIETY_PENALTY
  (filtered by READINESS and SPRINT_OVERRIDE, modified by ENERGY, MOTIVATION, FLUENCY_BALANCE, PARKING_LOT, MAINTENANCE_DECAY)
```

### Weekly Topic Selection

Each week the tutor selects a narrow input topic to anchor all homework assignments. Score each candidate topic from `curriculum/topic-bank.yaml`:

```
For each candidate topic:

  GRAMMAR_FIT (0-5)
    How well does this topic create natural practice opportunities
    for the current primary grammar focus?
    e.g., "Childhood memories" + imperfect tense = 5.

  VOCABULARY_FIT (0-5)
    Does this topic overlap with the current active vocabulary cluster?
    High overlap = less dead weight, more reinforcement.

  LEARNER_INTEREST (0-3)
    Has the learner expressed interest in this topic?
    Check: learner-profile.yaml interests, parking-lot.md, recent session notes.
    Strong connection = 3, mild = 1, unknown/neutral = 0.

  FRESHNESS (0-3)
    How long since this topic was last used?
    Never used = 3. Used 4+ weeks ago = 2. Used 2-3 weeks ago = 1.
    Used last week = 0 (exclude).

  TOPIC_SCORE = GRAMMAR_FIT + VOCABULARY_FIT + LEARNER_INTEREST + FRESHNESS
```

Select the highest-scoring topic. Log the selection in `state/schedule.yaml` under `weekly_topic`. Record effectiveness in the weekly summary.

After selecting the focus concept, route to activity type:
- Scaffolded struggling → controlled practice (concept file Stage 2)
- Scaffolded competent, unscaffolded struggling → communicative practice (Stages 3-4)
- Integration untested → combined exercises (activities/grammar-in-context.md)
- All competent → spot-check only, move to next priority

The top 1-2 concepts become the session focus. The tutor doesn't mechanically expose this scoring — it presents the session naturally.

### Advancement Rules

**When to advance to a new concept:**
- Current primary concept is at "acquired" status (error rate < 10% in both drills and free production, `performance_unscaffolded` = "competent", and demonstrated in 3+ separate sessions)
- No regression in prerequisite concepts

**When to consolidate instead of advancing:**
- Error rate trend is "declining" on any active concept
- The learner self-reports feeling overwhelmed
- More than 2 concepts (3 when carryover exists) are currently in "practicing" status simultaneously
- Context gap detected (correct in drills, errors in free speech)

**Concurrent concept gate (enforced by decision engine):** Before scoring any "unseen" concept for introduction, count concepts currently in "practicing" status. If count ≥ 3 (or ≥ 4 with carryover), exclude all unseen concepts from candidates. This gate is checked before PRIORITY scoring.

**When to flag a regression:**
- A concept previously at "acquired" or "automatic" shows error rate > 15% in a session
- Status changes to "regressed" and it re-enters active practice

**When to phase transition (A → B → C → D):**

Phase transition requires ALL of:
1. Every concept that is a prerequisite for any next-phase concept must have status "acquired"
2. All non-prerequisite concepts in the current phase must have status "practicing" (not "unseen", "introduced", or "regressed") with error_trend "stable" or "improving"
3. No concept in the current phase has status "regressed"
4. The learner passes a phase-transition assessment
   - Assessment minimum: at least 10 instances of the target structure in natural conversation, with ≥ 80% accuracy. Include at least one extended narrative (for past tense transitions) or one role-play scenario (for subjunctive/conditional transitions).

Concepts not meeting "acquired" enter `schedule.carryover_concepts` during the phase transition session and begin receiving active practice in session 1 of the new phase. They persist in carryover until acquired or until 3 weeks pass without acquisition (at which point flag in system-health.yaml).

Carryover scaffolding: practice carryover concepts at their current performance level (do not re-scaffold from Stage 1). In sessions that combine carryover and new-phase work, allocate approximately 60% of practice time to the new-phase concept and 40% to carryover consolidation.

Phase A → B specific requirements:
- Must be acquired: A-01, A-02, A-04 (prerequisites for Phase B concepts)
- May carry over: A-03, A-05, A-06, A-07, A-08, A-09

Phase B → C specific requirements:
- Must be acquired: B-01, B-04
- May carry over: B-02, B-03, B-05, B-06, B-07, B-08, B-09, B-10, B-11

Phase C → D specific requirements:
- Must be acquired: C-01, C-04, C-06
- May carry over: C-02, C-03, C-05, C-07, C-08, C-09

**Phase D → Graduation/Maintenance:**
When the learner meets their stated `graduation_criteria` from learner-profile.yaml:
1. Conduct a comprehensive fluency assessment covering all four skills (speaking, listening, reading, writing)
2. If the learner meets their target level: transition `autonomy_level` to "maintenance" in schedule.yaml
3. Maintenance mode: sessions shift to weekly, then biweekly, then on-demand as confidence grows
4. Focus shifts entirely to fluency activities, real-world debriefs, and interest-driven conversation
5. Record a graduation milestone in `state/milestones/`
6. If gaps remain: create a targeted sprint for specific weak areas rather than continuing the full Phase D curriculum

### Homework Assignment Logic

Each session ends with 2-4 assignments. Selection criteria:

1. **Always include SRS review** (Anki, 10-15 min) — non-negotiable daily habit
2. **One skill-targeted assignment** — addresses the session's primary focus using an external tool
3. **One immersion assignment** — listening or reading, preferably aligned to the weekly narrow topic
4. **Optional:** writing (journal entry) or stretch assignment — only if learner has time and energy

Total homework time should match what the learner has available (from learner-profile minus session time).

If the learner consistently doesn't complete all assignments, the tutor reduces quantity rather than letting incomplete work accumulate.

**Narrow topic alignment:** When a weekly topic is active, at least one homework assignment should use content related to that topic. This ensures the learner encounters the same vocabulary across multiple contexts within a week.

**SRS deck management:** The tutor monitors estimated deck size and daily review time. When daily review exceeds 20 minutes:
- Reduce new card additions to 3-5 per session
- Suggest retiring mature cards (interval > 60 days, no recent errors)
- Spot-check retired vocabulary during sessions periodically

**Homework time estimation:**

| Assignment Type | Estimated Minutes |
|----------------|------------------|
| Anki review (existing cards) | 10–20 |
| Anki new cards | 5–10 |
| Dreaming Spanish (comprehensible input video) | 5–15 |
| Podcast (News in Slow Spanish, etc.) | 15–25 |
| Reading (graded reader or article) | 10–20 |
| Journal entry | 10–20 |
| Speechling pronunciation practice | 10–15 |
| Grammar worksheet / drill | 10–15 |
| Conversation partner (italki, etc.) | 30–60 (external, not tutor time) |
| Self-narration (speaking homework) | 5–10 |

**Budget calculation:** Sum estimated minutes for all assigned tasks. Total must not exceed `learner_profile.typical_weekday_minutes - session_duration` (or `typical_weekend_minutes` on weekends). When time is tight, prioritize: (1) Anki review, (2) skill-targeted assignment, (3) immersion.

**External learning load note:** Conversation partner sessions and long podcast episodes count against the daily time budget even though they happen outside the tutor session. Factor them in when they are assigned.

---

## Correction Mode by Activity Type

| Activity Stage | Correction Style | Timing | Limit |
|---------------|-----------------|--------|-------|
| Stage 1–2 (controlled drills) | Explicit, direct | Immediate | No limit — accuracy is the point |
| Stage 3 (guided production) | Recast (model the correct form) | Immediate | No hard limit |
| Stage 4 (communicative practice) | Recast | Batched at end | Max 3 per segment |
| Fluency activities (timed monologue, free conversation) | Meaning-impeding only | Immediate for meaning-impeding; batch all others for post-activity review | Max 3 total |

---

## The Session Flow

### Standard Session (30-45 minutes)

```
Phase 1: Boot & Review (5-8 min)
├── Agent reads state files (silent)
├── Greets learner, asks about energy/time
├── Reviews yesterday's homework
│   ├── What did you complete?
│   ├── How did it go?
│   ├── Any corrections from external tools? (Speechling coach, italki tutor)
│   ├── Verification question (tests homework claim naturally)
│   └── Updates skill-map based on reports AND verification
├── Reviews journal entry if submitted (2-3 corrections, quality notes)
└── Brief warm-up activity (SRS hard cards, quick translation, or similar)

Phase 2: Main Lesson (15-25 min)
├── If introducing new concept:
│   ├── Check l1-interference.yaml for predicted English transfer errors
│   ├── Present concept through examples in context (not abstract rules)
│   ├── Preemptively address L1 interference: "In English you'd say X, but..."
│   ├── Check understanding: "Based on these examples, what pattern do you see?"
│   ├── Controlled practice: fill-in, translation, conjugation
│   └── Semi-free practice: use the concept in a guided conversation
├── If consolidating:
│   ├── Skip explanation, go straight to practice
│   ├── Increase difficulty: less scaffolding, more free production
│   └── Mix with other acquired concepts to test integration
├── If review/regression:
│   ├── Identify the specific failure pattern
│   ├── Targeted drills on the exact weak point
│   └── Re-test in a different context
└── If fluency day (Phase B+):
    ├── Timed monologue: "Talk about X for 2 minutes without stopping"
    ├── Speed translation: rapid-fire English→Spanish
    └── Track pace, hesitation, and risk-taking (not just accuracy)

Phase 3: Free Practice (5-10 min)
├── Open conversation in Spanish on a topic that naturally uses today's focus
├── Ideally aligned with weekly narrow topic for vocabulary reinforcement
├── Tutor notes errors silently, doesn't interrupt flow
├── At the end, provides 2-3 specific corrections with explanation
├── Notes fluency observations (pace, hesitation, circumlocution)
└── Highlights 1-2 things the learner did well

Phase 4: Checkout (3-5 min)
├── Assigns homework with clear, specific instructions
│   └── At least one assignment aligned with weekly narrow topic
├── Assigns journal prompt if writing track is active
├── Asks: "How did today feel?" (calibration check)
├── Brief preview of what's coming next
├── Writes session log and updates state files
└── Encouraging close (specific, genuine, not generic)

Phase 5: State Updates (Silent)
├── Write session log
├── Update skill-map
├── Update schedule
├── Update resource-tracker
├── Update system-health metrics
└── Commit state changes
```

### Micro Session (10-15 minutes)

For days when time is short. The tutor should detect this ("I only have 10 minutes") and shift:

```
├── Skip homework review (note: will review tomorrow)
├── One focused activity: SRS hard cards + 5 min conversation
├── One assignment: the single most valuable thing to do before tomorrow
└── Use micro session log (abbreviated schema — see below)
└── Quick state update
```

**Micro Session Log Schema:**

For sessions under 15 minutes, use this abbreviated log instead of the full session log schema:

```yaml
date: ""
session_number: 0
duration_minutes: 0
session_type: micro
session_status: complete
learner_energy: ""

activity_summary: ""              # one line: what you did
concepts_practiced: []            # list of concept IDs touched
errors_noted:                     # max 3 most important
  - error: ""
    correction: ""
    concept: ""

assignments:
  - task: ""
    resource: ""
    estimated_minutes: 0

next_session:
  recommended_focus: ""
  reason: ""
```

**Micro session recording policy:** Micro sessions record what's available but skip full-detail sections. Specifically: `skill_map_updates` and `learner_observations` are omitted — any concept status changes observed are noted in `activity_summary` and applied to skill-map during the next full session. If homework was reviewed, note it in `activity_summary` rather than the full `assignment_review` structure.

### Weekly Review Session (once per week, replaces normal session)

```
├── Progress summary: what improved this week, what stalled
├── Skill-map review: any reclassifications needed?
├── Resource check: are current external tools at the right level?
├── Goal check: on track for milestones?
├── Weekly summary generation: compress this week's daily logs into state/summaries/
├── System health review: check meta-metrics, adjust approach if needed
├── Schedule adjustment: set next week's narrow topic, plan focus areas
├── Motivation check: what's feeling good, what's feeling tedious?
├── Archive daily logs older than 60 days
├── Milestone celebration if any achievements this week
└── One fun, low-pressure activity (music, a game, casual conversation)
```

### Phase Transition Session (when all concepts in a phase are acquired)

```
├── Integrated assessment: a 15-20 min exercise that combines all phase concepts
│   (e.g., "Tell me a story about a trip, using past tenses, descriptions, and opinions")
├── If passed: celebration, write milestone record, brief intro to what's ahead
├── If gaps found: note specific weak points, extend current phase by 1-2 weeks
├── Update autonomy_level if appropriate (guided → collaborative at Phase B, etc.)
├── Adjust fluency_accuracy_balance for the new phase
├── Resource onboarding: suggest new tools appropriate for next phase
└── Update schedule to reflect new phase
```

### Offline Study Guide Export

When the learner says they'll be offline (traveling, no laptop, etc.), the tutor generates a self-contained study guide:

```
├── Export to state/offline-guides/YYYY-MM-DD.md
├── Include: Anki reminder, specific listening/reading assignments (pre-downloaded),
│   speaking practice prompts, journal prompt, self-narration tasks
├── All assignments are tool-independent (no Claude needed)
├── Designed for the learner's stated available time
└── Next session: tutor reads the offline guide and asks about completion
```

### Real-World Encounter Debrief

When the learner mentions a real-world Spanish encounter (ordered at a restaurant, overheard a conversation, tried to read a sign, had a chat with a native speaker), the tutor switches to debrief mode. These are the highest-value learning moments — real stakes, real emotion, real feedback.

```
Trigger: Learner mentions any real-world Spanish encounter
Protocol:
├── Set aside the planned lesson — this is more valuable
├── Ask what happened — let them tell the story
├── What went well? What did they understand or say successfully?
├── Where did they get stuck? What did they wish they could say?
├── Turn gaps into immediate teaching moments
├── Role-play the scenario: "Let's practice that. I'll be the waiter."
├── Add any gap vocabulary/phrases to Anki assignments
├── Log the encounter in the session log
├── Record as milestone if it's a first (first restaurant order, first phone call, etc.)
└── Detailed protocol in curriculum/tutor-guides/real-world-debrief.md
```

### Post-Session Vault Generation

After writing state files, the tutor generates/updates Obsidian vault content and includes it in the session commit.

- **Full generation** (initial setup, curriculum changes): `python3 scripts/generate-vault.py --full`
- **Per-session update** (after every session): `python3 scripts/generate-vault.py --session --date YYYY-MM-DD`
- Output: `vault/` directory (generated locally, gitignored — regenerated by `scripts/setup.py`)
- The learner opens the repo root as an Obsidian vault to browse progress, grammar notes, and milestone history

See spec at `docs/superpowers/specs/2026-04-06-system-audit-and-obsidian-vault-design.md` for full vault architecture.

---

## State Validation Protocol

At startup, after reading state files but before greeting the learner, the tutor runs validation checks to catch corruption or inconsistencies from prior sessions.

```
Validation checks:
1. Can all YAML files be parsed? (If not → load error-recovery.md)
2. Does skill-map have entries for all concepts in the current phase?
3. Are there status/error_rate contradictions?
   (e.g., status: "acquired" but error_rate_production: 0.40 → flag and investigate)
4. Is the session log sequence reasonable? (no future dates, no impossible gaps)
5. Does schedule.yaml reference concepts that exist in skill-map?
6. Are vocabulary counts consistent? (passive_known >= active_known always)
7. Is learner-profile populated for critical fields? (name, target_dialect, goals)

If validation fails:
├── Severity LOW (fixable inconsistency):
│   Auto-fix silently. Log the fix in system-health.yaml.
│   Example: recalculate error_rate from recent session data.
├── Severity MEDIUM (ambiguous state):
│   Fix and inform learner briefly: "I noticed a small data issue
│   and corrected it — your preterite skill was marked inconsistently."
├── Severity HIGH (unparseable file or major corruption):
│   Load curriculum/tutor-guides/error-recovery.md
│   Attempt to recover from snapshot: "python3 scripts/snapshot-state.py restore"
│   Or from git history if state is tracked: "git log --oneline state/"
│   If not recoverable, rebuild state from recent session logs
└── Always log validation issues in system-health.yaml
```

---

## Parking Lot — Learner-Initiated Gap Reporting

The `parking-lot.md` file in the repo root is editable by the learner at any time, between sessions. It captures questions, encountered words, and situations where they got stuck.

```markdown
# Parking Lot — Things I Want to Learn

Add anything here between sessions. Your tutor will review this at the
start of each session and work items into lessons.

- Heard "sin embargo" in a podcast, what does it mean?
- How do I say "I would have gone" in Spanish?
- At the restaurant, I couldn't remember how to ask for the check
- What's the difference between "por" and "para"?
```

**Tutor protocol:**
1. Read `parking-lot.md` during startup (add to startup protocol)
2. If items exist, address the most relevant 1-2 during the session
3. Items that match upcoming curriculum can wait — tell the learner: "Great question — we'll cover that in about 2 weeks when we hit subjunctive."
4. Items that are urgent (upcoming real-world need) get addressed immediately
5. Mark items as addressed by moving them to a "Completed" section at the bottom
6. The parking lot gives the learner agency between sessions and surfaces real gaps

---

## Narrow Input / Topic Cycling

Research on comprehensible input shows that consuming multiple pieces of content on the same topic is more effective than varied content. Vocabulary repeats naturally across related content, reinforcing without drilling.

**Implementation:** Each week has a theme. All homework assignments (listening, reading, writing, conversation) orbit the same topic.

```
Example Week — Topic: "Childhood and Family"

Monday:    Dreaming Spanish video about someone's childhood
Tuesday:   Graded reader story about family dynamics
Wednesday: Tutor conversation: "Cuéntame sobre tu infancia"
Thursday:  News in Slow Spanish: article about family traditions in Latin America
Friday:    Journal entry: "Mi familia y cómo era mi niñez"
Saturday:  Fun: watch an episode of a show, notice family-related vocabulary
```

The same vocabulary (infancia, crecer, recuerdos, hermanos, costumbres) appears in 5+ different contexts in one week. This is far more effective than Monday=food, Tuesday=weather, Wednesday=politics.

**Topic selection criteria:**
- Aligned with current grammar focus (talking about childhood = imperfect tense practice)
- Aligned with current vocabulary cluster
- Interesting to the learner (use learner profile interests)
- Appropriate for current CEFR level
- Rotates to avoid staleness

---

## Assessment Framework

### Continuous Assessment (Every Session)

The tutor evaluates during natural interaction. For every error or success in conversation:

| Signal | What it indicates | How it's recorded |
|--------|------------------|-------------------|
| Correct verb conjugation in free speech | Grammar concept is moving toward "acquired" | Positive data point for that concept |
| Self-correction ("wait, no, it's...") | Awareness is ahead of automaticity — good sign | Note: concept is in late "practicing" stage |
| Same error repeated across sessions | Concept is stuck — needs different approach | Error trend: "stable" or "declining" |
| Correct in drill, wrong in conversation | Context gap — knows the rule but can't apply under cognitive load | Update `performance_scaffolded` and `performance_unscaffolded` — scaffolded competent but unscaffolded struggling indicates a transfer gap. |
| Uses a concept not yet formally taught | Natural acquisition happening — adjust curriculum | May skip formal introduction, confirm and move on |
| Avoids a structure (talks around it) | Learner doesn't trust their ability with it — needs more practice | Note avoidance pattern, assign targeted practice |
| Comprehends but can't produce | Typical comprehension-production gap | Weight output practice higher |
| Speaks fluidly with minor errors | Fluency developing well, accuracy will follow | Note in fluency metrics, don't over-correct |
| Uses English word mid-sentence | Vocabulary gap — specific word needed | Add to Anki, note for next vocab cluster |

### Homework Verification

Self-reported homework completion is cross-referenced with in-session performance:

- **After reported listening:** "What was the video/podcast about? Tell me in Spanish." Tests both comprehension and production.
- **After reported reading:** "What happened in the story?" or "What was the article's main argument?"
- **After reported Anki:** "Let me quiz you on a few from this week's deck."
- **After reported conversation partner session:** "What did you talk about? Did they correct anything?"

The tutor tracks calibration between self-reports and observed performance. Over time, it learns how much to trust each learner's self-assessment.

### Verification Strategy by Assignment Type

| Assignment Type | Verification Approach | Red Flag |
|----------------|----------------------|----------|
| Anki review | Quiz 2-3 cards from the deck in conversation | Claims completion but can't recall any recent cards |
| Dreaming Spanish / listening | "¿De qué trataba?" — ask for summary in Spanish | Vague summary that could apply to any video |
| Graded reader / reading | Ask about a specific detail or character | Only recalls the topic, not content |
| Journal entry | Read it (it's in `journal/`). Correct 2-3 errors. | Entry is suspiciously short or copied |
| Speechling / pronunciation | Ask them to type a word that uses the target sound. Note if they report difficulty. | Skipped entirely — watch for pattern |
| Conversation partner (italki) | "¿De qué hablaron?" + "¿Qué palabra nueva aprendiste?" | Can't recall any specifics |

Don't interrogate — weave verification into warm-up conversation naturally. If a learner consistently doesn't complete assignments, reduce load before confronting.

### Periodic Formal Assessment

**Monthly placement check:**
The tutor conducts a structured assessment covering all "acquired" and "automatic" concepts. Not a test — framed as "let's see how far we've come." This catches silent regressions and validates the skill map.

**Phase transition assessment:**
A longer, integrated exercise before moving to the next phase. See Session Flow section.

**External benchmarks (optional):**
- Kwiziq placement test (free online, gives CEFR level by grammar topic)
- DELE practice exams (when approaching B1+)
- The tutor suggests these at appropriate milestones

### Self-Assessment Calibration

The tutor tracks the learner's self-assessment against actual performance:

```
If self_reported_confidence > actual_performance:
    Learner is overestimating. Don't advance yet.
    Gently increase challenge to reveal the gap.
    Increase verification questions for homework.

If self_reported_confidence < actual_performance:
    Learner is underestimating (common with perfectionists).
    Show them evidence of progress. Boost confidence.
    Pull early journal entries vs recent ones as tangible proof.

If self_reported_confidence ≈ actual_performance:
    Calibration is good. Trust their judgment more in decisions.
    Reduce verification overhead.
```

---

## Fluency vs. Accuracy Balance

The system tracks and develops both dimensions, but the emphasis shifts by phase:

| Phase | Balance | What this means in practice |
|-------|---------|---------------------------|
| A (Foundation) | Accuracy-leaning | Build correct habits before they fossilize. But always praise communication. "I understood you perfectly — and here's how to make it more precise." |
| B (Conversational) | Accuracy-leaning | Still building core grammar. But introduce fluency activities 1x/week: timed speaking, self-narration. |
| C (Intermediate) | Balanced | Fluency and accuracy get equal weight. Timed monologues, reduced correction frequency. Only correct repeated or high-impact errors. |
| D (Advanced) | Fluency-leaning | Focus on smoothness, natural rhythm, spontaneity. Correct only errors that impede meaning or sound unnatural. |

**Fluency-specific activities:**
- **Timed monologues:** "Talk about X for 2 minutes without stopping. Don't worry about mistakes." Then review.
- **Speed translation:** Rapid-fire English→Spanish, building reaction time.
- **Shadowing:** Listen to native speech and repeat simultaneously — builds rhythm and pace.
- **Retelling:** Listen to a story, then retell it. First attempt is rough; second is smoother. Track the delta.
- **Self-narration:** Describe daily activities in Spanish in real-time (assigned as homework).

**Typed vs. oral fluency:** These are distinct skills and must be tracked separately. A learner may write fluently but hesitate severely in speech (common with introverts and grammar-focused learners), or speak fluidly but struggle with written structure (common with immersion learners). The fluency balance table above applies primarily to oral production. Written fluency is developed through the writing track (journal, composition) and assessed separately via the writing rubric. Do not conflate the two when adjusting the fluency-accuracy balance.

---

## Writing Track

Writing develops alongside other skills, with escalating complexity:

| Phase | Writing Level | Activities |
|-------|-------------|------------|
| A | Sentence-level | Write 5 sentences using today's grammar. Anki cards with personal example sentences. |
| B | Paragraph-level | Journal entries (3-5 sentences daily). Paragraph descriptions. Homework summaries in Spanish. |
| C | Structured composition | Short emails. Opinion paragraphs. Summaries of podcasts/articles in Spanish. |
| D | Extended writing | Essay responses. Creative writing. Professional correspondence. Article summaries and critiques. |

**Journal system:** The `journal/` directory contains dated markdown files. The learner writes 3-7 sentences daily in Spanish. The tutor reviews entries at the start of the next session — correcting errors, noting improvement, and extracting grammar/vocabulary data.

Writing is high-signal for assessment: the learner has time to think, so errors reveal genuine gaps (not just performance pressure under conversational speed).

**Writing rubric — 4 dimensions tracked in `state/skill-map.yaml` under `writing:`:**

| Dimension | Introduced | Practicing | Acquired |
|-----------|-----------|-----------|---------|
| **Sentence Construction** | Attempts complete sentences; frequent agreement/verb errors | Mostly correct simple sentences; errors on complex structures | Consistently correct sentences including subordinate clauses |
| **Paragraph Coherence** | Ideas present but loosely connected; no clear structure | Uses some connectors (pero, porque, también); paragraphs have a point | Ideas flow logically; topic sentence + support + conclusion evident |
| **Formal Register** | Uses only casual/spoken forms in all contexts | Attempts register shifts when prompted; some errors | Selects register appropriately for context without prompting |
| **Creative Expression** | Translates directly from English; formulaic | Occasionally uses Spanish-native phrasing or idioms | Writes with natural Spanish rhythm; uses idiomatic expressions spontaneously |

Update writing dimension status in `skill-map.yaml` after reviewing journal entries. A dimension moves from `practicing` to `acquired` when it meets the "Acquired" criteria across 3+ consecutive journal entries without regression.

---

## Motivation System

### Detection

The tutor tracks motivation signals across sessions:

| Signal | What it suggests |
|--------|-----------------|
| Sessions getting shorter | Losing engagement — make sessions more interesting, not longer |
| Homework completion dropping | Overloaded or bored — reduce load and add variety |
| Self-assessments consistently "about right" | Comfort zone — might need a challenge push |
| No new concepts introduced in 3+ weeks | Plateau — learner may feel stuck |
| Learner says "I'm not making progress" | Explicit flag — show evidence of progress immediately |
| Gap between sessions increasing | Life stress or motivation dropping — don't guilt, adapt |
| Learner brings own questions/topics | High engagement — they're thinking about Spanish outside sessions |
| Excited about a breakthrough | Ride the wave — introduce something slightly harder |

### Intervention Playbook

| Situation | Intervention |
|-----------|-------------|
| **Novelty wearing off** (weeks 3-6) | Introduce first "real" content (a song, a short video they actually enjoy). Shift from "studying" to "using." |
| **First plateau** (months 2-4) | Show concrete progress: compare early journal entries to recent ones. "In session 1 you couldn't introduce yourself. Listen to what you said yesterday." |
| **Intermediate plateau** (months 6-10) | Change modality: if they've been doing mostly grammar, shift to immersion. Introduce a compelling show or book. Set a concrete short-term goal. |
| **After a break** | Lighter session, quick wins, no new material. Rebuild momentum before advancing. |
| **Boredom with routine** | Rotate activity types. Surprise them: a game, a riddle in Spanish, a funny video, teach them slang. |
| **Frustration with specific concept** | Temporarily shelve it. Work on something else where they'll succeed. Come back in a week with a different approach. |
| **Sprint mode** (upcoming trip, event, meeting) | Temporarily reprioritize toward the deadline. Travel vocabulary, survival phrases, specific scenarios. Log the sprint in schedule.yaml. |

### Milestone Celebrations

The tutor explicitly celebrates and records achievements:

- First time understanding a native speaker without subtitles
- First 30-day session streak
- First conversation entirely in Spanish
- First spontaneous use of subjunctive
- Each phase completion
- Reaching 500, 1000, 2000, 3000, 5000 known words
- First time thinking in Spanish
- First time dreaming in Spanish (learners report this!)

These get recorded in `state/milestones/` as permanent records.

---

## Learner Autonomy Progression

The system gradually hands control to the learner as they advance:

| Phase | Autonomy Level | Tutor Role | Learner Role |
|-------|---------------|------------|-------------|
| A | `guided` | Tutor decides everything. Picks focus, resources, homework. | Shows up and follows instructions. |
| B | `guided` → `collaborative` | Tutor proposes plan. "I was going to focus on X, but is there something you'd rather work on?" | Can redirect, bring questions, request specific topics. |
| C | `collaborative` | Tutor and learner co-decide. "What did you read/watch this week? Let's work with that." | Starts choosing input material. Brings topics from their life. |
| D | `learner-led` | Learner drives most decisions. Tutor catches blind spots and provides accountability. | Sets own goals, chooses content, identifies weak areas. |
| Post-D | `maintenance` | Weekly or monthly check-ins. On-demand help. | Fully independent learner. |

**Graduation:** The system defines what "done" looks like based on the learner's stated goals. When the learner consistently operates at their target level with minimal tutor intervention, the system shifts to maintenance mode: weekly check-ins, then monthly, then on-demand.

---

## Curriculum Design

### Curriculum Content Strategy

The curriculum files serve as **guardrails and structure**, not scripts. Each file provides:

- **Sequencing:** What to teach when, and what depends on what
- **Known pitfalls:** Common errors, L1 interference, and tricky areas
- **Drill templates:** Reusable exercise formats the tutor can adapt
- **Signs of acquisition:** What mastery looks like for each concept

The tutor uses its own knowledge of Spanish for:

- **Generating examples** in real-time (more natural than pre-written lists)
- **Conducting conversation** (impossible to script)
- **Explaining concepts** (adapts to the learner's style and questions)
- **Creating contextual drills** (uses the learner's life and interests)

**This means:** Curriculum files must be populated before the system is usable, but they don't need to contain complete lessons. They need enough structure to prevent the tutor from drifting (teaching things out of order, missing pitfalls, advancing too fast). The tutor fills in the rest.

**Minimum content needed before session 1:**
- All files in `curriculum/onboarding/` (sessions 1-10)
- All files in `curriculum/grammar/A-foundation/`
- All files in `curriculum/vocabulary/tier1-survival/`
- `curriculum/l1-interference.yaml`
- `curriculum/dialect-notes.yaml`
- `curriculum/topic-bank.yaml`

Later phases can be written as the learner approaches them.

### Communication Repair (Concept #0)

Before any grammar is taught, the learner needs survival phrases for when they're stuck. These are taught in session 1-2 and drilled until automatic:

```
curriculum/grammar/A-foundation/00-communication-repair.md

Core phrases (must be automatic by session 5):
- "¿Puedes repetir, por favor?" — Can you repeat that?
- "¿Qué significa [word]?" — What does [word] mean?
- "¿Cómo se dice [English word]?" — How do you say [word]?
- "No entiendo" — I don't understand
- "Más despacio, por favor" — More slowly, please
- "¿Puedes hablar más lento?" — Can you speak slower?

Circumlocution strategies (introduced in session 3-5):
- "Es como..." — It's like...
- "Es una cosa que..." — It's a thing that...
- "Es el lugar donde..." — It's the place where...
- Describing with basic words when you don't know the specific term

Why this is concept #0:
These phrases are more immediately useful than any grammar point.
They transform the learner from someone who freezes when stuck
to someone who can navigate uncertainty. They also model good
language learning behavior: asking for help is a skill, not a weakness.
```

### Grammar Progression

Ordered by frequency of use, prerequisite dependencies, and learner impact.

**Phase A — Foundation** (target: A1-A2)
Core sentence construction. The learner can form basic sentences about present situations. 10 concepts (8 in onboarding + 2 post-onboarding).

| # | Concept | Prerequisites | Key Challenge | L1 Interference |
|---|---------|--------------|---------------|-----------------|
| 0 | Communication repair phrases | None | Memorization, overcoming embarrassment | — |
| 1 | Present tense (regular -ar, -er, -ir) | None | Memorizing conjugation patterns | Subject pronoun overuse |
| 2 | Ser vs Estar | A-01 | Conceptual — English has one "to be" | Ser/estar confusion |
| 3 | Gender, number, agreement + demonstratives + possessives | None | No English equivalent, must build habit | Adjective placement |
| 4 | Articles, prepositions, personal 'a' | A-03 | Memorization + gender dependency | Preposition mapping |
| 5 | Basic questions and negation | A-01 | Inversion, question words | Double negative avoidance |
| 6 | Gustar-type verbs (gustar, encantar, molestar, importar, interesar, doler) | A-01 | Reversed sentence structure | Gustar construction |
| 7 | Common irregular present (ir, tener, querer, poder, hacer, decir, saber/conocer, hay) | A-01 | High-frequency, must memorize individually | — |
| 8 | Numbers, quantifiers, tener expressions | A-03 | Gender agreement on quantifiers, tener for age/states | Age with ser instead of tener |
| 9 | Accent and stress rules | None | Systematic understanding, not piecemeal | English stress patterns applied to Spanish |

**Note:** A-08 and A-09 are introduced post-onboarding via the decision engine (sessions 11+). See onboarding section.

**Phase B — Conversational** (target: A2-B1)
The learner can talk about the past and future, handle daily interactions. 11 concepts.

| # | Concept | Prerequisites | Key Challenge | L1 Interference |
|---|---------|--------------|---------------|-----------------|
| 1 | Preterite (regular) | A-01 | New conjugation set | — |
| 2 | Preterite (irregular) | B-01 | Memorization-heavy | — |
| 3 | Imperfect | A-01 | New tense concept | — |
| 4 | Preterite vs Imperfect | B-01, B-02, B-03 | The hardest A2-B1 concept | English doesn't distinguish aspect |
| 5 | Reflexive verbs | A-01 | Pronoun placement | — |
| 6 | Direct object pronouns | A-01, A-04 | Word order changes | — |
| 7 | Indirect object pronouns | B-06 | Stacking pronouns (se lo dije) | — |
| 8 | Estar + gerund (progressive) | A-01, A-02 | Progressive formation | Progressive overuse for habitual actions |
| 9 | Imperatives (tu/usted commands) | A-01, A-07 | Irregular forms, pronoun attachment | Pronoun placement with commands |
| 10 | Comparatives and superlatives | A-03 | Irregular forms (mejor, peor) | de vs que distinction |
| 11 | Future with ir + a | A-01 | Easy win — builds confidence | — |

**Phase C — Intermediate** (target: B1-B2)
The learner can express opinions, hypotheticals, and complex ideas. 9 concepts.

| # | Concept | Prerequisites | Key Challenge | L1 Interference |
|---|---------|--------------|---------------|-----------------|
| 1 | Present subjunctive (forms) | A-01, A-07 | New paradigm | Subjunctive avoidance |
| 2 | Subjunctive triggers | C-01 | Knowing WHEN to use it | — |
| 3 | Formal future tense | A-01 | Easy forms, nuance vs ir + a | — |
| 4 | Conditional | C-03 | Same stems, different endings | — |
| 5 | Por vs Para | A-04 | Notoriously difficult, many rules | — |
| 6 | Present perfect and compound tenses | B-01 | Relatively easy if preterite is solid | — |
| 7 | Relative clauses (que, quien, donde, lo que) | C-01 | Sentence complexity jumps | — |
| 8 | Indirect speech (me dijo que..., queria saber si...) | C-01, C-02, B-04 | Tense shifting with subjunctive | Tense shifting with subjunctive |
| 9 | Diminutives and augmentatives (-ito/-ita, -ote/-ota) | A-03 | Regional variation, register awareness | Diminutive underuse |

**Phase D — Advanced** (target: B2-C1)
The learner can handle nuanced expression, formal contexts, and complex narration. 6 concepts.

| # | Concept | Prerequisites | Key Challenge |
|---|---------|--------------|---------------|
| 1 | Past subjunctive (imperfect subjunctive) | C-01, B-03 | Two forms (-ra, -se) |
| 2 | Si clauses (if...then) | C-04, D-01 | Three types with different tense combos |
| 3 | Subjunctive across all tenses | D-01, C-06 | Integration challenge |
| 4 | Passive voice and se constructions | B-01 | Multiple uses of "se" |
| 5 | Register shifting (tú/usted/vos) | — | Social/cultural knowledge |
| 6 | Nuanced connectors (sin embargo, no obstante, a pesar de que) | — | Elevates speech from functional to fluent |

### Grammar Concept File Format

Each grammar concept markdown file follows this template (~2 pages per concept). The teaching sequence encodes the SHAPE of the lesson; the tutor provides the specific content.

```markdown
# [Concept Name]

## Overview
1-2 sentences: what this concept is and why it matters for communication.

## When to Teach
- Phase: [A/B/C/D]
- Prerequisites: [list]
- L1 interference to preempt: [reference l1-interference.yaml IDs]

## The Pattern
Clear grammatical explanation with paradigm tables as needed.
Show the pattern before explaining the rule.

## Examples in Context
8-10 sentences using the concept naturally.
**Bolded** target structures.
Dialect-appropriate vocabulary.
Graduated: simple to complex.

## L1 Interference
English habits that cause errors with this concept.
Contrast pairs: English instinct vs correct Spanish.
Preemption script: what to say BEFORE the learner makes the error.

## Common Errors
3-5 most frequent errors with corrections.
Each classified: developmental, L1 interference, or overgeneralization.

## Teaching Sequence

### Stage 1: Noticing
1-2 activities where the learner discovers the pattern before explicit instruction.
"Look at these sentences. What do you notice about...?"

### Stage 2: Controlled Practice
1-2 drill formats with concept-specific items.
References activity templates by name for reusable formats.

### Stage 3: Guided Production
1-2 structured conversation prompts requiring the concept.
Scaffolding strategies and how to reduce them.

### Stage 4: Communicative Practice
1-2 open-ended tasks where the concept is needed but focus is on meaning.
Topic suggestions that naturally elicit this structure.

## Dialect Notes
Relevant dialect differences. Cross-references dialect-notes.yaml.

## Signs of Acquisition
- Scaffolded: [what competence looks like in drills]
- Unscaffolded: [what competence looks like in free conversation]
- Integrated: [what competence looks like when combined with other concepts]

## Connection Points
How this relates to other concepts. What it enables, what it builds on.
Common regression triggers when later concepts are introduced.
```

### Vocabulary Progression

Vocabulary clusters are paired with grammar phases so that new words reinforce new structures.

| Phase | Vocabulary Tiers | Target Word Count |
|-------|-----------------|-------------------|
| A | Tier 1: Survival | 300-500 active words |
| B | Tier 2: Daily Life | 800-1,500 active words |
| C | Tier 3: Social | 2,000-3,000 active words |
| D | Tier 4: Abstract | 4,000-5,000+ active words |

Each vocabulary cluster file contains 40-60 words (30 core + 20 exposure). Core words become Anki cards with personal example sentences; exposure words are for passive recognition only.

Cluster contents:
- Core and exposure words grouped by subtopic
- Example sentences using current-phase grammar (for core words with non-obvious usage)
- Common collocations (words that go together)
- False cognates and tricky translations
- Cultural and pragmatic notes where relevant
- Pronunciation notes for tricky words
- Dialect variations for key vocabulary

### Pronunciation Progression

Not a separate phase — woven in throughout, with specific focus areas:

| When | Focus |
|------|-------|
| Phase A | Vowel sounds (consistent, pure), basic consonants, stress rules |
| Phase B | R vs RR, soft D (dado), B/V equivalence, linking between words |
| Phase C | Soft G (gente), J sound, Ñ, LL/Y, intonation patterns |
| Phase D | Regional accent awareness, natural rhythm, reduction of English accent |

---

## Emotional Intelligence Framework

### Emotional States to Watch For

| Signal | Likely emotion | Response |
|--------|---------------|----------|
| "I'll never get this" | Frustration, hopelessness | Show concrete evidence of past progress. Normalize the struggle. "This is the hardest part of B1. Everyone hits this wall." |
| Avoiding speaking, giving one-word answers | Shame, embarrassment | Reduce pressure. Switch to a receptive activity. Come back to production tomorrow. |
| "This is boring" | Disengagement | Change modality immediately. "Let's ditch the drill — tell me about [something they care about] in Spanish." |
| Comparing to others | Insecurity | "Everyone's path is different. You're [specific thing they do well]." |
| Excited after a breakthrough | Joy, confidence | Ride the wave. This is the session to introduce something slightly harder. |
| Silent after an error | Processing or shutting down | Give space. Don't pile on with more corrections. Acknowledge: "That's a tricky one." Move on. |
| Rushing through exercises | Wanting to be done, low engagement | Check in: "Do you want to keep going or wrap up early today?" Honor their answer. |
| Asking lots of "why" questions | Intellectual engagement | Feed it. This learner wants to understand the system, not just memorize. |

### Never Say

- "That's easy" (invalidates their struggle)
- "You should know this by now" (creates shame)
- "Most people get this faster" (comparison)
- "Let's try again" immediately after a failure (give them a beat)
- "Good job!" with no specificity (feels hollow)

### Instead

- Name what they did right specifically: "You used the subjunctive there without thinking about it — that's new."
- Normalize difficulty: "Preterite vs imperfect trips up everyone. Even advanced speakers pause on this sometimes."
- Frame errors as data: "Interesting — you went with ser there. Let's think about why estar fits better here."
- Show trajectory: "Look at your journal from last month — you're writing twice as much now."

---

## Failure Modes and Mitigations

| Failure Mode | Detection | Mitigation |
|-------------|-----------|------------|
| **State file corruption** | Agent can't parse YAML | Restore from snapshot (`scripts/snapshot-state.py restore`), or git history if state is tracked. CLAUDE.md includes recovery instructions. |
| **Agent misreads state** | Assigns already-acquired concepts or skips prerequisites | Session startup includes a sanity check: "Based on your records, you're working on X. Sound right?" Learner can correct. |
| **Methodology drift** | Agent stops following assessment protocol | CLAUDE.md is re-read every session. Key behaviors are explicit instructions, not suggestions. |
| **Learner games self-assessments** | Self-reports consistently diverge from performance | Tutor tracks calibration gap. If persistent, weights observed performance over self-reports and increases verification questions. |
| **Learner stops showing up** | Gap in session logs | Next session acknowledges the gap, does a quick diagnostic to check for decay, adjusts schedule. No guilt. |
| **Plateau at intermediate** | Skill map shows no advancement for 3+ weeks | Tutor flags this, suggests changing approach: new resource type, conversation partner, immersion experience, or sprint goal. Triggers motivation intervention. |
| **Homework overload** | Completion rate drops below 60% | Reduce assignment count. Prioritize high-impact items. Ask learner what feels manageable. |
| **Wrong difficulty level on resources** | Learner reports <70% comprehension or >95% comprehension | Adjust resource level. Track 85% comprehension target. |
| **Boredom / motivation loss** | Engagement drops, sessions get shorter, homework skipped | Trigger motivation intervention playbook. Rotate activity types, introduce fun content, revisit goals. |
| **Over-reliance on English** | Learner answers in English when they could use Spanish | Tutor gradually increases Spanish usage expectations. Phase A: mostly English. Phase C+: sessions primarily in Spanish. |
| **L1 errors fossilizing** | Same English transfer error persists across 5+ sessions despite correction | Change approach: different explanation, visual aid, explicit L1 contrast, dedicated drill. Escalate in l1-interference tracking. |
| **SRS deck overwhelming** | Anki daily review exceeds 20 minutes, learner reports burnout | Retire mature cards, reduce new card rate, audit deck with learner. |
| **Session log bloat** | 60+ daily logs accumulating | Weekly summarization protocol compresses old logs. Archive after 60 days. |
| **System effectiveness declining** | system-health metrics trending wrong direction | Weekly review includes system self-assessment. Tutor adjusts its own approach, not just the learner's plan. |

---

## Language of Instruction

The session language shifts as the learner advances:

| Phase | Tutor Language | Learner Expected Language |
|-------|---------------|--------------------------|
| A (Foundation) | 80% English, 20% Spanish | English with Spanish practice segments |
| B (Conversational) | 50% English, 50% Spanish | Mix — Spanish for practiced topics, English for new concepts |
| C (Intermediate) | 20% English, 80% Spanish | Mostly Spanish, English for complex grammar explanations |
| D (Advanced) | 5% English, 95% Spanish | Spanish for everything, English only if truly stuck |

The tutor adjusts within these ranges based on the learner's comfort and the activity type. Grammar explanations may stay in English longer; conversation practice moves to Spanish faster.

---

## Dialect Configuration

The system adapts to the learner's target dialect without maintaining separate curriculum tracks. Instead, a `curriculum/dialect-notes.yaml` file provides dialect-specific adjustments that the tutor applies on top of the shared curriculum.

```yaml
# curriculum/dialect-notes.yaml
vocabulary_differences:
  - neutral: "coche"
    mexican: "carro"
    castilian: "coche"
    argentinian: "auto"
    colombian: "carro"
    context: "car"
  - neutral: "computadora"
    castilian: "ordenador"
    context: "computer"
  - neutral: "apartamento"
    castilian: "piso"
    context: "apartment"
  # ... (50-100 high-frequency differences)

grammar_differences:
  - feature: "voseo"
    regions: [argentina, uruguay, parts of central america]
    introduce_at: Phase C
    description: "Replace tú conjugation with vos forms (vos tenés, vos querés)"
    notes: "Teach recognition in Phase B, production in Phase C for target dialects"
  - feature: "leísmo"
    regions: [spain]
    introduce_at: Phase D
    description: "Using 'le' where Latin America uses 'lo' for masculine direct objects"
  - feature: "ustedes vs vosotros"
    regions: [spain uses vosotros, all of latin america uses ustedes]
    introduce_at: Phase A
    description: "In Latin American Spanish, skip vosotros entirely. In Castilian, teach both."

pronunciation_differences:
  - feature: "seseo vs distinción"
    castilian: "Distinguish between s/z/c sounds (zapato with 'th')"
    latin_america: "All pronounced as 's' (seseo)"
    introduce_at: Phase A
    notes: "Affects which pronunciation model to follow from day 1"
  - feature: "yeísmo"
    most_dialects: "ll and y are pronounced the same"
    rioplatense: "ll/y pronounced as 'sh' (Argentine Spanish)"
    introduce_at: Phase B
```

**Tutor protocol:**
1. Read the learner's `target_dialect` from learner-profile.yaml
2. When introducing vocabulary, use the dialect-appropriate term and mention alternatives: "In Mexico we say 'carro.' In Spain you'd hear 'coche.' Since you're focused on Mexican Spanish, we'll use 'carro.'"
3. When teaching pronunciation, follow the dialect's model from day 1
4. Grammar differences are introduced at the phases noted in the file
5. When assigning media, prefer content from the target dialect region

---

## Progress Reports

YAML state files are transparent but not motivating. The system generates human-readable progress reports during weekly reviews, stored in `progress-reports/`.

```markdown
# progress-reports/2026-W13.md
# Week 13 Progress — March 23-29

**Sessions this week:** 5 of 7
**Current streak:** 18 days (personal best!)
**Phase:** A-Foundation (week 6)

## What Improved
- Preterite irregular verbs are clicking — you used "hice" and "fui"
  correctly in free conversation for the first time this week
- Listening comprehension moved up to Dreaming Spanish intermediate level
- Journal entries are noticeably longer and more complex than 2 weeks ago

## Still Working On
- Gender agreement slips when speaking fast (correct in writing — context gap)
- "Mariscos" and "propina" keep coming back as hard Anki cards
- Pronunciation: rr trill still inconsistent (Speechling coach noted improvement though)

## By the Numbers
- Active vocabulary: ~680 words (up from ~620 last week)
- Passive vocabulary: ~920 words
- Grammar concepts acquired: 4 of 6 in Phase A
- Homework completion: 85%
- CEFR estimate: A2 (solid, approaching B1 in listening)

## What's Ahead
- Next week's focus: Preterite vs imperfect — this is the big one
- Weekly topic: "Childhood and family" (natural pairing with imperfect tense)
- Goal check: On track for B1 by your June trip

## Highlight of the Week
Wednesday you told a full story about your weekend entirely in Spanish
without switching to English once. That's a first. 🎯
```

**The tutor generates this during weekly review and writes it to `progress-reports/`.** The learner can read it anytime. Over months, the collection of reports becomes a motivating record of the journey.

---

## Known Limitations

### Text-Based Tutoring Constraints

The tutor interacts through text. This means:

- **Fluency metrics** (speaking_pace, hesitation_frequency, self_correction_rate) are estimated from external tool reports and typed interaction patterns, not direct observation. They are lower-confidence than grammar error rates.
- **"Free conversation"** in sessions is typed. The learner has more processing time than real speech. The system has a built-in optimism bias for unscaffolded performance assessment.
- **Pronunciation** is entirely outsourced to Speechling, Forvo, and Whisper. The tutor assigns and tracks, but does not directly teach or assess.

### Mitigations

- italki/Tandem recommended from Phase B specifically because the tutor cannot assess spoken fluency
- Self-narration homework provides spoken practice the tutor cannot directly offer
- Speechling provides human pronunciation feedback the tutor cannot give
- The system is most accurate for grammar and vocabulary assessment, less accurate for pronunciation and spoken fluency

### Minimum Viable Commitment

- **Light:** 15-minute micro-session + 10 minutes Anki = 25 minutes/day
- **Typical:** 30-minute session + 20-30 minutes homework = 50-60 minutes/day
- **Full:** 45-minute session + 45-60 minutes homework = 90-105 minutes/day

---

## Privacy and Data

All state is stored locally in the repo. No data leaves the machine except:
- When Claude Code processes the session (standard Claude API usage)
- When the learner uses external tools (Anki, Speechling, etc. — governed by those tools' policies)

The learner owns all their data and can inspect, edit, or delete any state file at any time.
