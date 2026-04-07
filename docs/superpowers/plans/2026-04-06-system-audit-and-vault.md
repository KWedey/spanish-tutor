# System Audit Fixes & Obsidian Vault — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 20 system audit gaps and build an Obsidian vault as the learner's primary between-session interface.

**Architecture:** Two-phase approach. Phase 1 fixes the data model (schemas, guides, protocols) in the tutoring system. Phase 2 builds the Obsidian vault on the stable foundation. All schema changes are designed vault-aware (Dataview-queryable frontmatter, linkable IDs).

**Tech Stack:** YAML, Markdown, Python 3 (generation script), Obsidian (Dataview plugin, Mermaid diagrams)

**Spec:** `docs/superpowers/specs/2026-04-06-system-audit-and-obsidian-vault-design.md`

---

## Dependency Graph

```
Wave 1 (parallel): Tasks 1, 2, 3, 4 — foundation edits, no interdependencies
Wave 2 (parallel): Tasks 5, 6, 7, 8 — new guides, depend on Wave 1 schemas
Wave 3 (parallel): Tasks 9, 10, 11 — existing file updates, depend on Wave 1
Wave 4 (sequential): Task 12 — CLAUDE.md integration, depends on all above
Wave 5 (parallel): Tasks 13, 14 — vault structure + generation script
Wave 6 (sequential): Task 15 — run generation, verify, first-session update
```

---

## Wave 1: Foundation

### Task 1: Update system-design.md — All Schema Changes

This is the master reference document. 12 changes from the spec, applied top-to-bottom by line number.

**Files:**
- Modify: `docs/system-design.md`

- [ ] **Step 1: Update skill-map grammar schema (line ~278-291)**

Replace the example grammar entry to show the new error rate fields:

```yaml
grammar:
  present-tense-regular:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0           # total times actively practiced
    error_rate_drills: null     # rolling avg over last 5 drill instances
    error_rate_production: null # rolling avg over last 5 free production instances
    error_trend: null           # improving, stable, declining (based on production rate)
    performance_scaffolded: null    # null (untested), struggling, competent
    performance_unscaffolded: null  # null (untested), struggling, competent
    integration_tested: false       # tested in combination with other active concepts?
    prerequisites: []
    notes: ""
```

Add after the schema block (before `vocabulary:` section):

```markdown
**Error rate calculation rules:**
- Rates are rolling averages over the last 5 practice instances per context (drill or production)
- If `practice_count < 3`, rates remain `null` — use `performance_scaffolded` / `performance_unscaffolded` qualitative assessments instead
- `error_trend` is derived from `error_rate_production` trajectory over last 3 sessions

**Decision engine usage of error rates:**
| Drills | Production | Interpretation | Activity Route |
|--------|-----------|----------------|-------|
| High | High | Early learning | Stage 2 (controlled practice) |
| Low | High | Transfer gap | Stage 3-4 (communicative practice) |
| Low | Low | Near-acquired | Spot-check only |
| High | Low | Unusual — investigate | Review methodology |

**Updated advancement rule:** "Acquired" requires `error_rate_production < 0.10` AND `error_rate_drills < 0.10` AND `performance_unscaffolded = "competent"` AND demonstrated in 3+ separate sessions.
```

- [ ] **Step 2: Add vocabulary ID mapping (after vocabulary schema, line ~306)**

Add after the vocabulary schema section:

```markdown
**Vocabulary ID to file path mapping:**
| Key prefix | Directory |
|-----------|-----------|
| tier1-* | curriculum/vocabulary/tier1-survival/ |
| tier2-* | curriculum/vocabulary/tier2-daily-life/ |
| tier3-* | curriculum/vocabulary/tier3-social/ |
| tier4-* | curriculum/vocabulary/tier4-abstract/ |
```

- [ ] **Step 3: Update session log schema — add estimated_minutes and gap_days (line ~521-530)**

In the `assignments:` section, `estimated_minutes` already exists at line 527. Add `gap_days` field to the top-level session log schema (after `session_status`):

```yaml
session_status: complete        # complete, partial, aborted
gap_days: 0                     # days since last session (0 if consecutive)
```

- [ ] **Step 4: Replace phase milestone schema (line ~605-631)**

Replace the entire Section 7 (`### 7. Phase Milestones`) with the unified milestone schema:

```markdown
### 7. Milestones (`state/milestones/YYYY-MM-DD-milestone-id.yaml`)

Permanent records of significant learning events and phase transitions. Used for long-term progress review, motivation, and vault display.

```yaml
type: ""              # phase-transition | first-real-world | first-self-correction
                      # vocabulary-milestone | streak-milestone | fluency-milestone
                      # cultural-milestone | first-dream-in-spanish
date: "YYYY-MM-DD"
session_number: 0
title: ""             # human-readable: "First restaurant order in Spanish"
description: ""       # what happened, why it matters
evidence: ""          # observable behavior that triggered this

# Phase transitions only:
phase_transition:
  from_phase: ""
  to_phase: ""
  started: "YYYY-MM-DD"
  completed: "YYYY-MM-DD"
  total_sessions: 0
  total_days: 0
  assessment:
    production_task: ""
    receptive_task: ""
    performance_summary: ""
    gaps_identified: []
    decision: ""               # advance | extend | partial
  carryover_concepts: []
  learner_reflection: ""

# Snapshot at time of milestone (all types):
snapshot:
  cefr_estimate: ""
  active_vocabulary: 0
  grammar_acquired: 0
  total_sessions: 0
  days_since_start: 0
`` `
```

- [ ] **Step 5: Add homework time estimation table (after line ~955)**

Insert before the `---` separator that precedes `## The Session Flow`:

```markdown
**Homework time estimation reference:**

| Task Type | Estimated Minutes |
|-----------|------------------|
| Anki review (existing cards) | 10-20 (scales with deck size) |
| Anki new cards (≤10) | 5-10 |
| Dreaming Spanish (1 video) | 5-10 (Superbeginner/Beginner), 10-15 (Intermediate+) |
| Podcast episode | 15-25 (with re-listening) |
| Reading (graded reader) | 10-15 per session |
| Reading (article/news) | 15-20 |
| Journal entry | 10-15 (Phase B), 15-20 (Phase C+) |
| Speechling recordings (5 phrases) | 10-15 |
| Grammar worksheet / exercise | 10-15 |
| Conversation partner session | 30-60 (external, not counted against homework budget) |
| Self-narration (daily routine) | 5-10 |

**Budget calculation:**
- `available_minutes = learner_profile.typical_weekday_minutes - average_session_duration`
- If `available_minutes < 15`: assign Anki only
- If `available_minutes 15-30`: Anki + one task
- If `available_minutes 30-45`: Anki + two tasks
- If `available_minutes > 45`: Anki + two tasks + journal or stretch

**External learning load:** Conversation partner sessions and self-directed study count toward total learning load awareness but not the homework assignment budget. If learner has regular external sessions, reduce assigned homework proportionally.

Always log `estimated_minutes` per assignment in session log. Track actual vs. estimated via learner feedback to calibrate over time.
```

- [ ] **Step 6: Add correction mode table (after Homework Assignment Logic, before Session Flow)**

Insert as a new section:

```markdown
## Correction Mode by Activity Type

Correction approach follows the activity type, not a single global rule:

| Activity Stage | Correction Mode | Details |
|---------------|----------------|---------|
| Stage 1-2 (controlled practice) | Explicit, immediate | No limit. Correction is part of the drill. L1 interference protocol applies. |
| Stage 3 (guided production) | Recast, immediate | No hard limit. Correction is part of the scaffolding. |
| Stage 4 (free conversation) | Recast, batched | Max 3 corrections. Prefer recasting. Batch the rest for end-of-segment review. |
| Fluency activities | Zero in-the-moment | Batch everything for post-activity review. Never interrupt timed activities. |
```

- [ ] **Step 7: Update decision engine section (line ~821+)**

Add to the scoring formula description, after DECAY:

```markdown
  TOPIC_BOOST (0-3)
    Does the concept align with this week's narrow topic?
    Direct match = 3, Adjacent = 1, No connection = 0

  VARIETY_PENALTY (0-5)
    Same activity type 3 days in a row → penalize that type by 5.
```

Update the formula line to: `PRIORITY = NEED + GAP + DECAY + TOPIC_BOOST - VARIETY_PENALTY`

Add to the modifiers section:

```markdown
  **Parking lot items:** If a parking lot item aligns with a candidate concept, boost by +3. If the item suggests a concept not in the candidate list but prerequisites are met, it can override secondary concept selection.

  **Sprint override:** If `sprint.active` is true, only score concepts in `sprint.focus_areas`.

  **Maintenance decay by phase distance:** Current phase maintenance NEED = 2, previous phase = 1, two+ phases back = 0.5.
```

- [ ] **Step 8: Add narrow topic selection algorithm (after decision engine section)**

Insert as a new subsection:

```markdown
### Weekly Topic Selection (during weekly review)

Score each candidate from `curriculum/topic-bank.yaml`:

| Factor | Range | Description |
|--------|-------|-------------|
| GRAMMAR_FIT | 0-5 | Does the topic naturally elicit the current primary grammar concept? |
| VOCABULARY_FIT | 0-5 | Does the topic align with the active or upcoming vocabulary cluster? |
| LEARNER_INTEREST | 0-3 | Does the topic connect to known interests, goals, or real-world situations? |
| FRESHNESS | 0-3 | How recently was this topic used? (3=never, 2=4+ weeks, 1=2-3 weeks, 0=last week — exclude) |

`TOPIC_SCORE = GRAMMAR_FIT + VOCABULARY_FIT + LEARNER_INTEREST + FRESHNESS`

Select highest-scoring topic. Tie-break: prefer higher LEARNER_INTEREST. Sprint override: if `sprint.active` is true, topic = sprint scenario theme.
```

- [ ] **Step 9: Add typed vs. oral fluency distinction (line ~1247)**

Add to the Fluency vs. Accuracy Balance section, after the activities list:

