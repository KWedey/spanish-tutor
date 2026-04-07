# Initial Assessment & Placement Validation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the initial placement assessment with multi-dimensional signals, refined scoring, and a post-placement validation protocol for learners who skip onboarding.

**Architecture:** Schema-first approach — add new fields to state files and system-design.md, then update the tutor guides that reference them. No application code; all changes are YAML schemas and markdown guides.

**Spec:** `docs/superpowers/specs/2026-04-07-initial-assessment-redesign.md`

---

### Task 1: Add Schema Defaults to State Files

**Files:**
- Modify: `state/learner-profile.yaml`
- Modify: `state/schedule.yaml`
- Modify: `state/system-health.yaml`

- [ ] **Step 1: Add `initial_placement` block to learner-profile.yaml**

Add before the closing of the file (after the `notes` field at the end):

```yaml
initial_placement:
  level: ""
  date: null
  self_report: ""
  grammar_result: ""
  vocabulary_observation: ""
  reading_result: ""
  confidence: ""
  evidence_summary: ""
```

- [ ] **Step 2: Add `placement_validation` block to schedule.yaml**

Add before `adjustment_log` at the end of the file:

```yaml
placement_validation:
  active: false
  confidence: null
  sessions_completed: 0
  listening_baseline_set: false
  total_downgrades: 0
  queue: []
```

- [ ] **Step 3: Add `placement_validation_metrics` block to system-health.yaml**

Add before the `last_validation_issues` field near the end:

```yaml
placement_validation_metrics:
  placement_level: null
  initial_confidence: null
  total_concepts_validated: 0
  total_downgrades: 0
  final_assessment: null
  validation_completed: null
```

- [ ] **Step 4: Validate all three YAML files parse correctly**

Run:
```bash
python3 -c "
import yaml
for f in ['state/learner-profile.yaml', 'state/schedule.yaml', 'state/system-health.yaml']:
    with open(f) as fh:
        yaml.safe_load(fh)
    print(f'{f}: OK')
"
```

Expected: All three files print OK.

- [ ] **Step 5: Commit**

```bash
git add state/learner-profile.yaml state/schedule.yaml state/system-health.yaml
git commit -m "schema: add placement validation fields to state files"
```

---

### Task 2: Update system-design.md Schema Documentation

**Files:**
- Modify: `docs/system-design.md`

The schema examples in system-design.md are the canonical reference. Each new block must be documented here alongside the existing schemas.

- [ ] **Step 1: Add `initial_placement` to the learner-profile schema section**

In the learner-profile schema (Section 2), insert before the closing ` ``` ` (after `notes: ""`  around line 259):

```yaml

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

- [ ] **Step 2: Add `placement_validation` to the schedule schema section**

In the schedule schema (Section 4), insert before the closing ` ``` ` (after the `adjustment_log` block around line 517):

```yaml

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

- [ ] **Step 3: Add `assessment` and `validation_checks` to the session log schema section**

In the session log schema (Section 5), insert before `next_session:` (around line 603):

```yaml

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
```

- [ ] **Step 4: Add `placement_validation_metrics` to the system-health schema section**

In the system-health schema (Section 8), insert before `last_system_review: null` (around line 729):

```yaml

# Placement validation effectiveness (populated after validation period closes)
placement_validation_metrics:
  placement_level: null     # where the learner was placed
  initial_confidence: null  # high / medium / low
  total_concepts_validated: 0
  total_downgrades: 0
  final_assessment: null    # placement-confirmed / placement-adjusted
  validation_completed: null  # date validation period closed
```

- [ ] **Step 5: Verify the document renders correctly**

Run:
```bash
head -5 docs/system-design.md && echo "--- File readable ---" && wc -l docs/system-design.md
```

Visually scan the edited sections to confirm no broken markdown or misaligned YAML indentation.

- [ ] **Step 6: Commit**

```bash
git add docs/system-design.md
git commit -m "schema: document placement assessment and validation schemas in system-design"
```

