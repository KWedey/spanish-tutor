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
├── CLAUDE.md                        # Core tutor instructions (~150 lines, concise)
├── parking-lot.md                   # Learner-editable list of questions and gaps
├── docs/
│   ├── system-design.md             # This document
│   ├── claude-md-draft.md           # CLAUDE.md draft for review
│   └── resource-ecosystem.md        # External tools catalog
├── curriculum/
│   ├── tutor-guides/                # Conditional reference docs (loaded per session type)
│   │   ├── first-session.md         # Read only on session 1
│   │   ├── onboarding-guide.md      # Read during sessions 2-10
│   │   ├── weekly-review-guide.md   # Read on weekly review day
│   │   ├── emotional-intelligence.md # Read when motivation low or emotional signal
│   │   ├── l1-interference-protocol.md # Read when introducing new concepts
│   │   ├── fluency-activities.md    # Read in Phase C+
│   │   ├── sprint-mode.md           # Read when sprint is active
│   │   ├── real-world-debrief.md    # Read when learner reports real-world encounter
│   │   └── error-recovery.md        # Read when state validation fails
│   ├── onboarding/                  # Fixed starter sequence (sessions 1-10)
│   │   ├── session-01-discovery.md
│   │   ├── session-02-first-words.md
│   │   ├── session-03-present-tense-intro.md
│   │   └── ...through session-10.md
│   ├── grammar/                     # Grammar concept definitions
│   │   ├── A-foundation/
│   │   │   ├── 00-communication-repair.md  # FIRST concept: survival phrases for when you're stuck
│   │   │   ├── 01-present-regular.md
│   │   │   ├── 02-ser-vs-estar.md
│   │   │   ├── 03-gender-agreement.md
│   │   │   ├── 04-articles-prepositions.md
│   │   │   ├── 05-basic-questions.md
│   │   │   └── 06-present-irregular-common.md
│   │   ├── B-conversational/
│   │   │   ├── 01-preterite-regular.md
│   │   │   ├── 02-preterite-irregular.md
│   │   │   ├── 03-imperfect.md
│   │   │   ├── 04-preterite-vs-imperfect.md
│   │   │   ├── 05-reflexive-verbs.md
│   │   │   ├── 06-direct-object-pronouns.md
│   │   │   ├── 07-indirect-object-pronouns.md
│   │   │   └── 08-future-ir-a.md
│   │   ├── C-intermediate/
│   │   │   ├── 01-present-subjunctive.md
│   │   │   ├── 02-subjunctive-triggers.md
│   │   │   ├── 03-formal-future.md
│   │   │   ├── 04-conditional.md
│   │   │   ├── 05-por-vs-para.md
│   │   │   ├── 06-compound-tenses.md
│   │   │   └── 07-relative-clauses.md
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
│   ├── l1-interference.yaml         # Predicted English→Spanish transfer errors
│   ├── dialect-notes.yaml           # Vocabulary, grammar, pronunciation by dialect
│   ├── topic-bank.yaml              # Available weekly narrow topics with tags
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
│       └── grammar-in-context.md
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
└── resources/
    └── resource-catalog.yaml        # Structured catalog of all external tools
```

---

## Component Design

### 1. CLAUDE.md — Tutor Operating Instructions

The CLAUDE.md is kept concise (~150 lines) to minimize agent cognitive load. It contains only what every session needs:

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
| `fluency-activities.md` | Phase C+ and today includes a fluency activity |
| `sprint-mode.md` | `sprint.active` is true in schedule.yaml |
| `real-world-debrief.md` | Learner mentions a real-world Spanish encounter |
| `error-recovery.md` | State validation fails during startup |

This split means a standard session loads CLAUDE.md (~150 lines) + relevant state files. Only on special session types does the agent load additional protocol docs.

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

# Notes
notes: ""                    # anything else relevant
```

### 3. Skill Map (`state/skill-map.yaml`)

The core tracking document. Every grammar concept, vocabulary cluster, and skill dimension has a state entry.