```markdown
**Typed vs. oral fluency:** The tutor operates via text. "Timed monologue" in Claude Code is timed writing — a valid fluency proxy. True oral fluency is delegated to external tools (Speechling, conversation partners). The tutor tracks:
- **Typed production fluency:** directly observed and measured
- **Oral fluency:** via external tool feedback and learner self-reports

Fluency metrics in skill-map should note data source (e.g., `"moderate (per italki partner feedback)"` vs. `"moderate (estimated from typed production)"`).
```

- [ ] **Step 10: Add writing track rubric (line ~1267)**

Add after the Writing Track table, before "Journal system:":

```markdown
**Writing evaluation rubric:**

*Sentence Construction:*
- Introduced: Can write simple SVO sentences with present tense
- Practicing: Attempts compound sentences, some agreement/word order errors
- Acquired: Consistently produces grammatically correct compound sentences with appropriate connectors

*Paragraph Coherence:*
- Introduced: Writes connected sentences on a single topic
- Practicing: Attempts topic sentences and transitions, inconsistent flow
- Acquired: Paragraphs have clear structure, logical flow, appropriate transitions

*Formal Register:*
- Introduced: Aware of tú/usted distinction in writing
- Practicing: Attempts formal constructions, inconsistent
- Acquired: Can write a formal email or request with appropriate register throughout

*Creative Expression:*
- Introduced: Writes beyond literal description (metaphor, humor, opinion)
- Practicing: Attempts creative devices, sometimes awkward
- Acquired: Voice is emerging — writing has personality, not just accuracy

Evaluation method: Journal entries are the primary data source. Compare entries from 4 weeks ago to current (read older entries during weekly reviews). Dimensions progress independently.
```

- [ ] **Step 11: Add vault generation reference (after Session Flow section)**

Add brief note:

```markdown
### Post-Session Vault Generation

After updating state files, the tutor generates/updates Obsidian vault content:
- Today's daily note in `vault/Daily/`
- Frontmatter status on changed Grammar/Vocabulary notes
- Roadmap.md if phase or concept status changed
- Weekly Reports during weekly review
- Milestone entries when milestones recorded

See spec Section "Phase 2: Obsidian Vault" for full vault architecture.
```

- [ ] **Step 12: Verify system-design.md parses and cross-references are valid**

Run: `python3 -c "import yaml; print('YAML blocks parse OK')"` (spot-check — the file is markdown with embedded YAML)

Verify the updated section headers still appear in logical order.

- [ ] **Step 13: Commit**

```bash
git add docs/system-design.md
git commit -m "docs: update system-design.md with all audit schema changes

- Replace error_rate_recent with drill/production split
- Unify milestone schema (absorbs phase-completion)
- Add homework time estimation table
- Add correction mode by activity type
- Update decision engine with topic boost, parking lot, maintenance decay
- Add narrow topic selection algorithm
- Add typed vs oral fluency distinction
- Add writing track rubric
- Add vocabulary ID mapping
- Add vault generation reference"
```

---

### Task 2: Update Communication Repair Kit

**Files:**
- Modify: `curriculum/grammar/A-foundation/00-communication-repair.md`

- [ ] **Step 1: Read current file**

Read `curriculum/grammar/A-foundation/00-communication-repair.md` to find the right insertion point.

- [ ] **Step 2: Add concrete repair phrase checklist and verification protocol**

Add as a new section (after existing content, or integrated into the Teaching Sequence section):

```markdown
## Repair & Flow Kit Checklist

These phrases must be automatic by session 5. The tutor verifies acquisition through deliberate comprehension gaps.

### Comprehension Repair
- ¿Qué significa ___?
- No entiendo. ¿Puede repetir?
- Más despacio, por favor.
- ¿Puede explicar de otra manera?

### Production Repair
- ¿Cómo se dice ___ en español?
- ¿Está bien si digo ___?

### Time-Buying Fillers
- Un momento, estoy pensando...
- A ver...
- Pues...
- Es que...
- O sea...

### Dialect Variants
- **Mexican:** ¿Mande? (polite "what?"), Órale (acknowledgment)
- **Castilian:** ¿Cómo? preferred over ¿Mande?
- **Argentine:** Dale (acknowledgment/agreement)

### Verification Protocol (Session 5+)

**Method:** Tutor deliberately uses an unfamiliar word or speaks at natural speed. Observe learner's response.

| Result | Classification | Action |
|--------|---------------|--------|
| Deploys repair phrase without hesitation | Automatic | Mark acquired |
| Pauses, then uses repair phrase | Emerging | Continue drilling |
| Switches to English or freezes | Not yet automatic | Targeted practice |

**Escalation:** If not automatic by session 7, dedicate a full practice segment. Assign self-monitoring homework: "Count how many times you used a repair phrase during Anki review."
```

- [ ] **Step 3: Verify file is well-formed**

Read the file back to confirm the addition is correctly placed and formatted.

- [ ] **Step 4: Commit**

```bash
git add curriculum/grammar/A-foundation/00-communication-repair.md
git commit -m "feat: add concrete repair phrase checklist and verification protocol"
```

---

### Task 3: Dialect Expansion + Infrastructure Cleanup

**Files:**
- Modify: `curriculum/dialect-notes.yaml`
- Create: `state/sessions/archive/.gitkeep`
- Delete: `docs/claude-md-draft.md`

- [ ] **Step 1: Read dialect-notes.yaml**

Read `curriculum/dialect-notes.yaml` to find the insertion point for new dialect sections.

- [ ] **Step 2: Add Caribbean and Central American dialect entries**

Add to the appropriate sections in dialect-notes.yaml:

```yaml
# Under vocabulary_differences, add entries:
  - word: bus
    neutral: autobús
    mexican: camión
    castilian: autobús
    argentinian: colectivo
    colombian: bus
    caribbean: guagua
    central_american: bus/camioneta
    context: "guagua is distinctly Caribbean; means 'baby' in Chile"

# Add new sections:
caribbean_features:
  pronunciation:
    - feature: final-s-aspiration
      description: "Final 's' aspirated or deleted (esta → ehta)"
      regions: [cuba, dominican-republic, puerto-rico]
      introduce_at: B
    - feature: liquid-neutralization
      description: "R/L interchange in syllable-final position"
      regions: [caribbean]
      introduce_at: C
    - feature: rapid-tempo
      description: "Generally faster speech tempo than other dialects"
      regions: [caribbean]
      introduce_at: B
  grammar:
    - feature: subject-pronoun-frequency
      description: "Subject pronouns used more frequently than in other dialects"
      regions: [caribbean]
      introduce_at: B
    - feature: inverted-questions
      description: "¿Qué tú quieres? instead of ¿Qué quieres tú?"
      regions: [caribbean]
      introduce_at: C
  vocabulary:
    - word: guagua
      meaning: bus
      regions: [caribbean]
    - word: china
      meaning: orange (Puerto Rico)
      regions: [puerto-rico]

central_american_features:
  pronunciation:
    - feature: conservative-s
      description: "Generally clear 's' pronunciation"
      regions: [central-america]
      introduce_at: B
    - feature: costa-rican-r
      description: "Strong, sometimes retroflex 'r'"
      regions: [costa-rica]
      introduce_at: C
  grammar:
    - feature: varied-voseo
      description: "Vos usage varies by country; standard in Costa Rica/Guatemala"
      regions: [costa-rica, guatemala]
      introduce_at: B
    - feature: ustedeo
      description: "Using usted for informal contexts"
      regions: [costa-rica, colombia]
      introduce_at: C
  vocabulary:
    - word: mae
      meaning: "dude (Costa Rica)"
      regions: [costa-rica]
    - word: cipote
      meaning: "kid (Honduras)"
      regions: [honduras]
    - word: cabal
      meaning: "exactly (Guatemala)"
      regions: [guatemala]
    - word: puchica
      meaning: "exclamation (general Central American)"
      regions: [central-america]
```

- [ ] **Step 3: Create archive directory**

```bash
mkdir -p state/sessions/archive && touch state/sessions/archive/.gitkeep
```

- [ ] **Step 4: Check claude-md-draft.md for unique content before deletion**

Read `docs/claude-md-draft.md` and compare with current `CLAUDE.md`. If any unique, valuable content exists that isn't in the current CLAUDE.md, note it for preservation. Then delete.

```bash
rm docs/claude-md-draft.md
```

- [ ] **Step 5: Commit**

```bash
git add curriculum/dialect-notes.yaml state/sessions/archive/.gitkeep
git rm docs/claude-md-draft.md
git commit -m "feat: expand dialect coverage, create archive dir, remove dead draft file

- Add Caribbean (Cuba, DR, PR) and Central American dialect entries
- Create state/sessions/archive/ for session log archival
- Remove obsolete docs/claude-md-draft.md"
```

---

### Task 4: Skill-Map Schema Migration

**Files:**
- Modify: `state/skill-map.yaml`

- [ ] **Step 1: Read skill-map.yaml grammar section**

Read `state/skill-map.yaml` lines 21-463 (all grammar concepts).

- [ ] **Step 2: Replace error_rate_recent with split rates across all 34 grammar concepts**

For every grammar concept, replace:
```yaml
    error_rate_recent: null
    error_trend: null
```
With:
```yaml
    error_rate_drills: null
    error_rate_production: null
    error_trend: null
```

Use replace-all for the `error_rate_recent: null` → `error_rate_drills: null\n    error_rate_production: null` substitution across the file.

- [ ] **Step 3: Verify YAML parses**

```bash
python3 -c "import yaml; yaml.safe_load(open('state/skill-map.yaml')); print('OK')"
```

- [ ] **Step 4: Verify all 34 grammar concepts have the new fields**

```bash
grep -c "error_rate_drills" state/skill-map.yaml
```

Expected: 34 (one per grammar concept)

```bash
grep -c "error_rate_production" state/skill-map.yaml
```

Expected: 34

- [ ] **Step 5: Verify no lingering error_rate_recent**