---

### Task 3: Add GAP Table Row for Null Error Rates

**Files:**
- Modify: `curriculum/tutor-guides/decision-engine.md`

- [ ] **Step 1: Add the null error rate row to the GAP scoring table**

In the GAP table (around line 30-40), insert after the `Practicing, production error <15% | 3` row and before the `Acquired, not integration-tested | 2` row:

```markdown
| Practicing, error rate null (unassessed) | 7 |
```

The table should now read:

```markdown
| State | Score |
|-------|-------|
| Regressed | 10 |
| Practicing, production error >30% | 8 |
| Practicing, drill/production mismatch (transfer gap) | 7 |
| Practicing, error rate null (unassessed) | 7 |
| Practicing, production error 15-30% | 5 |
| Practicing, production error <15% | 3 |
| Acquired, not integration-tested | 2 |
| Acquired + integration-tested | 0 |
```

- [ ] **Step 2: Commit**

```bash
git add curriculum/tutor-guides/decision-engine.md
git commit -m "fix: add GAP scoring for unassessed concepts with null error rates"
```

---

### Task 4: Rewrite First Session Assessment Protocol

**Files:**
- Modify: `curriculum/tutor-guides/first-session.md`

This is the largest change. Replace the Experience Assessment section (### 3), the Placement Protocol subsection, and the skill-map pre-population rules. Also update State Initialization (### 7).

- [ ] **Step 1: Replace section 3 (Experience Assessment) and the Placement Protocol**

Replace everything from `### 3. Experience Assessment (5 min)` through the end of `**Onboarding skip rules:**` section (lines 47-83) with:

```markdown
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

**Below placement level:** `acquired` with `performance_unscaffolded: competent`. Grammar is hierarchical — producing above a level implies mastery of that level. If the inference is wrong, the validation protocol catches it.

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
```

- [ ] **Step 2: Update State Initialization (section 7) to include validation queue setup**

Replace the current section 7 content (lines 109-116) with:

```markdown
### 7. State Initialization

After the session, create and populate:
- `state/learner-profile.yaml` — all identity, goals, schedule fields, calibration, and initial_placement
- `state/skill-map.yaml` — mark concepts per placement rules above
- `state/schedule.yaml` — set initial phase, onboarding_complete
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
```

- [ ] **Step 3: Verify the document is well-formed**

Read the modified file and check:
- All markdown headers are properly nested (### under ##)
- All tables render (consistent pipe separators)
- Section numbers flow correctly (1-8)
- No orphaned references to removed content

- [ ] **Step 4: Commit**

```bash
git add curriculum/tutor-guides/first-session.md
git commit -m "feat: enhanced assessment protocol with multi-dimensional placement"
```

---

### Task 5: Create Placement Validation Tutor Guide

**Files:**
- Create: `curriculum/tutor-guides/placement-validation.md`

- [ ] **Step 1: Write the placement validation guide**

Create `curriculum/tutor-guides/placement-validation.md` with this content:

```markdown
# Placement Validation Guide

Loaded when: `placement_validation.active` is true and `placement_validation.sessions_completed` < 3 in schedule.yaml. This applies only to learners who skipped onboarding (Early B+ placement).

## Purpose

Confirm or correct the initial placement through real practice. The learner should experience this as normal warm-up and conversation — never as testing.

## How It Works

Each session during the validation period (sessions 2-4), overlay 2-3 spot-checks on top of the normal session flow. The decision engine runs normally — validation adds to the session, it doesn't replace it.

## Session Flow Overlay

### Before the session
1. Read `placement_validation.queue` from schedule.yaml
2. Select 2-3 concepts to validate this session (highest priority `pending` items)
3. Plan warm-up topics and conversation prompts that naturally elicit these structures

### During warm-up and conversation
4. Use directed conversation to elicit target concepts (see Elicitation Examples below)
5. Observe and score each concept
6. Do NOT tell the learner you're validating placement — frame everything as getting to know them

### After the session
7. Log results in the session file under `validation_checks`
8. Process downgrades (max 2 per session)
9. Update `placement_validation.sessions_completed`
10. Update the queue: mark checked concepts, add `pending_downgrade` for deferred downgrades

## Elicitation Examples

Choose warm-up topics and conversation prompts that naturally require the target structure:

| Concept | Natural elicitation |
|---|---|
| A-01 present regular | "Tell me about your typical day." |
| A-02 ser vs estar | "How are you feeling today? Describe your house." |
| A-03 gender agreement | "What's your favorite restaurant like? Describe it." |
| A-05 basic questions | "Ask me a few questions about myself." |
| A-06 gustar-type verbs | "What do you like doing on weekends? What bothers you?" |
| A-07 present irregular | "What do you want to do this summer? What do you know about...?" |
| B-01 preterite regular | "What did you do this weekend?" |
| B-03 imperfect | "What was your childhood like? What did you used to do?" |
| B-04 preterite vs imperfect | "Tell me about a trip — what was happening, what happened." |
| B-05 reflexive verbs | "Walk me through your morning routine." |
| B-06 direct object pronouns | "Did you finish the homework? When did you start it?" |
| B-07 indirect object pronouns | "Tell me about a gift you gave someone." |
| B-08 progressive | "What are you working on these days?" |
| C-01 present subjunctive | "What do you hope happens this year?" |
| C-04 conditional | "If you could live anywhere, where would it be?" |

## Scoring Rubric

For each spot-checked concept:

| Observation | Result | Action |
|---|---|---|
| Uses concept correctly and naturally | Validated | Stays `acquired`, remove from queue, log `checked-pass` |
| Minor errors (1-2 per exchange) | Validated with note | Stays `acquired`, add maintenance note to skill-map, log `checked-pass` |
| Significant errors, struggles to produce | Downgrade | → `practicing`, set error rates from observation, log `checked-fail` |
| Can't produce or avoids entirely | Downgrade | → `introduced`, flag for Stage 1-2 work, log `checked-fail` |
| Concept not naturally elicited by the conversation | Inconclusive | Remains `pending` in queue for next session |

## Downgrade Rules

- **Maximum 2 downgrades per session.** If 3 concepts fail in one session, record all failures but defer the third downgrade: mark it `pending_downgrade` in the queue. Process the status change at the start of the next session — do not re-validate it.
- **Each downgrade:** Update skill-map (status, error rates), log in session file with evidence.
- **Prerequisite cascade:** If a downgraded concept is a prerequisite for other acquired concepts, those dependent concepts should be queued for validation in the next session (they may be fine, but check).

## Widespread Gap Handling

If total downgrades across the validation period reach 4+:

1. Log `placement_adjustment: significant` in the session file
2. Reduce `max_new_concepts_per_week` to 1 in schedule.yaml
3. Note in system-health.yaml under `placement_validation_metrics`
4. Frame to the learner: "You've got a solid foundation — there are just some spots I want to make sure are rock solid before we build on them."
5. Do NOT reroute to onboarding. The decision engine handles recovery through its existing mechanics (concurrent concept cap, prerequisite gating, NEED scoring).

## Listening Baseline (Session 2)

During the session 2 warm-up:
1. Review the Dreaming Spanish assignment from session 1
2. Ask: "What level did you watch? How much did you follow?"
3. If the learner's `calibration.tendency` is `over-estimates`, probe: "What was the video about? Can you summarize what happened?"
4. Set `receptive_skills.listening.current_level` based on reported and observed comprehension
5. Set `placement_validation.listening_baseline_set: true`

## Closing the Validation Period

After session 4 (or session 3 if confidence is high and no downgrades):

1. Concepts still `pending` in queue: accept current status if overall performance is consistent. If performance has been mixed, extend to session 5 (maximum).
2. Process any remaining `pending_downgrade` items
3. Set `placement_validation.active: false`
4. Set `placement_validation.confidence: validated`
5. Log validation summary in the session file:
   - Total concepts validated
   - Pass/downgrade counts
   - Final assessment: `placement-confirmed` or `placement-adjusted`
6. Update `system-health.yaml` `placement_validation_metrics` with final numbers

## Early Close Criteria

Close validation after session 3 (skip session 4) if ALL of:
- Placement confidence was high or medium
- Zero downgrades in sessions 2-3
- Overall session performance is strong (no struggling on any practiced concepts)

## Framing Language

**Do say:**
- "Tell me about..." / "How would you say..." / "Let's talk about..."
- "I want to make sure we're building on the right foundation"
- "Your [concept] is solid — nice work"
- "I noticed [concept] needs a bit more practice — totally normal, we'll work on it"

**Do NOT say:**
- "I'm testing your placement"
- "Let me check if you actually know this"
- "Your placement might have been wrong"
- "We need to go back to basics"
```

- [ ] **Step 2: Verify the file is well-formed**

Read the new file and check: all tables have consistent pipes, all headers are properly nested, no broken markdown.

- [ ] **Step 3: Commit**

```bash
git add curriculum/tutor-guides/placement-validation.md
git commit -m "feat: add placement validation tutor guide for post-assessment sessions"
```

---

### Task 6: Update CLAUDE.md Routing and Guardrails

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add placement validation conditional load to Step 4**

In the Step 4 conditional loads section (around line 61), add after the line about the decision engine (`Standard session (post-onboarding)? Also read...decision-engine.md`):

```markdown
- `placement_validation.active` is true and `placement_validation.sessions_completed < 3`? Also read `curriculum/tutor-guides/placement-validation.md`
```

- [ ] **Step 2: Add guardrail exception for placement-acquired concepts**

In the Guardrails section, modify the acquisition guardrail. The current line reads:

```
- **Never mark a concept as "acquired" unless** error rates < 10% (both drill and production), `performance_unscaffolded` is "competent", AND the concept has been practiced in 3+ separate sessions.
```

Replace with:

```
- **Never mark a concept as "acquired" unless** error rates < 10% (both drill and production), `performance_unscaffolded` is "competent", AND the concept has been practiced in 3+ separate sessions. **Exception:** placement-acquired concepts (pre-populated below the assessed level during initial placement) are exempt from the session count requirement — the placement validation protocol serves as verification.
```

- [ ] **Step 3: Verify CLAUDE.md is well-formed**

Read the modified sections to confirm no broken markdown or misaligned table formatting.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "feat: add placement validation routing and guardrail exception to CLAUDE.md"
```

---

### Task 7: Final Verification Pass

- [ ] **Step 1: Validate all YAML state files still parse**

Run:
```bash
python3 -c "
import yaml
for f in ['state/learner-profile.yaml', 'state/schedule.yaml', 'state/system-health.yaml', 'state/skill-map.yaml']:
    with open(f) as fh:
        yaml.safe_load(fh)
    print(f'{f}: OK')
"
```

Expected: All four files print OK.

- [ ] **Step 2: Cross-reference check**

Verify these references are consistent:
1. The `placement_validation.queue` entry schema in system-design.md matches the fields referenced in placement-validation.md (concept_id, priority, status, checked_in_session, notes)
2. The `assessment` block schema in system-design.md matches the fields referenced in first-session.md
3. The GAP table row in decision-engine.md ("Practicing, error rate null") aligns with the "practicing with null error rates" state described in first-session.md
4. The CLAUDE.md Step 4 conditional load references `placement_validation.active` and `sessions_completed` — confirm these field names match schedule.yaml and system-design.md
5. The guardrail exception in CLAUDE.md references "placement-acquired concepts" — confirm first-session.md uses consistent terminology

- [ ] **Step 3: Final commit if any fixes were needed**

Only if the verification pass found issues:
```bash
git add -A && git commit -m "fix: address consistency issues from verification pass"
```