```yaml
# Status values:
#   unseen     — not yet introduced
#   introduced — seen once, not yet practiced
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
  present-tense-regular:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0           # total times actively practiced
    error_rate_recent: null     # rolling average over last 5 sessions where tested
    error_trend: null           # improving, stable, declining
    performance_scaffolded: null    # null (untested), struggling, competent
    performance_unscaffolded: null  # null (untested), struggling, competent
    integration_tested: false       # tested in combination with other active concepts?
    prerequisites: []
    notes: ""

  # ... (one entry per grammar concept in curriculum/grammar/)

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

  # ... (one entry per vocabulary cluster in curriculum/vocabulary/)

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
    current_level: null           # superbeginner, beginner, intermediate, advanced, native
    comprehension_quality: null   # gist, main-ideas, detailed, near-native
    speed_tolerance: null         # slow, moderate, natural
    last_level_change: null
    notes: ""
  reading:
    current_level: null           # graded-A1, graded-A2, graded-B1, adapted, authentic-simple, authentic
    comprehension_quality: null   # gist, main-ideas, detailed, near-native
    lookup_frequency: null        # constant, frequent, occasional, rare
    last_level_change: null
    notes: ""

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
fluency:
  speaking_pace: ""             # slow-deliberate, moderate, natural-flow
  hesitation_frequency: ""      # frequent, occasional, rare
  self_correction_rate: ""      # high (good awareness), low (automatic or unaware)
  circumlocution: ""            # how often they talk around words they don't know
  willingness_to_risk: ""       # avoids unfamiliar structures vs tries and fails
  thinking_language: ""         # still translating from English, or starting to think in Spanish

overall_estimates:
  cefr_estimate: A0
  estimated_active_vocabulary: 0    # words the learner can produce
  estimated_passive_vocabulary: 0   # words the learner can recognize (always >= active)
  production_gap: 0                 # passive - active; large gap = needs more output practice
  strongest_skill: null             # listening, reading, speaking, writing
  weakest_skill: null
  last_formal_assessment: null      # date of last placement test or equivalent
```

### 4. Schedule (`state/schedule.yaml`)

The tutor's current plan. Updated at the end of each session.

```yaml
current_phase: A-foundation    # matches curriculum directory
current_week: 1
onboarding_complete: false     # true after session 10 (decision engine activates)
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

# Fluency vs accuracy emphasis
fluency_accuracy_balance: accuracy-leaning  # accuracy-leaning, balanced, fluency-leaning

# Upcoming queue — what's next when current items are acquired
grammar_queue: []
vocabulary_queue: []

# Carryover — concepts from prior phase still in active practice
carryover_concepts: []

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
```

### 5. Session Logs (`state/sessions/YYYY-MM-DD.yaml`)

Written at the end of every session. The primary handoff mechanism between agents. Kept for 60 days, then compressed into weekly summaries.

```yaml
date: ""
session_number: 0
duration_minutes: 0
learner_energy: ""              # high, medium, low (self-reported or inferred)
session_type: ""                # standard, micro, weekly-review, phase-transition, return
session_status: complete        # complete, partial, aborted — partial if session was cut short

# Assignment review — how did yesterday's homework go?
assignment_review:
  - task: ""
    resource: ""
    completed: false
    learner_report: ""          # what they said about it
    tutor_assessment: ""        # what the tutor inferred
    verification_result: ""     # what the tutor observed when testing the claim
    skill_updates: []           # any changes to make to skill-map

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
    observations:
      - concept: ""
        context: ""           # scaffolded or unscaffolded
        attempts: 0           # only for scaffolded
        errors: 0             # only for scaffolded
        assessment: ""        # only for unscaffolded: struggling or competent
    highlights: ""              # things they did well
    l1_interference_noted: []   # specific English transfer errors observed
    fluency_observations: ""    # pace, hesitation, risk-taking notes
    notes: ""

# Assessment updates to apply to skill-map
skill_map_updates:
  - concept: ""
    field: ""                   # status, error_rate_recent, error_trend, etc.
    old_value: ""
    new_value: ""
    evidence: ""                # why this change

# Assignments for before next session
assignments:
  - type: ""                    # pronunciation, listening, reading, vocabulary, speaking, writing, fluency
    resource: ""                # which external tool
    task: ""                    # specific instructions
    target_skill: ""            # which skill-map entry this supports
    estimated_minutes: 0
    priority: ""                # required, recommended, bonus
    narrow_topic_aligned: false # true if this assignment is part of the weekly topic block
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

# Next session recommendation
next_session:
  recommended_focus: ""
  reason: ""
  avoid: ""                     # what NOT to do tomorrow and why
  session_type: ""              # normal, consolidation, light-review, push-forward, fun-day
  estimated_duration: 0
  l1_interference_to_preempt: [] # predicted transfer errors to address proactively
```

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

### 7. Phase Milestones (`state/milestones/phase-X-completion.yaml`)