```bash
grep "error_rate_recent" state/skill-map.yaml
```

Expected: no output (all replaced)

- [ ] **Step 6: Commit**

```bash
git add state/skill-map.yaml
git commit -m "refactor: migrate skill-map error rates to drill/production split

Replace error_rate_recent with error_rate_drills and
error_rate_production across all 34 grammar concepts.
Rolling 5-session averages, min 3 samples before non-null."
```

---

## Wave 2: New Guides

### Task 5: Create Return Session Guide

**Files:**
- Create: `curriculum/tutor-guides/return-session.md`

- [ ] **Step 1: Write the guide**

Create `curriculum/tutor-guides/return-session.md` with the complete content from spec Section 2.1. Use the same format as existing guides (title, "Loaded when:" line, then sections).

```markdown
# Return Session Guide

Loaded when: Gap of 3+ days since last session.

## Goal

Welcome the learner back, assess what's been retained, and calibrate the session plan to their current state. No guilt. No testing framing.

## Real-World Encounter Override

If the learner mentions real-world Spanish use during the break, switch to `real-world-debrief.md` immediately. Run the return diagnostic in the next session instead. Real-world encounters are the highest-value teaching moments.

## Tiered Approach

### Short Break (3-7 days)

1. Welcome back warmly. Zero guilt.
2. Quick diagnostic: revisit the 2 most recently active concepts (from `schedule.yaml` `active_grammar.primary` and `active_grammar.secondary`) via casual conversation — not drills.
3. If performance matches pre-break levels → resume normal schedule.
4. If regression detected → mark concepts as regressed in skill-map, reduce to 1 active concept + the regressed one.
5. Homework: reduce by 50% for this session only. Resume normal load next session.

### Extended Break (8-21 days)

1. Welcome back, acknowledge the gap without judgment.
2. Diagnostic: revisit all "practicing" concepts and the most recently "acquired" concepts (up to 4 concepts total).
3. Expect 1-2 regressions — this is normal, tell the learner so.
4. Update skill-map with any status changes.
5. Homework: reduce by 50% for 2 sessions.
6. No new concepts this session — consolidation only.
7. Motivation check: "What brought you back?" — the answer informs your approach.

### Major Break (22+ days)

1. Welcome back as if it's a fresh start, but with history.
2. Run abbreviated phase transition assessment for current phase (see `phase-transition-guide.md`).
3. Regressions likely across multiple concepts — don't alarm the learner.
4. **Phase regression criteria:** if >50% of current phase prerequisite concepts show regression in the diagnostic, regress to previous phase. Otherwise stay in current phase with consolidation focus.
5. Homework: minimal for first 3 sessions (SRS review + one light task only).
6. Rebuild momentum before rebuilding knowledge.
7. If motivation is fragile → also load `emotional-intelligence.md`.
8. If gap > 60 days → also check `state/sessions/archive/` for the last pre-gap session.

## All Tiers — Common Protocol

- Read last 3 session logs to remember where things stood.
- Check `parking-lot.md` — learner may have added real-world encounters or questions during the break.
- Update `motivation.streak_days` to 0 (restart).
- Log `session_type: "return"` with `gap_days: N` in the session log.
- Do NOT reference the gap repeatedly throughout the session. Acknowledge once, move on.
```

- [ ] **Step 2: Verify the file exists and is well-formed**

Read the file back.

- [ ] **Step 3: Commit**

```bash
git add curriculum/tutor-guides/return-session.md
git commit -m "feat: add return session guide with tiered gap-length protocol"
```

---

### Task 6: Create Decision Engine Guide

**Files:**
- Create: `curriculum/tutor-guides/decision-engine.md`

- [ ] **Step 1: Write the guide**

Create `curriculum/tutor-guides/decision-engine.md` with the complete decision engine content from spec Section 2.3. This is the largest new guide — it contains the full scoring formula, modifiers, routing, topic selection, and quick-reference scenarios.

```markdown
# Decision Engine Guide

Loaded when: Standard session (post-onboarding). Used to select today's focus concepts and route to appropriate activities.

## Step 1 — Gather Candidates

All concepts in current phase with status: introduced, practicing, regressed, or acquired (for maintenance). Plus `carryover_concepts` from `schedule.yaml`. Plus maintenance from all previous phases (with decaying priority).

**Filter:** Exclude any concept where prerequisites are not met.

## Step 2 — Score Each Candidate

```
PRIORITY = NEED + GAP + DECAY + TOPIC_BOOST - VARIETY_PENALTY
```

### NEED (0-10)

| Concept type | Score |
|-------------|-------|
| Phase prerequisite (unlocks most concepts) | 10 |
| Current phase concept | 7 |
| Carryover concept from prior phase | 5 |
| Current phase maintenance | 2 |
| Previous phase maintenance | 1 |
| Two+ phases back maintenance | 0.5 |

### GAP (0-10) — uses `error_rate_production`

| State | Score |
|-------|-------|
| Regressed | 10 |
| Practicing, production error >30% | 8 |
| Practicing, drill/production mismatch (transfer gap) | 7 |
| Practicing, production error 15-30% | 5 |
| Practicing, production error <15% | 3 |
| Acquired, not integration-tested | 2 |
| Acquired + integration-tested | 0 |

### DECAY (0-10)

| Days since last practiced | Score |
|--------------------------|-------|
| 0-1 | 0 |
| 2-3 | 2 |
| 4-7 | 5 |
| 8-14 | 7 |
| 15+ | 9 |

### TOPIC_BOOST (0-3)

| Alignment with weekly narrow topic | Score |
|------------------------------------|-------|
| Direct match (topic naturally elicits this concept) | 3 |
| Adjacent (topic uses related vocabulary) | 1 |
| No connection | 0 |

### VARIETY_PENALTY (0-5)

Same activity type 3 days in a row → penalize that type by 5. Prefer alternation.

## Step 3 — Apply Modifiers

- **Low energy:** Boost passive activities (listening/reading review), reduce production demands. Halve GAP score for challenging concepts.
- **Low motivation / at-risk:** Boost easy wins (high-confidence concepts), add novelty. Double NEED for fun/interesting concepts.
- **Parking lot items:** If a parking lot item aligns with a candidate concept, boost that concept by +3. If the item suggests a concept not in the candidate list but prerequisites are met, it can override secondary concept selection.
- **Sprint override:** If `sprint.active` is true, only score concepts in `sprint.focus_areas`. All others excluded.

## Step 4 — Select Top 1-2 Concepts

Highest score = primary focus. Second highest = secondary (if time allows and not same category). If top concept is grammar, prefer vocabulary or pronunciation as secondary (variety). Tie-break: prefer higher learner interest.

## Step 5 — Route to Activity

**Fluency days** (1x/week in Phase B, 2x/week in Phase C, every session in Phase D): Run Steps 1-4 normally to select concept(s). At Step 5, route to `fluency-activities.md` instead of the stage-based routing below.

**Non-fluency days** — check `error_rate_drills` and `error_rate_production`:

| Drills | Production | Route |
|--------|-----------|-------|
| Both high | → | Stage 2 (controlled practice from concept file) |
| Drills low, production high | → | Stage 3-4 (communicative practice) |
| Both low | → | Spot-check via conversation, move to secondary |
| Integration untested | → | Combined exercise with another acquired concept |

**New concept introduction:** Only if ≤2 concepts in "practicing" status (≤3 with carryover). Route to Stage 1 (noticing) from concept file.

## Step 6 — Weekly Topic Selection (during weekly review)

Score each candidate from `curriculum/topic-bank.yaml`:

| Factor | Range | Description |
|--------|-------|-------------|
| GRAMMAR_FIT | 0-5 | Does the topic naturally elicit the primary grammar concept? |
| VOCABULARY_FIT | 0-5 | Aligned with active or upcoming vocabulary cluster? |
| LEARNER_INTEREST | 0-3 | Connects to known interests, goals, real-world situations? |
| FRESHNESS | 0-3 | 3=never used, 2=4+ weeks ago, 1=2-3 weeks, 0=last week (exclude) |

`TOPIC_SCORE = GRAMMAR_FIT + VOCABULARY_FIT + LEARNER_INTEREST + FRESHNESS`

Highest score wins. Tie-break: prefer higher LEARNER_INTEREST.

Sprint override: if `sprint.active` is true, topic = sprint scenario theme. Skip scoring.

## Quick Reference — Common Scenarios

- **"Stuck on ser/estar for 4 sessions"**: GAP=8, DECAY=0, NEED=10 → score 18. Top priority. Route: try a different Stage 2 approach.
- **"Preterite not practiced in 10 days, was acquired"**: GAP=0, DECAY=7, NEED=1 → score 8. Maintenance. Spot-check in conversation.
- **"New concept ready to introduce"**: NEED=10, GAP=10, DECAY=0 → score 20. Highest. Route: Stage 1 (noticing).
- **"Post-return regression on gender agreement"**: GAP=10, DECAY=9, NEED=7 → score 26. Urgent. Dedicated recovery.
- **"Parking lot: learner asked about conditional"**: If C-04 prerequisites met, boost by +3 and consider as primary.
```

- [ ] **Step 2: Verify the file**

Read back and verify all sections are present.

- [ ] **Step 3: Commit**

```bash
git add curriculum/tutor-guides/decision-engine.md
git commit -m "feat: add decision engine guide — extracted scoring logic for standard sessions"
```

---

### Task 7: Create Phase Transition Guide + Session Log Example

**Files:**
- Create: `curriculum/tutor-guides/phase-transition-guide.md`
- Create: `docs/session-log-example.yaml`

- [ ] **Step 1: Write phase transition guide**

Create `curriculum/tutor-guides/phase-transition-guide.md`:

