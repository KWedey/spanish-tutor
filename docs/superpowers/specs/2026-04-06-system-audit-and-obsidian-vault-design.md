# System Audit Fixes & Obsidian Vault Design

**Date:** 2026-04-06
**Status:** Approved
**Approach:** Foundation → Surface (Phase 1: audit fixes, Phase 2: vault)

## Overview

A comprehensive system audit identified 20 gaps in the tutoring system — missing schemas, undefined guides, contradictions between files, and underspecified protocols. Separately, the learner experience needs a visual layer: an Obsidian vault that serves as the learner's primary interface between sessions and a reference companion during sessions.

**Phase 1** addresses all 20 audit gaps, designing every schema and protocol vault-aware (Dataview-queryable frontmatter, linkable IDs, Obsidian-compatible formats).

**Phase 2** builds the Obsidian vault on the now-stable foundation.

## Design Principles

1. **State in YAML, views in markdown.** State files remain the source of truth. The vault is a generated view layer.
2. **One-way data flow.** Tutor writes state → generator produces vault markdown. The only learner-editable vault files are journal entries, parking lot, and personal notes.
3. **Vault-aware schemas.** All new schemas use flat YAML where possible, consistent key naming, and IDs that map to Obsidian wiki-links.
4. **Generated files are flagged.** `generated: true` in frontmatter. Generator only overwrites flagged files. Learner's custom notes are safe by default.
5. **Two generation modes.** Bulk script for init/curriculum changes. Tutor direct for per-session updates.

## Out of Scope

- Mobile Obsidian support (desktop only)
- Multi-learner support (single learner per repo)
- Real-time vault updates during active sessions (post-session only)
- Obsidian Publish or web hosting
- Custom Obsidian theme (uses default)
- Obsidian plugin development (uses existing community plugins)
- Automated Anki card generation (learner creates cards manually)

---

# Phase 1: Audit Fixes

## Section 1: Missing Schemas & Definitions

### 1.1 Unified Milestone Schema

**Problem:** `state/milestones/` referenced by 4+ files but no schema exists. Separate `phase-X-completion.yaml` schema in system-design.md overlaps.

**Solution:** One unified schema that absorbs the phase-completion format. All milestone types use the same structure.

**File:** `state/milestones/YYYY-MM-DD-milestone-id.yaml`

```yaml
type: ""              # phase-transition | first-real-world | first-self-correction
                      # vocabulary-milestone | streak-milestone | fluency-milestone
                      # cultural-milestone | first-dream-in-spanish
date: "YYYY-MM-DD"
session_number: 0
title: ""             # human-readable: "First restaurant order in Spanish"
description: ""       # what happened, why it matters
evidence: ""          # observable behavior that triggered this

# Phase transitions only (replaces old phase-X-completion.yaml):
phase_transition:
  from_phase: ""
  to_phase: ""
  started: "YYYY-MM-DD"       # when from_phase began
  completed: "YYYY-MM-DD"     # transition date
  total_sessions: 0
  total_days: 0
  assessment:
    production_task: ""        # what was asked
    receptive_task: ""         # listening/reading check
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
```

### 1.2 Communication Repair & Flow Kit

**Problem:** CLAUDE.md mandates "communication repair phrases must be automatic by session 5" but no checklist defines the phrases or verification method.

**Solution:** Add concrete checklist and verification protocol to `A-00-communication-repair.md`.

**Comprehension Repair:**
- ¿Qué significa ___?
- No entiendo. ¿Puede repetir?
- Más despacio, por favor.
- ¿Puede explicar de otra manera?

**Production Repair:**
- ¿Cómo se dice ___ en español?
- ¿Está bien si digo ___?

**Time-Buying Fillers:**
- Un momento, estoy pensando...
- A ver...
- Pues...
- Es que...
- O sea...

**Dialect Notes:**
- Mexican: ¿Mande? (polite "what?"), Órale (acknowledgment)
- Castilian: ¿Cómo? preferred over ¿Mande?
- Argentine: Dale (acknowledgment/agreement)

**Verification Protocol (Session 5+):**

Method: Tutor deliberately uses an unfamiliar word or speaks at natural speed. Observe learner's response.

| Result | Classification | Action |
|--------|---------------|--------|
| Learner deploys repair phrase without hesitation | Automatic | Mark acquired |
| Learner pauses, then uses repair phrase | Emerging | Continue drilling |
| Learner switches to English or freezes | Not yet automatic | Targeted practice |

If not automatic by session 7: dedicated drill session. Assign self-monitoring homework ("count how many times you used a repair phrase during Anki review").

### 1.3 Skill-Map Error Rate Split

**Problem:** `error_rate_recent` is a single number but acquisition rules require distinct drill vs. free production performance. Decision engine needs to know which rate to use.

**Solution:** Replace `error_rate_recent` with context-aware rates. Specify rolling window and minimum sample size.

**Schema change (per grammar concept in skill-map.yaml):**

```yaml
# Old:
error_rate_recent: null
error_trend: null

# New:
error_rate_drills: null       # controlled practice, fill-in-the-blank, translation
error_rate_production: null   # free conversation, storytelling, unscaffolded output
error_trend: null             # improving | stable | declining (based on production rate)
```

**Calculation rules:**
- Rates are rolling averages over the last 5 practice instances
- If `practice_count < 3`, rates remain `null` — the decision engine uses `performance_scaffolded` / `performance_unscaffolded` qualitative assessments instead
- This prevents premature advancement or regression flags from small samples

**Decision engine usage:**