Permanent records of major transitions. Useful for long-term progress review.

```yaml
phase: ""                       # e.g., A-foundation
started: ""
completed: ""
total_sessions: 0
total_days: 0

# Snapshot of learner state at completion
cefr_estimate_at_completion: ""
active_vocabulary_at_completion: 0
grammar_concepts_acquired: []
notable_achievements: []

# Transition assessment results
transition_assessment:
  task_given: ""                # e.g., "Tell a story about a trip using past tenses"
  performance_summary: ""
  gaps_identified: []
  decision: ""                  # advanced, extended

# Learner reflection (if provided)
learner_reflection: ""
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
    preempt_at: A-06-present-irregular-common
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

During the first 10 sessions, the decision engine is **not active**. Instead, the tutor follows a fixed onboarding sequence defined in `curriculum/onboarding/`. This period:

- Establishes the learner profile through observation
- Introduces core Phase A concepts in a tested order
- Collects baseline performance data (error rates, learning speed, energy patterns)
- Sets up external tools (Anki, Speechling, etc.)
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

  VARIETY (0-5 penalty)
    Has the learner done this activity TYPE too many times recently?
    3 consecutive grammar-heavy days → penalize grammar, boost listening/speaking.

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

  PRIORITY = NEED + GAP + DECAY - VARIETY_PENALTY
  (filtered by READINESS, modified by ENERGY, MOTIVATION, FLUENCY_BALANCE)
```

The top 1-2 concepts become the session focus. The tutor doesn't mechanically expose this scoring — it presents the session naturally.

### Advancement Rules

**When to advance to a new concept:**
- Current primary concept is at "acquired" status (error rate < 10% in both drills and free production)
- The learner has demonstrated the concept in at least 3 separate sessions
- No regression in prerequisite concepts

**When to consolidate instead of advancing:**
- Error rate trend is "declining" on any active concept
- The learner self-reports feeling overwhelmed
- More than 2 concepts are currently in "practicing" status simultaneously
- Context gap detected (correct in drills, errors in free speech)

**When to flag a regression:**
- A concept previously at "acquired" or "automatic" shows error rate > 15% in a session
- Status changes to "regressed" and it re-enters active practice

**When to phase transition (A → B → C → D):**
- All concepts in the current phase are at "acquired" or "automatic"
- The learner passes a phase-transition assessment (a longer, integrated exercise that tests all phase concepts together)
- The tutor explicitly marks the phase transition in the schedule, session log, and creates a milestone record

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
└── If fluency day (Phase C+):
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
└── Quick state update
```

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

---

## State Validation Protocol

At startup, after reading state files but before greeting the learner, the tutor runs validation checks to catch corruption or inconsistencies from prior sessions.

```
Validation checks:
1. Can all YAML files be parsed? (If not → load error-recovery.md)
2. Does skill-map have entries for all concepts in the current phase?
3. Are there status/error_rate contradictions?
   (e.g., status: "acquired" but error_rate_recent: 0.40 → flag and investigate)
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
│   Attempt to recover from git history: "git log --oneline state/"
│   If recoverable, roll back the specific file
│   If not, inform learner and rebuild state from recent session logs
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
| Correct in drill, wrong in conversation | Context gap — knows the rule but can't apply under cognitive load | `context_gap: true` in skill-map |
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
Core sentence construction. The learner can form basic sentences about present situations.

| # | Concept | Prerequisites | Key Challenge | L1 Interference |
|---|---------|--------------|---------------|-----------------|
| 0 | Communication repair phrases | None | Memorization, overcoming embarrassment | — |
| 1 | Present tense (regular -ar, -er, -ir) | None | Memorizing conjugation patterns | Subject pronoun overuse |
| 2 | Ser vs Estar | Present tense | Conceptual — English has one "to be" | Ser/estar confusion |
| 3 | Gender and number agreement | None | No English equivalent, must build habit | Adjective placement |
| 4 | Articles, prepositions, contractions (al, del) | Gender | Memorization + gender dependency | Preposition mapping |
| 5 | Question formation | Present tense | Inversion, question words | Double negative avoidance |
| 6 | Common irregular present (ir, tener, querer, poder, hacer, decir, saber, conocer) | Present tense | High-frequency, must memorize individually | Gustar construction |

**Phase B — Conversational** (target: A2-B1)
The learner can talk about the past and future, handle daily interactions.