```markdown
# Phase Transition Assessment Guide

Loaded when: All prerequisites for the next phase show "acquired" for 2+ consecutive sessions.

## Framing — Critical

- **Never** say "I'm going to assess you" or "this is a test."
- Frame as natural conversation: "Let's talk about your week."
- If learner shows anxiety, back off and retry next session embedded in normal conversation.
- If learner clearly fails, don't label it — note gaps, continue in current phase, retry in 2 weeks.

## A → B Assessment (15-20 min)

**Production (10 min):** "Tell me about your typical week — what you do, where you go, what you like and don't like."
- Tests: present regular + irregular, ser/estar, gender agreement, gustar-type, questions

**Receptive (5 min):** Play 60-sec Dreaming Spanish clip at Beginner level. Ask: "¿De qué habló?"
- Tests: listening comprehension + production

**Repair check:** Tutor deliberately uses one unfamiliar word mid-conversation.
- Tests: automatic repair phrase deployment

**Pass criteria:**
- A-01, A-02, A-04 at <10% production error
- Repair phrases automatic
- Can sustain 3+ minutes of guided conversation

**Borderline:** Extend 1-2 weeks, focus on weakest prerequisite.

## B → C Assessment (20-25 min)

**Production (12 min):** "Tell me about something that happened last week, and what you're planning for this weekend."
- Tests: preterite/imperfect contrast, future (ir+a), object pronouns, reflexives

**Receptive (8 min):** Listen to 2-min podcast excerpt at natural speed. Answer comprehension questions in Spanish.

**Pass criteria:**
- B-01, B-04 at <10% production error
- Appropriate past tense selection >80% of the time
- Can narrate event sequence without reverting to present tense

**Borderline:** Extend 2-3 weeks. If only one prerequisite weak, focused sprint.

## C → D Assessment (25-30 min)

**Production (15 min):** "What would change about your city if you were mayor? I disagree with your first point — convince me."
- Tests: subjunctive triggers, conditional, por/para, compound tenses, opinion defense

**Receptive (10 min):** Read short opinion article (~300 words). Summarize argument and state agreement/disagreement in Spanish.

**Pass criteria:**
- C-01, C-04, C-06 at <10% production error
- Uses subjunctive unprompted in at least 2 contexts
- Can sustain an argument with connectors

**Borderline:** Extend 2-4 weeks. Subjunctive is the usual blocker — if that's the gap, dedicated subjunctive sprint.

## Recording Results

Record the assessment outcome in a milestone file (`state/milestones/YYYY-MM-DD-phase-transition.yaml`) using the unified milestone schema with `type: phase-transition`. Include `phase_transition.assessment.production_task`, `receptive_task`, and `decision`.
```

- [ ] **Step 2: Write session log example**

Create `docs/session-log-example.yaml` — a realistic, fully-populated example:

```yaml
# Example Session Log — shows all fields with realistic values
# Use as a reference when writing session logs

date: "2026-04-15"
session_number: 14
duration_minutes: 35
learner_energy: medium
session_type: standard
session_status: complete
gap_days: 1

assignment_review:
  - task: "Review Anki deck — focus on food vocabulary"
    resource: Anki
    completed: true
    learner_report: "Got through all cards, struggled with 'cuchara' vs 'cucharón'"
    tutor_assessment: "Production of kitchen utensils still weak"
    verification_result: "Asked about restaurant ordering — used 'tenedor' correctly unprompted"
    skill_updates:
      - concept: tier1-food-restaurant
        field: weak_production
        note: "Add cuchara, cucharón to weak list"
  - task: "Watch Dreaming Spanish: 'En el mercado' (8 min)"
    resource: Dreaming Spanish
    completed: true
    learner_report: "Understood most of it, missed some fast parts"
    tutor_assessment: "Comprehension at Beginner level solid"
    verification_result: "Asked '¿De qué trataba el video?' — produced 3 accurate summary sentences"
    skill_updates: []

session_activities:
  - type: grammar-drill
    target_concepts: [A-02-ser-vs-estar]
    duration_minutes: 10
    performance: mixed
    errors_noted:
      - error: "Estoy un estudiante"
        correction: "Soy estudiante"
        category: grammar
        concept: A-02-ser-vs-estar
        error_type: l1-interference
      - error: "Es caliente hoy"
        correction: "Está caliente hoy / Hace calor hoy"
        category: grammar
        concept: A-02-ser-vs-estar
        error_type: l1-interference
    observations: "Consistent ser/estar confusion with temporary states"
    highlights: "Self-corrected 'estoy alto' to 'soy alto' unprompted"
    l1_interference_noted: true
    fluency_observations: ""
    notes: "Stage 2 controlled practice — needs more contrastive drilling"
  - type: conversation
    target_concepts: [A-02-ser-vs-estar, tier1-food-restaurant]
    duration_minutes: 12
    performance: good
    errors_noted:
      - error: "La comida es buena" (when talking about today's lunch)
        correction: "La comida está buena (temporary quality judgment)"
        category: grammar
        concept: A-02-ser-vs-estar
        error_type: developmental
    observations: "Conversation about restaurants flowed well, used food vocab from homework"
    highlights: "Produced 'Me gusta el restaurante porque la comida está rica' — correct estar usage!"
    l1_interference_noted: false
    fluency_observations: "Moderate pace, 3-4 second pauses for verb conjugation, willing to attempt complex sentences"
    notes: ""

skill_map_updates:
  - concept: A-02-ser-vs-estar
    field: error_rate_drills
    old_value: 0.30
    new_value: 0.25
    evidence: "3/12 errors in controlled practice (improving from 4/12 last session)"
  - concept: A-02-ser-vs-estar
    field: error_rate_production
    old_value: 0.35
    new_value: 0.28
    evidence: "1 error in ~12 min conversation (context-dependent: temporary states still weak)"
  - concept: A-02-ser-vs-estar
    field: error_trend
    old_value: stable
    new_value: improving
    evidence: "Both drill and production rates declining over last 3 sessions"

assignments:
  - type: vocabulary
    resource: Anki
    task: "Review existing deck + add 5 new cards from today's restaurant conversation (tenedor, cuchillo, cuchara, cuenta, propina)"
    target_skill: tier1-food-restaurant
    estimated_minutes: 15
    priority: required
    narrow_topic_aligned: true
    notes: "Focus on production — say each word aloud before flipping"
  - type: listening
    resource: Dreaming Spanish
    task: "Watch 'Mi familia' (Beginner, 7 min) — notice ser vs estar usage"
    target_skill: A-02-ser-vs-estar
    estimated_minutes: 10
    priority: recommended
    narrow_topic_aligned: false
    notes: "Pay attention to how they describe people (ser) vs how they feel (estar)"
  - type: writing
    resource: journal
    task: "Write 5 sentences describing your favorite restaurant — use both ser and estar"
    target_skill: A-02-ser-vs-estar
    estimated_minutes: 10
    priority: recommended
    narrow_topic_aligned: true
    notes: "Prompt: ¿Cómo es tu restaurante favorito? ¿Cómo está la comida?"

journal_review:
  entry_date: "2026-04-14"
  errors_found:
    - error: "Yo como el almuerzo a las doce"
      correction: "Como el almuerzo a las doce (subject pronoun unnecessary)"
      concept: l1-interference-subject-pronoun
    - error: "La comida es muy delicioso"
      correction: "La comida es muy deliciosa (gender agreement)"
      concept: A-03-gender-agreement
  quality_notes: "Good sentence variety. Attempting compound sentences. Agreement errors persist but decreasing."

learner_observations:
  mood: motivated
  engagement: high
  emotional_state: confident
  self_assessment: "Feels like ser/estar is starting to click"
  calibration_note: "Slightly overestimates — still 25% production errors, but trend is positive"
  autonomy_readiness: "Not yet — still needs structured practice for ser/estar"

next_session:
  recommended_focus: A-02-ser-vs-estar
  reason: "Production error still at 28%, but improving. One more session of communicative practice before spot-checking."
  avoid: "Don't introduce new grammar — ser/estar needs consolidation"
  session_type: normal
  estimated_duration: 35
  l1_interference_to_preempt: [ser-estar-confusion]
```

- [ ] **Step 3: Verify YAML parses**

```bash
python3 -c "import yaml; yaml.safe_load(open('docs/session-log-example.yaml')); print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add curriculum/tutor-guides/phase-transition-guide.md docs/session-log-example.yaml
git commit -m "feat: add phase transition guide and session log example

- Phase transition assessments with production + receptive components
- Framing guidance to avoid test anxiety
- Complete session log example with realistic values"
```

---

### Task 8: Create Progress Report Template

**Files:**
- Create: `docs/progress-report-template.md`

- [ ] **Step 1: Write the template**

Create `docs/progress-report-template.md`:

```markdown
# Progress Report Template

Reports are written to `progress-reports/YYYY-WNN.md` during weekly review. Written in encouraging, specific tone — the learner reads these in the Obsidian vault.

## Template

```markdown
# Week NN Progress — [Mon date] to [Sun date]

## This Week
- Sessions completed: X/Y
- Total practice time: Xh Ym (sessions + homework)
- Homework completion: X%
- Current streak: X days (longest: Y)

## Grammar
- New: [concepts introduced this week]
- Advancing: [concept: old status → new status, with evidence]
- Needs work: [concept + specific gap]

## Vocabulary
- New words introduced: X
- Active vocabulary estimate: X (+Y this week)
- Production gap: X words
- Weak production: [specific words needing output practice]

## Pronunciation
- Focus this week: [target]
- Progress: [observation]

## Writing (if journal active)
- Entries submitted: X
- Quality trend: [improving/stable/declining]
- Common errors: [patterns]

## Fluency Metrics (Phase C+ only)
- Speaking pace: [benchmark reference]
- Hesitation: [frequency]
- Risk-taking: [assessment]

## Highlights
- Best moment: [specific achievement with evidence]
- Breakthrough: [if any — be specific about what changed]

## Motivation
- Energy this week: [observation]
- Parking lot items addressed: [list]

## Next Week
- Primary focus: [concept]
- Weekly topic: [topic from topic-bank]
- Goal: [specific, measurable]
`` `

Conditional sections: omit "Writing" if journal is not active. Omit "Fluency Metrics" before Phase C. Omit "Pronunciation" if no pronunciation focus this week.
```