| Drills | Production | Interpretation | Route |
|--------|-----------|----------------|-------|
| High | High | Early learning | Stage 2 (controlled practice) |
| Low | High | Transfer gap | Stage 3-4 (communicative practice) |
| Low | Low | Near-acquired | Spot-check only |
| High | Low | Unusual — investigate test conditions | Review methodology |

**Advancement rule (updated):** "Acquired" requires `error_rate_production < 0.10` AND `error_rate_drills < 0.10` AND `performance_unscaffolded = "competent"` AND demonstrated in 3+ separate sessions.

### 1.4 Phase Transition Assessment Format

**Problem:** "Learner passes phase-transition assessment" referenced in multiple files but no format, tasks, or pass criteria defined.

**Solution:** New file `curriculum/tutor-guides/phase-transition-guide.md` with structured assessments per transition. Each includes production and receptive components.

**Framing guidance (all transitions):**
- Never say "I'm going to assess you" or "this is a test"
- Frame as natural conversation: "Let's talk about your week"
- Initiate when all prerequisites show "acquired" for 2+ consecutive sessions
- If learner shows anxiety, back off and retry next session embedded in normal conversation
- If learner clearly fails, don't label it — note gaps, continue in current phase, retry in 2 weeks

**A → B Assessment (15-20 min):**
- Production (10 min): "Tell me about your typical week — what you do, where you go, what you like and don't like."
  - Tests: present regular + irregular, ser/estar, gender, gustar, questions
- Receptive (5 min): Play 60-sec Dreaming Spanish clip at Beginner level. Ask: "¿De qué habló?"
  - Tests: comprehension + production
- Repair check: Tutor uses one unfamiliar word mid-conversation.
  - Tests: automatic repair phrase deployment
- Pass: A-01, A-02, A-04 at <10% production error. Repair phrases automatic. Can sustain 3+ min guided conversation.
- Borderline: Extend 1-2 weeks, focus on weakest prerequisite.

**B → C Assessment (20-25 min):**
- Production (12 min): "Tell me about something that happened last week, and what you're planning for this weekend."
  - Tests: preterite/imperfect, future, object pronouns, reflexives
- Receptive (8 min): Listen to 2-min podcast excerpt at natural speed. Answer comprehension questions in Spanish.
- Pass: B-01, B-04 at <10% production error. Appropriate past tense selection >80%. Can narrate event sequence without present tense fallback.
- Borderline: Extend 2-3 weeks. If only one prerequisite weak, focused sprint.

**C → D Assessment (25-30 min):**
- Production (15 min): "What would change about your city if you were mayor? I disagree — convince me."
  - Tests: subjunctive triggers, conditional, por/para, compound tenses
- Receptive (10 min): Read short opinion article (300 words). Summarize argument and state agreement/disagreement in Spanish.
- Pass: C-01, C-04, C-06 at <10% production error. Uses subjunctive unprompted in 2+ contexts. Sustains argument with connectors.
- Borderline: Extend 2-4 weeks. Subjunctive is the usual blocker — if that's the gap, dedicated subjunctive sprint.

### 1.5 Session Log Example

**Problem:** Session log schema exists in system-design.md but no filled-out example. First-session state initialization will be inconsistent without a reference.

**Solution:** Create `docs/session-log-example.yaml` — a complete, realistic session log demonstrating every field with plausible values. Shows: homework review with verification, multiple activity types, error logging with L1 interference tagging, skill map updates with evidence, homework assignment with time estimates, and next-session recommendations.

### 1.6 Progress Report Format

**Problem:** `progress-reports/` directory exists but no schema or template.

**Solution:** Define template for `progress-reports/YYYY-WNN.md`. Covers all skill dimensions. Sections conditional by phase. Written in encouraging, specific tone (learner reads this in the vault).

```markdown
# Week NN Progress — [Mon date] to [Sun date]

## This Week
- Sessions completed: X/Y
- Total practice time: Xh Ym (sessions + homework)
- Homework completion: X%
- Current streak: X days (longest: Y)

## Grammar
- New: [concepts introduced this week]
- Advancing: [concept: old status → new status]
- Needs work: [concept + specific gap]

## Vocabulary
- New words introduced: X
- Active vocabulary estimate: X (+Y this week)
- Production gap: X words
- Weak production: [specific words]

## Pronunciation
- Focus this week: [target]
- Progress: [observation]

## Writing (if journal active)
- Entries submitted: X
- Quality trend: [improving/stable/declining]
- Common errors: [patterns]

## Fluency Metrics (Phase C+ only)
- Speaking pace: [reference benchmark]
- Hesitation: [frequency]
- Risk-taking: [assessment]

## Highlights
- Best moment: [specific achievement with evidence]
- Breakthrough: [if any]

## Motivation
- Energy this week: [observation]
- Parking lot items addressed: [list]

## Next Week
- Primary focus: [concept]
- Weekly topic: [topic from topic-bank]
- Goal: [specific, measurable]
```

---

## Section 2: Missing & Incomplete Guides

### 2.1 Return Session Guide

**Problem:** CLAUDE.md defines a return protocol for 3+ day gaps as 4 bullet points with no operational detail. Every other session type has a dedicated guide.

**Solution:** New file `curriculum/tutor-guides/return-session.md`. Tiered approach based on gap length.

**Trigger:** Gap of 3+ days since last session. Loaded instead of standard session flow.

**Real-world encounter override:** If learner mentions real-world Spanish use during the break, switch to `real-world-debrief.md` immediately. Run return diagnostic in the next session instead.