| # | Concept | Prerequisites | Key Challenge | L1 Interference |
|---|---------|--------------|---------------|-----------------|
| 1 | Preterite (regular) | Present tense | New conjugation set | — |
| 2 | Preterite (irregular) | Preterite regular | Memorization-heavy | — |
| 3 | Imperfect | Present tense | New tense concept | — |
| 4 | Preterite vs Imperfect | Both above | The hardest A2-B1 concept | English doesn't distinguish aspect |
| 5 | Reflexive verbs | Present, preterite | Pronoun placement | — |
| 6 | Direct object pronouns | Present tense | Word order changes | — |
| 7 | Indirect object pronouns | Direct objects | Stacking pronouns (se lo dije) | — |
| 8 | Future with ir + a | Present tense | Easy win — builds confidence | — |

**Phase C — Intermediate** (target: B1-B2)
The learner can express opinions, hypotheticals, and complex ideas.

| # | Concept | Prerequisites | Key Challenge | L1 Interference |
|---|---------|--------------|---------------|-----------------|
| 1 | Present subjunctive (forms) | Present tense, irregulars | New paradigm | Subjunctive avoidance |
| 2 | Subjunctive triggers | Subjunctive forms | Knowing WHEN to use it | — |
| 3 | Formal future tense | Present tense | Easy forms, nuance vs ir + a | — |
| 4 | Conditional | Future tense | Same stems, different endings | — |
| 5 | Por vs Para | All basic prepositions | Notoriously difficult, many rules | — |
| 6 | Present perfect (he hablado) | Past participles | Relatively easy if preterite is solid | — |
| 7 | Relative clauses (que, quien, donde, lo que) | All above | Sentence complexity jumps | — |

**Phase D — Advanced** (target: B2-C1)
The learner can handle nuanced expression, formal contexts, and complex narration.

| # | Concept | Prerequisites | Key Challenge |
|---|---------|--------------|---------------|
| 1 | Past subjunctive (imperfect subjunctive) | Present subjunctive, imperfect | Two forms (-ra, -se) |
| 2 | Si clauses (if...then) | Conditional, past subjunctive | Three types with different tense combos |
| 3 | Subjunctive across all tenses | All subjunctive + all tenses | Integration challenge |
| 4 | Passive voice and se constructions | All above | Multiple uses of "se" |
| 5 | Register shifting (tú/usted/vos, formal/informal) | All above | Social/cultural knowledge |
| 6 | Nuanced connectors (sin embargo, no obstante, a pesar de que) | All above | Elevates speech from functional to fluent |

### Grammar Concept File Format

Each grammar concept markdown file contains:

```markdown
# Concept Name

## Overview
Brief explanation of what this concept is and why it matters.

## Pattern
The grammatical pattern with examples. Show, don't just tell.

## Examples in Context
5-10 example sentences showing the concept in natural use.
Bolded target structures.

## Common Errors
Typical mistakes learners make with this concept.
Include L1 interference patterns from l1-interference.yaml.

## Drill Templates
2-3 exercise formats the tutor can use:
- Fill-in-the-blank
- Translation prompts
- Conversation starters that elicit this structure

## Cultural Notes
Any cultural or pragmatic context (e.g., conditional for politeness).

## Prerequisites
What must be acquired before introducing this concept.

## Signs of Acquisition
What does it look like when the learner has truly acquired this?
(e.g., "Uses correct form in free speech without pausing to think")
```

### Vocabulary Progression

Vocabulary clusters are paired with grammar phases so that new words reinforce new structures.

| Phase | Vocabulary Tiers | Target Word Count |
|-------|-----------------|-------------------|
| A | Tier 1: Survival | 300-500 active words |
| B | Tier 2: Daily Life | 800-1,500 active words |
| C | Tier 3: Social | 2,000-3,000 active words |
| D | Tier 4: Abstract | 4,000-5,000+ active words |

Each vocabulary cluster file contains:
- 20-40 words/phrases grouped by subtopic
- Example sentences using current-phase grammar
- Common collocations (words that go together)
- False cognates and tricky translations
- Cultural and pragmatic notes where relevant
- Pronunciation notes for tricky words

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
| **State file corruption** | Agent can't parse YAML | Git versioning — roll back to last good commit. CLAUDE.md includes recovery instructions. |
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

## Privacy and Data

All state is stored locally in the repo. No data leaves the machine except:
- When Claude Code processes the session (standard Claude API usage)
- When the learner uses external tools (Anki, Speechling, etc. — governed by those tools' policies)

The learner owns all their data and can inspect, edit, or delete any state file at any time.