- [ ] **Step 2: Commit**

```bash
git add docs/progress-report-template.md
git commit -m "docs: add progress report template for weekly reviews"
```

---

## Wave 3: Existing Guide Updates

### Task 9: Update Onboarding Guide

**Files:**
- Modify: `curriculum/tutor-guides/onboarding-guide.md`

- [ ] **Step 1: Read current file**

Read `curriculum/tutor-guides/onboarding-guide.md` (35 lines).

- [ ] **Step 2: Add onboarding failure path**

Append the failure path protocol:

```markdown
## Struggling During Onboarding

### Signals
- Unable to reproduce previous session's concept after review
- Error rate >50% on controlled practice after full explanation
- Learner expresses frustration or confusion 2+ sessions in a row
- Homework consistently incomplete or reported as too difficult

### Step 1 — Check External Factors FIRST

Before assuming concept difficulty, check:
- Is homework getting done? If not, the fix is reducing load, not reteaching.
- Has available study time changed? Life events, schedule shifts?
- Is the learner overwhelmed by tools (Anki setup, multiple apps)?
- Ask: "How's your study time been this week?"
- If external factors are the cause → adjust homework load and tool expectations. Do NOT insert consolidation.

### Step 2 — If Concept Difficulty Confirmed

1. Never repeat the exact same session — reteach with a different approach (examples-first if rules-first failed, or vice versa).
2. Insert an unscheduled consolidation session before advancing.
3. Maximum 2 inserted consolidation sessions per concept — if still struggling, note as "slow acquisition" in skill-map and continue forward (concept resurfaces via decision engine post-onboarding).
4. Extend onboarding beyond session 10 if:
   - 3+ A-phase concepts are still "introduced" (not "practicing")
   - Learner hasn't demonstrated basic sentence construction
   - Communication repair phrases are not emerging
   - Maximum extension: 5 additional sessions (to session 15)
5. If extended onboarding exceeds session 15:
   - Complete onboarding regardless
   - Decision engine takes over with heavy consolidation weighting
   - Flag in system-health.yaml: `onboarding_extended: true`, `onboarding_sessions: N`
   - Reduce `max_new_concepts_per_week` to 1

### Emotional Considerations
- Never imply the learner is behind or slow
- Frame consolidation as "let's make sure this is solid before we build on it"
- Adjust energy: more games, less drilling

## Weekly Review During Onboarding

If the learner's `weekly_review_day` falls during onboarding, run a simplified review:

1. Progress check: "Here's what we've covered so far" — list concepts introduced and their status.
2. Homework review: completion rate, difficulty feedback.
3. Tool check: is Anki working? Any setup issues?
4. Quick wins: highlight 2-3 specific things they can do now that they couldn't before.
5. Motivation check: "How's it feeling so far?"

**Skip:** narrow topic selection, decision engine references, skill-map audit, system health review, resource rotation.

Write an abbreviated weekly summary noting it's an onboarding review. First full weekly review happens the first review day after `onboarding_complete = true`.
```

- [ ] **Step 3: Verify**

Read back to confirm additions are properly formatted.

- [ ] **Step 4: Commit**

```bash
git add curriculum/tutor-guides/onboarding-guide.md
git commit -m "feat: add onboarding failure path and simplified weekly review protocol"
```

---

### Task 10: Update Fluency Activities Guide

**Files:**
- Modify: `curriculum/tutor-guides/fluency-activities.md`

- [ ] **Step 1: Read current file**

Read `curriculum/tutor-guides/fluency-activities.md` (53 lines).

- [ ] **Step 2: Update loading condition and add phase-specific guidance**

Update the header/loading condition to reflect Phase B+ (was Phase C+). Add phase-specific sections and fluency benchmarks.

Add/update at appropriate locations:

```markdown
# Fluency Activities Guide

Loaded when: Phase B+ and today is a fluency day.

## Phase-Specific Guidance

### Phase B (1x/week)
- Timed monologue only (1 minute). Accuracy is still primary.
- Fluency work is exposure, not expectation. Don't track metrics yet.
- Goal: build comfort with sustained output.

### Phase C (2x/week)
- Full activity set unlocked (monologue, speed translation, shadowing, retelling).
- Begin tracking fluency metrics. Balanced correction.
- Only correct meaning-impeding errors and current focus-area errors.

### Phase D (every session)
- Every session includes a fluency component.
- Metrics are the primary assessment tool.
- Correct only meaning-impeding errors during fluency work.
- Batch everything else for post-activity review.
```

Add benchmarks section:

```markdown
## Fluency Benchmarks

### Oral Fluency (reference — tutor cannot measure directly)

| Metric | Phase C | Phase D |
|--------|---------|---------|
| Pace (WPM) | 60-80 developing, 80-100 on track | 100-120 developing, 120+ natural-flow |
| Hesitation (pauses >2s/min) | 6+ frequent, 3-5 occasional, 0-2 rare | 3+ frequent, 1-2 occasional, 0 rare |
| Native reference | 120-180 WPM (varies by dialect) | |

### Typed Production (tutor-measurable)

| Phase | Benchmark |
|-------|-----------|
| B | Can produce 3-4 simple sentences in 2 minutes |
| C | Can produce a coherent paragraph in 2 minutes |
| D | Can sustain multi-paragraph response with complex structures in 3 minutes |

### Self-Correction Rate
- High self-correction = good (shows monitoring). Track trend.
- Declining self-correction + stable accuracy = automaticity emerging.
- Declining self-correction + declining accuracy = losing awareness — flag.

**Important:** These are reference benchmarks, not pass/fail criteria. The tutor estimates from conversation — qualitative assessment backed by quantitative reference.

## Typed vs. Oral Fluency

The tutor operates via text. "Timed monologue" in Claude Code is timed writing — a valid fluency proxy. True oral fluency is delegated to external tools (Speechling, conversation partners).

Fluency metrics in skill-map should note data source: `"moderate (per italki feedback)"` vs. `"moderate (typed production estimate)"`.
```

- [ ] **Step 3: Verify**

Read back to confirm.

- [ ] **Step 4: Commit**

```bash
git add curriculum/tutor-guides/fluency-activities.md
git commit -m "feat: update fluency guide — Phase B+ loading, benchmarks, typed vs oral distinction"
```

---

### Task 11: Update Weekly Review Guide

**Files:**
- Modify: `curriculum/tutor-guides/weekly-review-guide.md`

- [ ] **Step 1: Read current file**

Read `curriculum/tutor-guides/weekly-review-guide.md` (58 lines).

- [ ] **Step 2: Add archive instruction**