**3-7 days (short break):**
- Welcome back warmly, zero guilt
- Quick diagnostic: revisit the 2 most recently active concepts (from `schedule.yaml` active_grammar.primary and secondary) via casual conversation (not drills)
- If performance matches pre-break levels: resume normal schedule
- If regression detected: mark concepts as regressed, reduce to 1 active concept + the regressed one
- Homework: reduce by 50% for this session only
- Resume normal load next session

**8-21 days (extended break):**
- Welcome back, acknowledge the gap without judgment
- Diagnostic: revisit all "practicing" and most recent "acquired" concepts (up to 4 concepts total)
- Expect 1-2 regressions — this is normal, say so explicitly
- Update skill-map with any status changes
- Homework: reduce by 50% for 2 sessions
- No new concepts this session — consolidation only
- Check motivation: "What brought you back?" (informs approach)

**22+ days (major break):**
- Welcome back as if it's a fresh start (but with history)
- Run abbreviated phase transition assessment for current phase
- Regressions likely across multiple concepts — don't alarm the learner
- Phase regression criteria: if >50% of current phase prerequisite concepts show regression in diagnostic, regress to previous phase. Otherwise stay in current phase with consolidation focus.
- Homework: minimal for first 3 sessions (SRS + one light task)
- Rebuild momentum before rebuilding knowledge
- If motivation is fragile: also load `emotional-intelligence.md`
- If gap > 60 days: also check `state/sessions/archive/` for the last pre-gap session

**All tiers:**
- Read last 3 session logs to remember where things stood
- Check parking lot — learner may have added real-world encounters
- Update `streak_days` to 0 (restart)
- Log `session_type: "return"` with `gap_days` field
- Do NOT reference the gap repeatedly throughout the session

### 2.2 Onboarding Failure Path

**Problem:** No guidance on what happens when a learner is significantly struggling during sessions 2-10. Can sessions be repeated? Can onboarding be extended?

**Solution:** Add to `curriculum/tutor-guides/onboarding-guide.md`.

**Struggling signals:**
- Unable to reproduce previous session's concept after review
- Error rate >50% on controlled practice after full explanation
- Learner expresses frustration or confusion 2+ sessions in a row
- Homework consistently incomplete or reported as too difficult

**Step 1 — Check external factors FIRST** (before assuming concept difficulty):
- Is homework getting done? If not, the fix is reducing load, not reteaching.
- Has available study time changed? Life events, schedule shifts?
- Is the learner overwhelmed by tools (Anki setup, multiple apps)?
- Ask: "How's your study time been this week?"
- If external: adjust homework load and tool expectations. Do NOT insert consolidation.