Add to the maintenance section (or create one if it doesn't exist):

```markdown
## Session Archive

During weekly review, archive session logs older than 60 days:
- Move files from `state/sessions/` to `state/sessions/archive/`
- Archive = move, don't delete. Archived sessions are accessible but not loaded at startup.
- The 60-day window provides buffer for monthly reviews and regression analysis.
```

- [ ] **Step 3: Commit**

```bash
git add curriculum/tutor-guides/weekly-review-guide.md
git commit -m "feat: add session archive protocol to weekly review guide"
```

---

## Wave 4: CLAUDE.md Integration

### Task 12: Update CLAUDE.md — All 13 Changes

**Files:**
- Modify: `CLAUDE.md`

This task applies all 13 changes from the spec's "CLAUDE.md Changes Required" section. Read the file first, then apply changes in order.

- [ ] **Step 1: Read CLAUDE.md**

Read `CLAUDE.md` (147 lines) completely.

- [ ] **Step 2: Add vault existence check to startup protocol (Step 1)**

In the Session Startup Protocol, after "Step 1 — Read core state:", add at the end of the read list:

```markdown
10. If `vault/` directory does not exist, note this — vault setup will be part of first session
```

- [ ] **Step 3: Update Step 3 routing table**

Add return session guide loading and fluency day condition:

| Condition | Session Type | Load |
|-----------|-------------|------|
| Gap of 3+ days since last session | Return | `curriculum/tutor-guides/return-session.md` |
| Phase B+ and today is a fluency day | Fluency | `curriculum/tutor-guides/fluency-activities.md` |

(The return row replaces the current inline return protocol. The fluency row is new.)

- [ ] **Step 4: Update Step 4 conditional loads**

Change the fluency condition from "Phase C+" to "Phase B+ and today is a fluency day."

Add new conditional loads:

```markdown
- Standard session (post-onboarding)? Also read `curriculum/tutor-guides/decision-engine.md`
- All prerequisites for next phase show "acquired" for 2+ consecutive sessions? Also read `curriculum/tutor-guides/phase-transition-guide.md`
```

- [ ] **Step 5: Add Correction Mode by Activity table**

Add as a new section after Error Correction:

```markdown
## Correction Mode by Activity Type

| Activity Stage | Mode | Details |
|---------------|------|---------|
| Stage 1-2 (controlled practice) | Explicit, immediate | No limit. L1 interference protocol applies. |
| Stage 3 (guided production) | Recast, immediate | No hard limit. Correction is scaffolding. |
| Stage 4 (free conversation) | Recast, batched | Max 3. Batch rest for end-of-segment. |
| Fluency activities | Zero in-the-moment | Batch everything for post-activity review. |
```

- [ ] **Step 6: Update State Updates section**

Add vault generation steps after the existing state update steps:

```markdown
8. Generate/update vault content:
   a. Generate/update today's daily note in `vault/Daily/`
   b. Update frontmatter status on any Grammar/Vocabulary vault notes that changed
   c. Update `vault/Roadmap.md` if phase or concept status changed
   d. During weekly review: append to `vault/Progress/Weekly Reports.md`
   e. On milestone: update `vault/Progress/Milestones.md`
9. Include `vault/` files in session commit
10. During weekly review, archive session logs older than 60 days to `state/sessions/archive/`
```

- [ ] **Step 7: Add vault guardrails**

Add to Guardrails section:

```markdown
- **Never overwrite vault files without `generated: true` frontmatter flag.**
- **On fluency days, still run decision engine for concept selection** — skip activity routing only, not concept selection.
```

- [ ] **Step 8: Update first session reference**

In the Step 3 routing table, ensure the first session row notes vault setup:

```markdown
| No session logs exist | First Session | `curriculum/tutor-guides/first-session.md` (includes vault setup) |
```

- [ ] **Step 9: Remove inline return protocol**

The "Return Protocol (Gap of 3+ Days)" section in CLAUDE.md should be replaced with a brief reference:

```markdown
## Return Protocol

See `curriculum/tutor-guides/return-session.md` — loaded automatically when a gap of 3+ days is detected.
```

- [ ] **Step 10: Verify CLAUDE.md is coherent**

Read the entire file back. Check that:
- Routing table has no duplicate conditions
- Conditional loads don't conflict
- State update steps are numbered correctly
- Guardrails section has no contradictions

- [ ] **Step 11: Commit**

```bash
git add CLAUDE.md
git commit -m "feat: integrate all audit fixes into CLAUDE.md

- Add vault existence check to startup
- Update routing table with return guide and fluency day
- Add decision engine and phase transition conditional loads
- Add correction mode by activity table
- Add vault generation to state updates
- Add vault guardrails
- Replace inline return protocol with guide reference"
```

---

## Wave 5: Vault Foundation

### Task 13: Create Vault Directory Structure + Obsidian Config

**Files:**
- Create: `vault/` directory tree
- Create: `.obsidian/app.json`
- Create: `.obsidian/graph.json`

- [ ] **Step 1: Create vault directory structure**

```bash
mkdir -p vault/Daily/Archive vault/Grammar/"Phase A - Foundation" vault/Grammar/"Phase B - Conversational" vault/Grammar/"Phase C - Intermediate" vault/Grammar/"Phase D - Advanced" vault/Vocabulary/"Tier 1 - Survival" vault/Vocabulary/"Tier 2 - Daily Life" vault/Vocabulary/"Tier 3 - Social" vault/Vocabulary/"Tier 4 - Abstract" vault/Pronunciation vault/Progress vault/Templates
```

- [ ] **Step 2: Create .obsidian config**

Create `.obsidian/app.json`:

```json
{
  "userIgnoreFilters": [
    "state/",
    "curriculum/",
    "docs/",
    ".git/",
    ".superpowers/",
    ".planning/",
    "resources/",
    "progress-reports/",
    "scripts/"
  ],
  "newFileLocation": "folder",
  "newFileFolderPath": "vault",
  "attachmentFolderPath": "vault"
}
```

Create `.obsidian/graph.json`:

```json
{
  "colorGroups": [
    { "query": "tag:#unseen", "color": { "a": 1, "rgb": 8421504 } },
    { "query": "tag:#introduced", "color": { "a": 1, "rgb": 4444159 } },
    { "query": "tag:#practicing", "color": { "a": 1, "rgb": 16761600 } },
    { "query": "tag:#acquired", "color": { "a": 1, "rgb": 3394611 } },
    { "query": "tag:#automatic", "color": { "a": 1, "rgb": 65280 } },
    { "query": "tag:#regressed", "color": { "a": 1, "rgb": 16711680 } }
  ],
  "search": "-tag:#daily",
  "showTags": false,
  "showAttachments": false,
  "showOrphans": false
}
```

- [ ] **Step 3: Update .gitignore**

Add `.obsidian/workspace.json` and `.obsidian/workspace-mobile.json` to `.gitignore` (these are user-local state and shouldn't be committed):

```
.superpowers/
.obsidian/workspace.json
.obsidian/workspace-mobile.json
```

- [ ] **Step 4: Commit**

```bash
git add vault/ .obsidian/ .gitignore
git commit -m "feat: create vault directory structure and Obsidian config

- Vault directories for Grammar, Vocabulary, Pronunciation, Progress, Daily
- .obsidian config with excluded folders and graph color groups
- Graph colors: gray=unseen, blue=introduced, amber=practicing, green=acquired, red=regressed"
```

---

### Task 14: Create Vault Generation Script

**Files:**
- Create: `scripts/generate-vault.py`

- [ ] **Step 1: Write the generation script**

Create `scripts/generate-vault.py`:

```python
#!/usr/bin/env python3
"""
Vault generation script for Spanish Fluency Tutor.

Two modes:
  --full    Generate everything (init, curriculum changes)
  --session Generate per-session updates (daily note, frontmatter refresh)

Usage:
  python scripts/generate-vault.py --full
  python scripts/generate-vault.py --session --date 2026-04-15
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "vault"
STATE = ROOT / "state"
CURRICULUM = ROOT / "curriculum"

TIER_MAP = {
    "tier1": "Tier 1 - Survival",
    "tier2": "Tier 2 - Daily Life",
    "tier3": "Tier 3 - Social",
    "tier4": "Tier 4 - Abstract",
}

PHASE_MAP = {
    "A": "Phase A - Foundation",
    "B": "Phase B - Conversational",
    "C": "Phase C - Intermediate",
    "D": "Phase D - Advanced",
}

PHASE_DIR_MAP = {
    "A": "A-foundation",
    "B": "B-conversational",
    "C": "C-intermediate",
    "D": "D-advanced",
}

GENERATED_NOTICE = "%%Auto-generated from tutor state. Edits will be overwritten.%%"


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def write_vault_file(path, frontmatter, body):
    """Write a vault file with YAML frontmatter and body content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write("---\n")
        yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True)
        f.write("---\n")
        f.write(f"{GENERATED_NOTICE}\n\n")
        f.write(body)


def concept_id_to_title(concept_id):
    """Convert A-01-present-regular to Present Regular."""
    parts = concept_id.split("-", 2)
    if len(parts) >= 3:
        return parts[2].replace("-", " ").title()
    return concept_id.replace("-", " ").title()


def concept_id_to_phase(concept_id):
    """Extract phase letter from concept ID."""
    return concept_id[0].upper()


def generate_grammar_notes(skill_map):
    """Generate vault/Grammar/ notes from curriculum and skill-map."""
    grammar = skill_map.get("grammar", {})
    for concept_id, data in grammar.items():
        phase = concept_id_to_phase(concept_id)
        title = concept_id_to_title(concept_id)
        phase_dir = PHASE_MAP.get(phase, f"Phase {phase}")

        # Find source curriculum file
        src_dir = CURRICULUM / "grammar" / PHASE_DIR_MAP.get(phase, "")
        src_pattern = concept_id.split("-", 1)[1] if "-" in concept_id else concept_id
        src_file = None
        if src_dir.exists():
            for f in src_dir.iterdir():
                if f.suffix == ".md" and src_pattern.lstrip("0") in f.stem.lstrip("0"):
                    src_file = f
                    break

        # Read source content
        body = f"# {title}\n\n"
        if src_file and src_file.exists():
            content = src_file.read_text()
            # Strip any existing frontmatter from source
            if content.startswith("---"):
                _, _, content = content.split("---", 2)
                content = content.strip()
            body += content
        else:
            body += f"*Content source not found for {concept_id}*\n"

        # Build prerequisites as wiki-links
        prereqs = data.get("prerequisites", [])
        prereq_links = [f"[[{concept_id_to_title(p)}]]" for p in prereqs]

        frontmatter = {
            "generated": True,
            "source": str(src_file.relative_to(ROOT)) if src_file else "",
            "last_generated": datetime.now().strftime("%Y-%m-%d"),
            "concept_id": concept_id,
            "title": title,
            "phase": phase,
            "status": data.get("status", "unseen"),
            "error_rate_drills": data.get("error_rate_drills"),
            "error_rate_production": data.get("error_rate_production"),
            "error_trend": data.get("error_trend"),
            "last_practiced": data.get("last_practiced"),
            "practice_count": data.get("practice_count", 0),
            "integration_tested": data.get("integration_tested", False),
            "prerequisites": prereq_links,
            "tags": ["grammar", f"phase-{phase.lower()}", data.get("status", "unseen")],
        }

        out_path = VAULT / "Grammar" / phase_dir / f"{title}.md"
        write_vault_file(out_path, frontmatter, body)

    print(f"  Generated {len(grammar)} grammar notes")


def generate_vocabulary_notes(skill_map):
    """Generate vault/Vocabulary/ notes from curriculum and skill-map."""
    vocab = skill_map.get("vocabulary", {})
    for cluster_id, data in vocab.items():
        # Parse tier and cluster name
        parts = cluster_id.split("-", 1)
        tier_prefix = parts[0] if parts else "tier1"
        cluster_name = parts[1] if len(parts) > 1 else cluster_id
        title = cluster_name.replace("-", " ").title()
        tier_dir = TIER_MAP.get(tier_prefix, tier_prefix)

        # Find source file
        src_dirs = {
            "tier1": "tier1-survival",
            "tier2": "tier2-daily-life",
            "tier3": "tier3-social",
            "tier4": "tier4-abstract",
        }
        src_subdir = src_dirs.get(tier_prefix, tier_prefix)
        src_file = CURRICULUM / "vocabulary" / src_subdir / f"{cluster_name}.md"

        body = f"# {title}\n\n"
        if src_file.exists():
            content = src_file.read_text()
            if content.startswith("---"):
                _, _, content = content.split("---", 2)
                content = content.strip()
            body += content
        else:
            body += f"*Content source not found for {cluster_id}*\n"

        tier_num = int(tier_prefix.replace("tier", "")) if "tier" in tier_prefix else 0
        category = src_subdir.split("-", 1)[1] if "-" in src_subdir else ""

        frontmatter = {
            "generated": True,
            "source": str(src_file.relative_to(ROOT)) if src_file.exists() else "",
            "last_generated": datetime.now().strftime("%Y-%m-%d"),
            "cluster_id": cluster_id,
            "title": title,
            "tier": tier_num,
            "category": category,
            "status": data.get("status", "unseen"),
            "words_total": data.get("words_total", 0),
            "words_introduced": data.get("words_introduced", 0),
            "passive_known": data.get("passive_known", 0),
            "active_known": data.get("active_known", 0),
            "last_practiced": data.get("last_practiced"),
            "tags": ["vocabulary", f"tier-{tier_num}", category, data.get("status", "unseen")],
        }

        out_path = VAULT / "Vocabulary" / tier_dir / f"{title}.md"
        write_vault_file(out_path, frontmatter, body)

    print(f"  Generated {len(vocab)} vocabulary notes")


def generate_pronunciation_notes(skill_map):
    """Generate vault/Pronunciation/ notes from curriculum."""
    pronunciation = skill_map.get("pronunciation", {})
    for sound_id, data in pronunciation.items():
        title = sound_id.replace("-", " ").title()
        src_file = CURRICULUM / "pronunciation" / f"{sound_id}.md"

        body = f"# {title}\n\n"
        if src_file.exists():
            content = src_file.read_text()
            if content.startswith("---"):
                _, _, content = content.split("---", 2)
                content = content.strip()
            body += content

        frontmatter = {
            "generated": True,
            "source": str(src_file.relative_to(ROOT)) if src_file.exists() else "",
            "last_generated": datetime.now().strftime("%Y-%m-%d"),
            "sound_id": sound_id,
            "title": title,
            "status": data.get("status", "unseen"),
            "last_practiced": data.get("last_practiced"),
            "tags": ["pronunciation", data.get("status", "unseen")],
        }

        out_path = VAULT / "Pronunciation" / f"{title}.md"
        write_vault_file(out_path, frontmatter, body)

    print(f"  Generated {len(pronunciation)} pronunciation notes")


def generate_home(skill_map, schedule):
    """Generate vault/Home.md with Dataview queries."""
    phase = schedule.get("current_phase", "A-foundation")
    week = schedule.get("current_week", 1)

    body = """# My Spanish Journey

## Right Now

```dataview
TABLE WITHOUT ID
  "Phase" AS label,
  current_phase AS value
FROM "state"
WHERE file.name = "schedule"
```

> Check your most recent daily note for today's homework.

## Today's Homework

```dataview
TASK
FROM "vault/Daily"
SORT file.name DESC
LIMIT 1
```

## Active Concepts

```dataview
TABLE status, error_rate_drills AS "Drills", error_rate_production AS "Production", error_trend AS "Trend"
FROM "vault/Grammar" OR "vault/Vocabulary"
WHERE status != "unseen" AND status != "automatic"
SORT status DESC
```

## Recent Milestones

```dataview
TABLE date, title, type
FROM "vault/Progress"
WHERE contains(tags, "milestone")
SORT date DESC
LIMIT 3
```

## Quick Links

- [[vault/Roadmap|Roadmap]]
- [[parking-lot|Parking Lot]]
- [[journal/|Journal]]
- [[vault/Progress/Grammar Progress|Grammar Progress]]
- [[vault/Progress/Vocabulary Progress|Vocabulary Progress]]
"""

    frontmatter = {
        "generated": True,
        "last_generated": datetime.now().strftime("%Y-%m-%d"),
        "tags": ["dashboard"],
    }

    write_vault_file(VAULT / "Home.md", frontmatter, body)
    print("  Generated Home.md")


def generate_roadmap(skill_map):
    """Generate vault/Roadmap.md with Mermaid dependency trees."""
    grammar = skill_map.get("grammar", {})

    body = "# Roadmap\n\n"

    for phase_letter, phase_name in PHASE_MAP.items():
        phase_concepts = {
            k: v for k, v in grammar.items() if concept_id_to_phase(k) == phase_letter
        }
        if not phase_concepts:
            continue

        acquired = sum(1 for v in phase_concepts.values() if v.get("status") in ("acquired", "automatic"))
        total = len(phase_concepts)

        body += f"## {phase_name}\n\n"
        body += f"**Progress:** {acquired}/{total} concepts acquired\n\n"

        # Status indicators
        status_icons = {
            "unseen": "○",
            "introduced": "◐",
            "practicing": "◑",
            "acquired": "●",
            "automatic": "★",
            "regressed": "⟲",
        }

        for cid, cdata in phase_concepts.items():
            icon = status_icons.get(cdata.get("status", "unseen"), "?")
            title = concept_id_to_title(cid)
            body += f"- {icon} [[{title}]]\n"

        body += "\n"

        # Mermaid dependency graph
        body += "```mermaid\ngraph LR\n"
        for cid, cdata in phase_concepts.items():
            title = concept_id_to_title(cid)
            safe_id = cid.replace("-", "_")
            status = cdata.get("status", "unseen")
            style = ":::acquired" if status in ("acquired", "automatic") else ""
            body += f'    {safe_id}["{title}"]{style}\n'
            for prereq in cdata.get("prerequisites", []):
                safe_prereq = prereq.replace("-", "_")
                body += f"    {safe_prereq} --> {safe_id}\n"
        body += "```\n\n"

    frontmatter = {
        "generated": True,
        "last_generated": datetime.now().strftime("%Y-%m-%d"),
        "tags": ["roadmap"],
    }

    write_vault_file(VAULT / "Roadmap.md", frontmatter, body)
    print("  Generated Roadmap.md")


def generate_progress_dashboards():
    """Generate vault/Progress/ dashboard files."""
    # Grammar Progress
    body = """# Grammar Progress

```dataview
TABLE phase, status, error_rate_drills AS "Drills", error_rate_production AS "Production", error_trend AS "Trend", last_practiced AS "Last Practiced"
FROM "vault/Grammar"
WHERE generated = true
SORT phase ASC, status DESC
```
"""
    write_vault_file(
        VAULT / "Progress" / "Grammar Progress.md",
        {"generated": True, "last_generated": datetime.now().strftime("%Y-%m-%d"), "tags": ["dashboard"]},
        body,
    )

    # Vocabulary Progress
    body = """# Vocabulary Progress

```dataview
TABLE tier, status, words_total AS "Total", words_introduced AS "Introduced", active_known AS "Active", passive_known AS "Passive"
FROM "vault/Vocabulary"
WHERE generated = true
SORT tier ASC, status DESC
```
"""
    write_vault_file(
        VAULT / "Progress" / "Vocabulary Progress.md",
        {"generated": True, "last_generated": datetime.now().strftime("%Y-%m-%d"), "tags": ["dashboard"]},
        body,
    )

    # Weekly Reports (append-only, created empty)
    reports_path = VAULT / "Progress" / "Weekly Reports.md"
    if not reports_path.exists():
        write_vault_file(
            reports_path,
            {"generated": True, "last_generated": datetime.now().strftime("%Y-%m-%d"), "tags": ["dashboard"]},
            "# Weekly Reports\n\n*Reports are appended here during weekly reviews.*\n",
        )

    # Milestones
    milestones_path = VAULT / "Progress" / "Milestones.md"
    if not milestones_path.exists():
        write_vault_file(
            milestones_path,
            {"generated": True, "last_generated": datetime.now().strftime("%Y-%m-%d"), "tags": ["dashboard"]},
            "# Milestones\n\n*Milestones are recorded here as they happen.*\n",
        )

    print("  Generated progress dashboards")


def generate_templates():
    """Generate vault/Templates/ for Templater plugin."""
    # Daily Note template
    daily = """---
generated: true
date: {{date}}
session_number: 0
session_type: ""
duration_minutes: 0
concepts_practiced: []
homework_complete: false
tags:
  - daily
  - session
---

# Session — {{date}}

## Summary


## Concepts Practiced


## Errors Noted


## Homework
- [ ] Anki review
- [ ] 

## Journal Prompt

"""
    (VAULT / "Templates" / "Daily Note.md").write_text(daily)

    # Journal Entry template
    journal = """---
date: {{date}}
prompt: ""
generated: false
tags:
  - journal
---

## {{date}}

**Prompt:**



"""
    (VAULT / "Templates" / "Journal Entry.md").write_text(journal)
    print("  Generated templates")


def generate_getting_started():
    """Generate vault/Getting Started.md."""
    body = """# Getting Started with Your Spanish Study Vault

Welcome! This vault is your study companion — it tracks your progress, shows your homework, and lets you explore the entire Spanish curriculum as an interconnected knowledge graph.

## Setup (one-time)

1. **Install Obsidian** — Download from [obsidian.md](https://obsidian.md) if you haven't already.
2. **Open this folder as a vault** — In Obsidian, choose "Open folder as vault" and select this project directory.
3. **Trust community plugins** — Obsidian will ask about community plugins. Click "Trust author and enable plugins."
4. **Install required plugins** — Go to Settings > Community Plugins > Browse:
   - **Dataview** — powers all dashboards and progress tables
   - **Homepage** — opens your dashboard when you launch the vault
5. **Install recommended plugins:**
   - **Calendar** — visual calendar in sidebar showing session days
   - **Templater** — templates for journal entries
6. **Configure Homepage** — Settings > Homepage > Set to `vault/Home.md`
7. **Configure Calendar** — Settings > Calendar > Daily notes folder: `vault/Daily`

## Your Vault

- **Home** (`vault/Home.md`) — your dashboard. Homework, active concepts, streak.
- **Roadmap** (`vault/Roadmap.md`) — where you are and where you're going.
- **Grammar/** — full reference for every grammar concept, with your mastery status.
- **Vocabulary/** — every vocabulary cluster with word lists and progress.
- **Pronunciation/** — guides for every Spanish sound.
- **Progress/** — dashboards for grammar, vocabulary, weekly reports, milestones.
- **Journal/** — your Spanish writing practice (you write these!).
- **Parking Lot** — jot down questions, words you encounter, things to discuss.

## The Graph

Press `Ctrl/Cmd + G` to open the graph view. You'll see the entire Spanish curriculum as interconnected nodes, colored by your mastery status:
- Gray = not yet started
- Blue = introduced
- Amber = practicing
- Green = acquired
- Red = regressed

## Daily Workflow

1. Open the vault — Home.md shows your homework.
2. Check your homework items (checkboxes in the daily note).
3. Write your journal entry if one was assigned.
4. Add anything to the Parking Lot you want to discuss next session.
5. Explore the graph or browse grammar/vocabulary when curious.
"""

    frontmatter = {
        "generated": True,
        "last_generated": datetime.now().strftime("%Y-%m-%d"),
        "tags": ["guide"],
    }

    write_vault_file(VAULT / "Getting Started.md", frontmatter, body)
    print("  Generated Getting Started.md")


def full_generation():
    """Run full vault generation."""
    print("Loading state files...")
    skill_map = load_yaml(STATE / "skill-map.yaml")
    schedule = load_yaml(STATE / "schedule.yaml")

    print("Generating vault content...")
    generate_grammar_notes(skill_map)
    generate_vocabulary_notes(skill_map)
    generate_pronunciation_notes(skill_map)
    generate_home(skill_map, schedule)
    generate_roadmap(skill_map)
    generate_progress_dashboards()
    generate_templates()
    generate_getting_started()

    print("\nVault generation complete!")
    print(f"Output: {VAULT}")


def session_update(date_str):
    """Run per-session vault update."""
    print(f"Updating vault for session {date_str}...")
    skill_map = load_yaml(STATE / "skill-map.yaml")

    # Update grammar note frontmatter
    grammar = skill_map.get("grammar", {})
    updated = 0
    for concept_id, data in grammar.items():
        phase = concept_id_to_phase(concept_id)
        title = concept_id_to_title(concept_id)
        phase_dir = PHASE_MAP.get(phase, f"Phase {phase}")
        note_path = VAULT / "Grammar" / phase_dir / f"{title}.md"

        if note_path.exists():
            content = note_path.read_text()
            if "generated: true" in content:
                # Update frontmatter fields
                # Read existing frontmatter
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    fm["status"] = data.get("status", "unseen")
                    fm["error_rate_drills"] = data.get("error_rate_drills")
                    fm["error_rate_production"] = data.get("error_rate_production")
                    fm["error_trend"] = data.get("error_trend")
                    fm["last_practiced"] = data.get("last_practiced")
                    fm["practice_count"] = data.get("practice_count", 0)
                    fm["integration_tested"] = data.get("integration_tested", False)
                    fm["tags"] = ["grammar", f"phase-{phase.lower()}", data.get("status", "unseen")]
                    fm["last_generated"] = datetime.now().strftime("%Y-%m-%d")

                    with open(note_path, "w") as f:
                        f.write("---\n")
                        yaml.dump(fm, f, default_flow_style=False, allow_unicode=True)
                        f.write("---\n")
                        f.write(parts[2])
                    updated += 1

    # Same for vocabulary
    vocab = skill_map.get("vocabulary", {})
    for cluster_id, data in vocab.items():
        parts_id = cluster_id.split("-", 1)
        tier_prefix = parts_id[0]
        cluster_name = parts_id[1] if len(parts_id) > 1 else cluster_id
        title = cluster_name.replace("-", " ").title()
        tier_dir = TIER_MAP.get(tier_prefix, tier_prefix)
        note_path = VAULT / "Vocabulary" / tier_dir / f"{title}.md"

        if note_path.exists():
            content = note_path.read_text()
            if "generated: true" in content:
                file_parts = content.split("---", 2)
                if len(file_parts) >= 3:
                    fm = yaml.safe_load(file_parts[1])
                    fm["status"] = data.get("status", "unseen")
                    fm["words_total"] = data.get("words_total", 0)
                    fm["words_introduced"] = data.get("words_introduced", 0)
                    fm["passive_known"] = data.get("passive_known", 0)
                    fm["active_known"] = data.get("active_known", 0)
                    fm["last_practiced"] = data.get("last_practiced")
                    fm["last_generated"] = datetime.now().strftime("%Y-%m-%d")

                    tier_num = int(tier_prefix.replace("tier", ""))
                    src_dirs = {"tier1": "survival", "tier2": "daily-life", "tier3": "social", "tier4": "abstract"}
                    category = src_dirs.get(tier_prefix, "")
                    fm["tags"] = ["vocabulary", f"tier-{tier_num}", category, data.get("status", "unseen")]

                    with open(note_path, "w") as f:
                        f.write("---\n")
                        yaml.dump(fm, f, default_flow_style=False, allow_unicode=True)
                        f.write("---\n")
                        f.write(file_parts[2])
                    updated += 1

    # Regenerate roadmap
    generate_roadmap(skill_map)

    print(f"  Updated {updated} concept notes + roadmap")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Obsidian vault content")
    parser.add_argument("--full", action="store_true", help="Full generation (init/curriculum change)")
    parser.add_argument("--session", action="store_true", help="Per-session update")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Session date (YYYY-MM-DD)")

    args = parser.parse_args()

    if args.full:
        full_generation()
    elif args.session:
        session_update(args.date)
    else:
        parser.print_help()
        sys.exit(1)
```

- [ ] **Step 2: Make the script executable**

```bash
chmod +x scripts/generate-vault.py
```

- [ ] **Step 3: Test script with --full**

```bash
python3 scripts/generate-vault.py --full
```

Verify output reports generation counts for grammar (34), vocabulary (22), pronunciation (12), plus Home.md, Roadmap.md, dashboards, templates, Getting Started.

- [ ] **Step 4: Verify generated files exist**

```bash
ls vault/Grammar/Phase\ A\ -\ Foundation/ | wc -l
ls vault/Vocabulary/Tier\ 1\ -\ Survival/ | wc -l
ls vault/Pronunciation/ | wc -l
cat vault/Home.md | head -20
```

- [ ] **Step 5: Verify YAML frontmatter parses on a generated file**

```bash
python3 -c "
import yaml
content = open('vault/Grammar/Phase A - Foundation/Present Regular.md').read()
parts = content.split('---', 2)
fm = yaml.safe_load(parts[1])
assert fm['generated'] == True
assert 'concept_id' in fm
assert 'tags' in fm
print('Frontmatter OK:', fm['concept_id'], fm['status'])
"
```

- [ ] **Step 6: Commit**

```bash
git add scripts/generate-vault.py
git commit -m "feat: add vault generation script

Python script with two modes:
--full: generates all vault content from curriculum + state
--session: lightweight per-session frontmatter updates

Generates Grammar, Vocabulary, Pronunciation notes with
Dataview-queryable frontmatter, Home.md with Dataview queries,
Roadmap.md with Mermaid dependency graphs, progress dashboards,
templates, and Getting Started guide."
```

---

## Wave 6: Final Assembly

### Task 15: Run Generation, Update First Session, Final Verification

**Files:**
- Modify: `curriculum/tutor-guides/first-session.md`
- Generated: all `vault/` content

- [ ] **Step 1: Run full generation**

```bash
python3 scripts/generate-vault.py --full
```

- [ ] **Step 2: Update first-session.md with vault setup step**

Read `curriculum/tutor-guides/first-session.md` and add Step 8 after Step 7:

```markdown
### 8. Vault Setup
After state initialization, set up the learner's Obsidian vault:
1. Run the generation script: `python3 scripts/generate-vault.py --full`
2. Tell the learner: "I've set up your study companion. Open Obsidian, point it at this project folder, and install the community plugins listed in vault/Getting Started.md. This is where you'll find your homework, track progress, and write your journal."
3. Commit vault/ alongside initial state files.
4. The first session's daily note will be generated as part of normal post-session vault updates.
```

- [ ] **Step 3: Final verification — check all new files exist**

```bash
echo "=== New Guides ==="
ls curriculum/tutor-guides/return-session.md
ls curriculum/tutor-guides/decision-engine.md
ls curriculum/tutor-guides/phase-transition-guide.md

echo "=== New Docs ==="
ls docs/session-log-example.yaml
ls docs/progress-report-template.md

echo "=== Archive Dir ==="
ls state/sessions/archive/

echo "=== Vault ==="
find vault -name "*.md" | wc -l

echo "=== Obsidian Config ==="
ls .obsidian/app.json
ls .obsidian/graph.json

echo "=== Script ==="
ls scripts/generate-vault.py
```

- [ ] **Step 4: Verify no dead file remains**

```bash
test ! -f docs/claude-md-draft.md && echo "Dead file removed OK"
```

- [ ] **Step 5: Verify skill-map migration complete**

```bash
python3 -c "
import yaml
sm = yaml.safe_load(open('state/skill-map.yaml'))
grammar = sm.get('grammar', {})
for cid, data in grammar.items():
    assert 'error_rate_drills' in data, f'{cid} missing error_rate_drills'
    assert 'error_rate_production' in data, f'{cid} missing error_rate_production'
    assert 'error_rate_recent' not in data, f'{cid} still has error_rate_recent'
print(f'All {len(grammar)} grammar concepts migrated OK')
"
```

- [ ] **Step 6: Verify CLAUDE.md has all required changes**

```bash
grep -c "decision-engine.md" CLAUDE.md          # should be >= 1
grep -c "phase-transition-guide.md" CLAUDE.md    # should be >= 1
grep -c "return-session.md" CLAUDE.md            # should be >= 1
grep -c "Correction Mode" CLAUDE.md              # should be >= 1
grep -c "vault" CLAUDE.md                        # should be >= 3
grep -c "generated: true" CLAUDE.md              # should be >= 1
```

- [ ] **Step 7: Commit generated vault content + first-session update**

```bash
git add vault/ curriculum/tutor-guides/first-session.md
git commit -m "feat: generate initial vault content and update first-session guide

- Full vault generation: Grammar, Vocabulary, Pronunciation notes
- Home.md dashboard with Dataview queries
- Roadmap.md with Mermaid dependency trees
- Progress dashboards, templates, Getting Started guide
- First-session.md updated with Step 8 vault setup"
```

- [ ] **Step 8: Final commit — all .obsidian config**

```bash
git add .obsidian/
git commit -m "feat: add Obsidian vault configuration

- app.json with excluded folders for clean learner navigation
- graph.json with status-based node coloring"
```