**Step 2 — If concept difficulty confirmed:**
1. Never repeat the exact same session — reteach with a different approach (examples-first if rules-first failed, or vice versa)
2. Insert an unscheduled consolidation session before advancing (e.g., consolidation between session 3 and 4 if gender agreement isn't landing)
3. Maximum 2 inserted consolidation sessions per concept — if still struggling, note as "slow acquisition" in skill-map and continue forward (the concept will resurface via the decision engine post-onboarding)
4. Extend onboarding beyond session 10 if:
   - 3+ A-phase concepts are still in "introduced" (not "practicing")
   - Learner hasn't demonstrated basic sentence construction
   - Communication repair phrases are not emerging
   - Maximum extension: 5 additional sessions (to session 15)
5. If extended onboarding exceeds session 15:
   - Complete onboarding regardless
   - Decision engine takes over with heavy consolidation weighting
   - Flag in system-health.yaml: `onboarding_extended: true`, `onboarding_sessions: N`
   - Reduce `max_new_concepts_per_week` to 1

**Emotional considerations:**
- Never imply the learner is behind or slow
- Frame consolidation as "let's make sure this is solid before we build on it"
- Adjust energy: more games, less drilling

### 2.3 Decision Engine Guide

**Problem:** The decision engine scoring logic exists in `system-design.md` (1,766 lines) but CLAUDE.md just says "select focus using the decision engine." The tutor never loads system-design.md during standard sessions.

**Solution:** New file `curriculum/tutor-guides/decision-engine.md`. Extracted, actionable guide loaded for standard sessions post-onboarding.

**Step 1 — Gather Candidates**

All concepts in current phase with status: introduced, practicing, regressed, or acquired (for maintenance). Plus: `carryover_concepts` from schedule.yaml. Plus: maintenance from all previous phases (with decaying priority).

Filter: exclude any where prerequisites are not met.

**Step 2 — Score Each Candidate**

```
PRIORITY = NEED + GAP + DECAY + TOPIC_BOOST - VARIETY_PENALTY
```

**NEED (0-10):** How important for current phase?

| Concept type | Score |
|-------------|-------|
| Phase prerequisite (unlocks most concepts) | 10 |
| Current phase concept | 7 |
| Carryover concept from prior phase | 5 |
| Current phase maintenance | 2 |
| Previous phase maintenance | 1 |
| Two+ phases back maintenance | 0.5 |

**GAP (0-10):** Distance from "acquired"? Uses `error_rate_production`.

| State | Score |
|-------|-------|
| Regressed | 10 |
| Practicing, production error >30% | 8 |
| Practicing, drill/production mismatch (transfer gap) | 7 |
| Practicing, production error 15-30% | 5 |
| Practicing, production error <15% | 3 |
| Acquired, not integration-tested | 2 |
| Acquired + integration-tested | 0 |

**DECAY (0-10):** Days since last practiced?

| Days | Score |
|------|-------|
| 0-1 | 0 |
| 2-3 | 2 |
| 4-7 | 5 |
| 8-14 | 7 |
| 15+ | 9 |

**TOPIC_BOOST (0-3):** Does the concept align with this week's narrow topic?

| Alignment | Score |
|-----------|-------|
| Direct match (topic naturally elicits this concept) | 3 |
| Adjacent (topic uses vocabulary related to this concept) | 1 |
| No connection | 0 |

**VARIETY_PENALTY (0-5):** Same activity type 3 days in a row? Penalize that type by 5. Prefer alternation.

**Step 3 — Apply Modifiers**

- **Low energy:** Boost passive activities (listening/reading review), reduce production demands. Halve GAP score for challenging concepts.
- **Low motivation / at-risk:** Boost easy wins (high-confidence concepts), add novelty. Double NEED for fun/interesting concepts.
- **Parking lot items:** If a parking lot item aligns with a candidate concept, boost that concept by +3. If the item suggests a concept not in the candidate list but prerequisites are met, it can override secondary concept selection.
- **Sprint override:** If `sprint.active` is true, only score concepts in `sprint.focus_areas`. All others excluded.

**Step 4 — Select Top 1-2 Concepts**

Highest score = primary focus. Second highest = secondary (if time allows and not same category). If top concept is grammar, prefer vocabulary or pronunciation as secondary (variety). Tie-break: prefer the concept with higher learner interest.

**Step 5 — Route to Activity**

On fluency days (1x/week in Phase B, 2x/week in Phase C, every session in Phase D): run Steps 1-4 normally to select concept(s). At Step 5, route to `fluency-activities.md` instead of the stage-based activity routing below.

For non-fluency days, check `error_rate_drills` and `error_rate_production`:

| Drills | Production | Route |
|--------|-----------|-------|
| Both high | → | Stage 2 (controlled practice from concept file) |
| Drills low, production high | → | Stage 3-4 (communicative practice) |
| Both low | → | Spot-check via conversation, move to secondary |
| Integration untested | → | Combined exercise with another acquired concept |

New concept introduction: only if 2 or fewer concepts in "practicing" status (3 or fewer with carryover). Route to Stage 1 (noticing) from concept file.

**Step 6 — Weekly Topic Selection** (during weekly review)

Score each candidate from `topic-bank.yaml`:

| Factor | Range | Description |
|--------|-------|-------------|
| GRAMMAR_FIT | 0-5 | Does the topic naturally elicit the current primary grammar concept? (5=perfect, 3=partial, 0=none) |
| VOCABULARY_FIT | 0-5 | Does the topic align with the active or upcoming vocabulary cluster? |
| LEARNER_INTEREST | 0-3 | Does the topic connect to known interests, goals, or real-world situations? |
| FRESHNESS | 0-3 | How recently was this topic used? (3=never, 2=4+ weeks, 1=2-3 weeks, 0=last week — exclude) |

`TOPIC_SCORE = GRAMMAR_FIT + VOCABULARY_FIT + LEARNER_INTEREST + FRESHNESS`

Select highest-scoring topic. Tie-break: prefer higher LEARNER_INTEREST.

Sprint override: if `sprint.active` is true, topic = sprint scenario theme. Skip scoring.

**Quick Reference — Common Scenarios:**

- "Learner is stuck on ser/estar for 4 sessions": GAP=8, DECAY=0, NEED=10 → score 18. Top priority. Route: different Stage 2 approach.
- "Haven't practiced preterite in 10 days but it was acquired": GAP=0, DECAY=7, NEED=1 → score 8. Maintenance check. Spot-check in conversation.
- "New concept ready to introduce": NEED=10, GAP=10, DECAY=0 → score 20. Highest possible. Route: Stage 1 (noticing).
- "Post-return regression on gender agreement": GAP=10, DECAY=9, NEED=7 → score 26. Urgent. Dedicated recovery session.
- "Parking lot: learner asked about conditional": If C-04-conditional prerequisites met, boost by +3 and consider as primary.

---

## Section 3: Consistency Fixes

### 3.1 Fluency Activities Phase Conflict

**Problem:** `fluency-activities.md` loaded at "Phase C+" but references "start with 1 minute in Phase B."

**Solution:** Change CLAUDE.md loading condition from "Phase C+ and today includes fluency work" to "Phase B+ and today is a fluency day." Update fluency-activities.md with phase-specific guidance:

- **Phase B:** 1x/week. Timed monologue only (1 min). Accuracy still primary — fluency work is exposure, not expectation. Don't track metrics yet.
- **Phase C:** 2x/week. Full activity set unlocked. Begin tracking fluency metrics. Balanced correction.
- **Phase D:** Every session includes a fluency component. Metrics are primary assessment tool. Correct only meaning-impeding errors.

**Typed vs. oral fluency distinction:** The tutor operates via text. "Timed monologue" in Claude Code is timed writing. Typed production speed is a valid fluency proxy. True oral fluency is delegated to external tools (Speechling, conversation partners). The tutor tracks:
- Typed production fluency: directly observed and measured
- Oral fluency: via external tool feedback and learner self-reports

Fluency metrics in skill-map should note data source (e.g., `"moderate (per italki partner feedback 2026-04-15)"` vs. `"moderate (estimated from typed production)"`).

### 3.2 Error Correction Mode by Activity Type

**Problem:** CLAUDE.md says "prefer recasting, max 3 corrections." L1-interference-protocol.md says "drill the contrast explicitly." These apply to different activity stages but the boundary is unstated.

**Solution:** Add Correction Mode by Activity table to CLAUDE.md. Correction mode follows activity type, not a single global rule.

| Activity Stage | Correction Mode | Details |
|---------------|----------------|---------|
| Stage 1-2 (controlled practice) | Explicit, immediate | No limit. Correction is part of the drill. L1 interference protocol applies here. |
| Stage 3 (guided production) | Recast, immediate | No hard limit. Correction is part of the scaffolding. |
| Stage 4 (free conversation) | Recast, batched | Max 3 corrections. Prefer recasting. Batch the rest for end-of-segment review. |
| Fluency activities | Zero in-the-moment | Batch everything for post-activity review. Never interrupt timed activities. |

### 3.3 Archive Location

**Problem:** `weekly-review-guide.md` references `state/sessions/archive/` but the directory doesn't exist.

**Solution:**
- Create `state/sessions/archive/` directory
- Archive sessions older than 60 days (provides buffer for monthly reviews and regression analysis)
- Archive = move files, don't delete. Archived sessions accessible but not loaded at startup.
- Tutor's startup protocol already limits to "3 most recent" — archive adds no cognitive load.
- Update CLAUDE.md state updates: "During weekly review, archive session logs older than 60 days to `state/sessions/archive/`"

### 3.4 Weekly Review During Onboarding

**Problem:** Weekly review guide assumes the decision engine is active and weekly topics exist. Neither is true during onboarding (sessions 2-10).

**Solution:** Add simplified onboarding review protocol to `onboarding-guide.md`.

If learner's `weekly_review_day` falls during onboarding, run a simplified review:
1. Progress check: "Here's what we've covered so far" (list concepts introduced and their status)
2. Homework review: completion rate, difficulty feedback
3. Tool check: is Anki working? Any setup issues?
4. Quick wins: highlight 2-3 specific things they can do now that they couldn't before
5. Motivation check: "How's it feeling so far?"

**Skip:** narrow topic selection, decision engine references, skill-map audit (too early), system health review, resource rotation.

Write an abbreviated weekly summary noting it's an onboarding review. First full weekly review happens the first review day after `onboarding_complete = true`.

### 3.5 Vocabulary ID Format

**Problem:** Skill-map uses `tier1-greetings-introductions` but vocabulary files live at `vocabulary/tier1-survival/greetings-introductions.md`. Tier naming differs.

**Solution:** Keep current skill-map key format. Document the tier-to-directory mapping (1:1 relationship):

| Key prefix | Directory |
|-----------|-----------|
| tier1-* | curriculum/vocabulary/tier1-survival/ |
| tier2-* | curriculum/vocabulary/tier2-daily-life/ |
| tier3-* | curriculum/vocabulary/tier3-social/ |
| tier4-* | curriculum/vocabulary/tier4-abstract/ |

The vault auto-generator uses this mapping. No renaming of 22 keys needed.

---

## Section 4: Specification Gaps

### 4.1 Quantitative Fluency Benchmarks

**Problem:** Fluency metrics are qualitative only. The tutor can't objectively track progress.

**Solution:** Add reference benchmarks to `fluency-activities.md`. Distinguish oral (external-measured) from typed (tutor-measured).

**Oral fluency benchmarks** (reference for learner self-assessment and external tool feedback — tutor cannot measure directly):

| Metric | Phase C | Phase D |
|--------|---------|---------|
| Pace (WPM) | 60-80 developing, 80-100 on track | 100-120 developing, 120+ natural-flow |
| Hesitation (pauses >2s per min) | 6+ frequent, 3-5 occasional, 0-2 rare | 3+ frequent, 1-2 occasional, 0 rare |
| Native reference | 120-180 WPM varies by dialect/context | |

**Typed production benchmarks** (tutor-measurable):

| Phase | Benchmark |
|-------|-----------|
| B | Can produce 3-4 simple sentences in 2 minutes |
| C | Can produce a coherent paragraph in 2 minutes |
| D | Can sustain multi-paragraph response with complex structures in 3 minutes |

**Self-correction rate:** High = good (shows monitoring). Track trend, not absolute value. Declining self-correction + stable accuracy = automaticity emerging. Declining self-correction + declining accuracy = losing awareness — flag.

**Important:** These are reference benchmarks, not pass/fail criteria. Learners vary enormously. Always weight accuracy appropriately for the current phase's fluency-accuracy balance. The tutor estimates from conversation — qualitative assessment backed by quantitative reference.

### 4.2 Homework Time Estimation

**Problem:** The tutor assigns homework constrained by available time but has no per-task estimates.

**Solution:** Add reference table to system-design.md.

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

```
available_minutes = learner_profile.typical_weekday_minutes - average_session_duration

If available_minutes < 15: assign Anki only
If available_minutes 15-30: Anki + one task
If available_minutes 30-45: Anki + two tasks
If available_minutes > 45: Anki + two tasks + journal or stretch
```

**External learning load:** Conversation partner sessions and self-directed study count toward total learning load awareness but not the homework assignment budget. If learner has regular external sessions, reduce assigned homework proportionally to keep total daily learning under stated capacity.

Always log `estimated_minutes` per assignment in session log. Track actual vs estimated via learner feedback to calibrate over time.

### 4.3 Caribbean & Central American Dialect Expansion

**Problem:** `dialect-notes.yaml` covers Mexican, Castilian, Argentine, Colombian. Caribbean and Central American are underdeveloped.

**Solution:** Expand dialect-notes.yaml.

**Caribbean (Cuba, Dominican Republic, Puerto Rico):**
- Pronunciation: final 's' aspiration or deletion, liquid consonant neutralization (r/l), rapid speech tempo
- Vocabulary: guagua (bus), china (orange, PR), boricua/dominicano identity terms
- Grammar: subject pronoun use more frequent, inverted questions (¿Qué tú quieres?)
- Introduction: Phase B (awareness), Phase C (recognition), Phase D (production)

**Central American (Guatemala, Honduras, El Salvador, Costa Rica):**
- Pronunciation: generally conservative, clear 's', Costa Rican strong 'r'
- Vocabulary: vos usage varies by country, puchica (exclamation), cipote (kid, Honduras), mae (dude, Costa Rica), cabal (exactly, Guatemala)
- Grammar: voseo conjugation differs from Argentine, ustedeo in Costa Rica/Colombia
- Introduction: Phase B (awareness), Phase C (recognition)

**Scope:** These are awareness entries. The learner's target dialect (from learner-profile.yaml) determines primary instruction. Other dialects introduced for recognition, not production, unless learner specifically requests it.

### 4.4 Writing Track Rubric

**Problem:** Skill-map tracks 4 writing dimensions but no evaluation criteria exist.

**Solution:** Add rubric to system-design.md or as new reference in tutor-guides.

**Sentence Construction:**
- Introduced: Can write simple SVO sentences with present tense
- Practicing: Attempts compound sentences, some errors in agreement/word order
- Acquired: Consistently produces grammatically correct compound sentences with appropriate connectors
- Signs of acquisition: subordinate clauses, relative clauses used naturally

**Paragraph Coherence:**
- Introduced: Writes connected sentences on a single topic
- Practicing: Attempts topic sentences and transitions, inconsistent flow
- Acquired: Paragraphs have clear structure, logical flow, appropriate transitions (primero, luego, además, sin embargo)
- Signs of acquisition: reader can follow argument without re-reading

**Formal Register:**
- Introduced: Aware of tú/usted distinction in writing
- Practicing: Attempts formal constructions, inconsistent
- Acquired: Can write a formal email, complaint, or request with appropriate register throughout
- Signs of acquisition: subjunctive in formal requests, indirect constructions

**Creative Expression:**
- Introduced: Writes beyond literal description (metaphor, humor, opinion)
- Practicing: Attempts creative devices, sometimes awkward
- Acquired: Voice is emerging — writing has personality, not just accuracy
- Signs of acquisition: reader engagement, idiomatic expression, risk-taking

**Evaluation method:** Journal entries are the primary data source. Structured writing exercises (from activities templates) for targeted practice. Tutor reviews 2-3 corrections per entry. Quality notes in session log track which dimension showed progress. Formal assessment: compare a journal entry from 4 weeks ago to the current week's entry (read older entries during weekly reviews). Dimensions progress independently — this is expected.

### 4.5 Dead File Removal

**Problem:** `docs/claude-md-draft.md` (563 lines) is an alternate CLAUDE.md version with unclear status.

**Solution:** Delete `docs/claude-md-draft.md` after verifying no unique content needs to be preserved. CLAUDE.md is the authoritative tutor prompt. Any valuable content not in current CLAUDE.md should be evaluated and merged before deletion.

### 4.6 Narrow Topic Selection

Covered in Section 2.3 (Decision Engine Guide, Step 6). Included here for completeness as it was originally audit item #12.

---

# Phase 2: Obsidian Vault

## Architecture

**Obsidian vault scope = repo root.** Obsidian points at the project directory. Generated content lives in `vault/` subdirectory. Existing files (`journal/`, `parking-lot.md`) stay at their current locations — Obsidian sees them natively.

**Excluded from Obsidian file explorer** (configured in `.obsidian/app.json`): `state/`, `curriculum/`, `docs/`, `.git/`, `.superpowers/`, `.planning/`, `resources/`, `progress-reports/`. The learner sees: `vault/`, `journal/`, `parking-lot.md`.

**Everything is committed to git.** The vault is the learner's interface and historical record. Vault updates are part of the post-session commit.

## Directory Structure

```
/ (repo root = Obsidian vault)
│
├── .obsidian/                        Vault config (committed)
│   ├── app.json                      Homepage, excluded folders, appearance
│   ├── graph.json                    Node colors by status tag
│   └── plugins/
│       ├── dataview/
│       ├── calendar/
│       ├── templater/
│       └── homepage/
│
├── journal/                          Learner-editable (unchanged location)
│   └── YYYY-MM-DD.md                Templater provides entry template
│
├── parking-lot.md                    Learner-editable (unchanged location)
│
└── vault/                            All generated content (committed)
    ├── Home.md                       Dashboard landing page
    ├── Roadmap.md                    Phase overview + dependency tree
    ├── Getting Started.md            First-time setup guide
    │
    ├── Daily/                        One note per session day
    │   ├── YYYY-MM-DD.md            (auto-generated from session logs)
    │   └── Archive/                  Older than 60 days
    │
    ├── Grammar/                      Curriculum reference
    │   ├── Phase A - Foundation/     (generated from curriculum/grammar/)
    │   │   ├── Communication Repair.md
    │   │   ├── Present Regular.md
    │   │   └── ...
    │   ├── Phase B - Conversational/
    │   ├── Phase C - Intermediate/
    │   └── Phase D - Advanced/
    │
    ├── Vocabulary/                   Vocabulary reference
    │   ├── Tier 1 - Survival/       (generated from curriculum/vocabulary/)
    │   ├── Tier 2 - Daily Life/
    │   ├── Tier 3 - Social/
    │   └── Tier 4 - Abstract/
    │
    ├── Pronunciation/                Pronunciation guides
    │                                 (generated from curriculum/pronunciation/)
    │
    ├── Progress/                     Dashboards (Dataview-powered)
    │   ├── Grammar Progress.md
    │   ├── Vocabulary Progress.md
    │   ├── Weekly Reports.md
    │   └── Milestones.md
    │
    └── Templates/                    Obsidian templates
        ├── Journal Entry.md
        └── Daily Note.md
```

## Generated vs. Editable Convention

**Generated files** (everything in `vault/`):
- Frontmatter includes `generated: true`, `source: "<path>"`, `last_generated: "YYYY-MM-DD"`
- Body includes (line 1 after frontmatter): `%%Auto-generated from tutor state. Edits will be overwritten.%%`
- Generator ONLY overwrites files where `generated: true`
- If a file is missing the flag, generator skips it (safety)

**Editable files** (`journal/`, `parking-lot.md`):
- No `generated` flag, or `generated: false`
- Generator never touches these

**Personal notes** (learner can create anywhere in vault):
- Won't have `generated: true`, so generator won't overwrite them
- Learner's custom notes are safe by default

## Frontmatter Specifications

**Grammar note:**
```yaml
---
generated: true
source: curriculum/grammar/A-foundation/01-present-regular.md
last_generated: 2026-04-06
concept_id: A-01-present-regular
title: Present Tense - Regular Verbs
phase: A
status: practicing
error_rate_drills: 0.12
error_rate_production: 0.23
error_trend: improving
last_practiced: 2026-04-05
practice_count: 7
integration_tested: false
prerequisites:
  - "[[Communication Repair]]"
tags:
  - grammar
  - phase-a
  - practicing
---
```

**Vocabulary note:**
```yaml
---
generated: true
source: curriculum/vocabulary/tier1-survival/food-restaurant.md
last_generated: 2026-04-06
cluster_id: tier1-food-restaurant
title: Food and Restaurant
tier: 1
category: survival
status: practicing
words_total: 45
words_introduced: 28
passive_known: 22
active_known: 15
last_practiced: 2026-04-04
tags:
  - vocabulary
  - tier-1
  - survival
  - practicing
---
```

**Daily note:**
```yaml
---
generated: true
source: state/sessions/2026-04-06.yaml
last_generated: 2026-04-06
date: 2026-04-06
session_number: 12
session_type: standard
duration_minutes: 35
concepts_practiced:
  - "[[Ser vs Estar]]"
  - "[[Food and Restaurant]]"
homework_complete: false
tags:
  - daily
  - session
---
```

**Journal entry template** (Templater):
```yaml
---
date: {{date}}
prompt: ""
generated: false
tags:
  - journal
---
```

Templater auto-fills date. Prompt pulled from most recent daily note's homework section.

## Home.md Dashboard

Sections (powered by Dataview queries against frontmatter):

1. **Right Now** — current streak, session count, phase + progress fraction (e.g., "Phase A: 5/8 concepts acquired"), this week's topic
2. **Today's Homework** — Dataview query pulls homework checklist from most recent Daily note (inherits learner's checkbox state, since checkboxes live in the daily note, not Home.md)
3. **Active Concepts** — table: concept name (wiki-link), status, drill accuracy, production accuracy, trend. Dataview query: grammar/vocabulary WHERE status != "unseen" AND status != "automatic"
4. **Recent Milestones** — last 3, from Progress/Milestones.md
5. **Quick Links** — Roadmap, Parking Lot, Journal, Progress

## Roadmap.md

**Header:** Current phase, days in phase, overall CEFR estimate.

**Per phase (A through D):**
- Phase title + description + estimated duration
- Concept list with status indicators: ○ unseen, ◐ introduced, ◑ practicing, ● acquired, ★ automatic
- Prerequisite dependency tree rendered as Mermaid flowchart (Obsidian supports Mermaid natively, no plugin needed)
- Phase transition requirements summary
- Progress bar: `Phase A: ●●●●◑◑○○ (5/8)`

**Display rules:**
- Current phase: expanded with full detail
- Future phases: collapsed (titles + concept count only)
- Past phases: show completion date and "all acquired" status

**Footer:** Estimated timeline to next phase transition (based on current acquisition rate from system-health.yaml).

## Graph View Configuration

**Node colors by tag** (configured in `.obsidian/graph.json`):

| Tag | Color | Meaning |
|-----|-------|---------|
| #unseen | Gray (dim) | Not yet introduced |
| #introduced | Blue | Seen once |
| #practicing | Amber/yellow | Actively working on |
| #acquired | Green | Consistent performance |
| #automatic | Green (bright) | Used without thinking |
| #regressed | Red | Errors resurfaced |

**Node sizing:** grammar = larger nodes, vocabulary = smaller nodes.

**Excluded from default graph view:** #daily (session notes would clutter the curriculum graph).

**Saved graph presets:**
- "Grammar Map" — filter: tag:#grammar
- "Full Curriculum" — filter: tag:#grammar OR tag:#vocabulary
- "Active Only" — filter: tag:#practicing OR tag:#introduced
- "My Progress" — filter: -tag:#unseen -tag:#daily

The dependency tree emerges naturally from `[[prerequisite]]` wiki-links. Gray nodes (future) → colored nodes (current) → green nodes (mastered).

## Plugin Configuration

Pre-configured in `.obsidian/` (committed to repo). Learner installs plugins manually on first setup per `vault/Getting Started.md`.

**Dataview (required):**
- Powers all dashboards and filtered views
- JavaScript queries disabled (YAML-only, safe)
- Refresh interval: on file change

**Homepage (required):**
- Opens `vault/Home.md` on vault launch
- Mode: replace existing tab

**Calendar (recommended):**
- Shows session days in sidebar calendar
- Daily notes folder: `vault/Daily`
- Date format: `YYYY-MM-DD` (matches daily note filenames)
- Click a day → opens that session's daily note
- If learner clicks a non-session day, Calendar may create an empty note — this is acceptable (learner can use it for personal notes; no `generated: true` flag means generator won't touch it)

**Templater (recommended):**
- Template folder: `vault/Templates`
- Journal Entry template: auto-fills date + prompt
- Trigger: new file in `journal/` folder

## Getting Started Guide

`vault/Getting Started.md` — included in initial vault generation. Contains:
1. Install Obsidian (link to download)
2. Open this project folder as a vault
3. Trust community plugins when prompted
4. Install required plugins: Dataview, Homepage
5. Install recommended plugins: Calendar, Templater
6. Vault is ready — Home.md opens automatically
7. Brief orientation: where to find homework, journal, grammar reference, progress

## Auto-Generation: Two Modes

### Generation Script (bulk / initial setup)

**When:** First session setup, curriculum file changes.

**What it generates:**
- All Grammar/ notes from curriculum/grammar/ (34 files)
- All Vocabulary/ notes from curriculum/vocabulary/ (22 files)
- All Pronunciation/ notes from curriculum/pronunciation/ (12 files)
- Roadmap.md from skill-map prerequisites
- Home.md template with Dataview queries
- Progress/ dashboard templates with Dataview queries
- Getting Started.md
- Templates/ for Templater
- .obsidian/ config with plugin settings

**Implementation:** Script in `scripts/` directory. Reads YAML state files + curriculum markdown, writes vault markdown with frontmatter. Idempotent — safe to re-run. Only overwrites files with `generated: true`.

### Tutor Direct (per-session)

**When:** After every session, as part of state update protocol.

**What it updates:**
- Generate/update today's Daily/ note from session log (homework as checkboxes, links to concepts practiced, journal prompt)
- Update frontmatter status fields on Grammar/ and Vocabulary/ notes that changed this session
- Update tags on changed notes (status tag reflects new status)
- Update Roadmap.md if phase or concept status changed
- Append to Progress/Weekly Reports.md during weekly review
- Create milestone entry in Progress/Milestones.md when milestone recorded

**Scope:** Lightweight — typically 3-6 file updates. Added to existing post-session commit.

### First Session Vault Setup

Added to `first-session.md` after Step 7 (State Initialization):

**Step 8 — Vault Setup:**
1. Run generation script (creates all vault/ content from curriculum + initial state)
2. Instruct learner: "I've set up your study companion. Open Obsidian, point it at this project folder, and install the community plugins listed in vault/Getting Started.md."
3. Commit vault/ alongside initial state files
4. First session daily note generated as part of normal post-session vault update

### Vault Recovery

If generation produces bad output or a learner accidentally edits a generated file:
- Re-run the generation script. It's idempotent and only overwrites `generated: true` files.
- Learner's journal, parking lot, and personal notes are untouched.
- If state/ YAML is corrupt, fix state first (error-recovery.md), then regenerate vault.
- Git history provides additional safety net: `git checkout vault/` restores last committed state.

---

# CLAUDE.md Changes Required

All behavioral changes from this spec must be reflected in CLAUDE.md:

1. **Session Startup Protocol:** Add vault existence check — if `vault/` doesn't exist, note for first-session setup
2. **Step 3 routing table:** Add condition for "Phase B+ fluency day" → load `fluency-activities.md`
3. **Step 3 routing table:** Update "Gap of 3+ days" row to load `curriculum/tutor-guides/return-session.md` instead of inline handling
4. **Step 4 conditional loads:** Update fluency condition from "Phase C+" to "Phase B+ and today is a fluency day"
5. **Step 4 conditional loads:** Add "Standard session (post-onboarding)" → load `curriculum/tutor-guides/decision-engine.md`
6. **Step 4 conditional loads:** Add "All prerequisites for next phase show 'acquired' for 2+ consecutive sessions" → load `curriculum/tutor-guides/phase-transition-guide.md`
7. **New section:** Correction Mode by Activity table (Stage 1-2 explicit, Stage 3 recast, Stage 4 batched max-3, Fluency zero-correction)
8. **State Updates:** Add step — vault generation (generate/update daily note, update frontmatter on changed concept notes, update Roadmap if status changed)
9. **State Updates:** Add step — include `vault/` files in session commit
10. **State Updates:** Add "During weekly review, archive session logs older than 60 days to `state/sessions/archive/`"
11. **Guardrails:** Add "Never overwrite vault files without `generated: true` frontmatter flag"
12. **Guardrails:** Add "On fluency days, still run decision engine for concept selection — skip activity routing only"
13. **First session guide reference:** Note vault setup as Step 8

# system-design.md Changes Required

1. Replace phase-completion schema with unified milestone schema (Section 1.1)
2. Update skill-map grammar schema: `error_rate_recent` → `error_rate_drills` + `error_rate_production` with rolling 5-session window, minimum 3 samples (Section 1.3)
3. Add homework time estimation table with budget calculation and external load awareness (Section 4.2)
4. Add phase transition assessment format with production + receptive tasks, pass/borderline criteria, framing guidance (Section 1.4)
5. Update decision engine section: GAP uses production rate, add weekly topic boost, add parking lot influence, add maintenance decay by phase distance, add fluency day routing (Section 2.3)
6. Add narrow topic selection scoring algorithm (Section 2.3, Step 6)
7. Add correction mode by activity type table (Section 3.2)
8. Add writing track evaluation rubric (Section 4.4)
9. Update session log schema: add `estimated_minutes` per homework assignment, add `gap_days` for return sessions (Sections 4.2, 2.1)
10. Add vault generation to post-session protocol (Phase 2)
11. Add typed vs. oral fluency distinction to fluency metrics section (Section 3.1)
12. Note: all schema changes designed for vault frontmatter compatibility
