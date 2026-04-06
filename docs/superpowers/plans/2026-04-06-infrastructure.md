# Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update all state schemas, operating instructions, and supporting files to match the design spec before building curriculum content.

**Architecture:** Modify 9 existing files and create 1 directory. The skill-map.yaml gets a near-complete rewrite (new concepts, renamed concepts, new fields on every grammar entry, new sections). Other files get targeted edits.

**Spec:** `docs/superpowers/specs/2026-04-06-curriculum-and-infrastructure-design.md`

---

## File Map

| File | Action | Scope |
|------|--------|-------|
| `state/skill-map.yaml` | Rewrite | Rename 2 concepts, add 6 new, replace `context_gap` with 3 fields on all 34 grammar entries, add `receptive_skills`, expand `cultural_awareness` |
| `state/schedule.yaml` | Modify | Add `carryover_concepts`, move Anki config from system-health |
| `state/system-health.yaml` | Modify | Remove Anki config fields (moved to schedule) |
| `CLAUDE.md` | Modify | Add validation checks, update consolidation path, add guardrails (~12 lines) |
| `curriculum/l1-interference.yaml` | Modify | Update 1 entry, add 5 new patterns |
| `curriculum/dialect-notes.yaml` | Modify | Add 3 new entries |
| `curriculum/topic-bank.yaml` | Modify | Add 5 new topics, update 3 existing alignment arrays |
| `curriculum/tutor-guides/onboarding-guide.md` | Modify | Update to reflect midpoint consolidation sequence |
| `docs/system-design.md` | Modify | Update schemas, decision engine, architecture, onboarding, progression tables, file formats |
| `curriculum/pronunciation/` | Create | New directory with `.gitkeep` |

---

### Task 1: Rewrite skill-map.yaml — Grammar Section

**Files:**
- Rewrite: `state/skill-map.yaml` (grammar section only — lines 1-312)

This is the largest single change. Every grammar entry gets `context_gap` replaced with three new fields. Two entries are renamed. Six new entries are added. One prerequisite chain is updated.

- [ ] **Step 1: Write the new grammar section of skill-map.yaml**

Replace lines 1-312 of `state/skill-map.yaml` with the following. All grammar entries use the new field structure: `performance_scaffolded`, `performance_unscaffolded`, `integration_tested` replace `context_gap`.

```yaml
# Skill Map — learner's current mastery state across all skill dimensions
# Updated every session. The single source of truth for what has been taught and how well it's retained.
# Schema defined in docs/system-design.md

# Status values:
#   unseen     — not yet introduced
#   introduced — seen once, not yet practiced
#   practicing — actively working on it, error rate > 15%
#   acquired   — consistent in drills AND free production, error rate < 10%
#   automatic  — used without thinking, only spot-checked periodically
#   regressed  — was acquired/automatic, but errors resurfaced
#
# Context performance values:
#   null       — untested in this context
#   struggling — frequent errors in this context
#   competent  — reliable performance in this context
#
# Acquisition requirement: status cannot be "acquired" unless
# performance_unscaffolded is "competent"

grammar:
  A-00-communication-repair:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: []
    notes: "FIRST concept — survival phrases for when learner is stuck"

  A-01-present-regular:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: []
    notes: "Includes hay (there is/there are) as key irregular form"

  A-02-ser-vs-estar:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular]
    notes: ""

  A-03-gender-agreement:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: []
    notes: "Expanded: includes demonstratives (este/ese/aquel) and unstressed possessives (mi/tu/su)"

  A-04-articles-prepositions:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-03-gender-agreement]
    notes: "Expanded: includes personal 'a' as dedicated section"

  A-05-basic-questions:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular]
    notes: ""

  A-06-gustar-type-verbs:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular]
    notes: "Reversed sentence structure: gustar, encantar, molestar, importar, interesar, doler"

  A-07-present-irregular-common:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular]
    notes: "ir, tener, querer, poder, hacer, decir, saber/conocer, hay"

  B-01-preterite-regular:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular]
    notes: ""

  B-02-preterite-irregular:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [B-01-preterite-regular]
    notes: ""

  B-03-imperfect:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular]
    notes: ""

  B-04-preterite-vs-imperfect:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [B-01-preterite-regular, B-02-preterite-irregular, B-03-imperfect]
    notes: ""

  B-05-reflexive-verbs:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular, B-01-preterite-regular]
    notes: ""

  B-06-direct-object-pronouns:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular, A-04-articles-prepositions]
    notes: "Prerequisite includes A-04 for personal 'a' knowledge"

  B-07-indirect-object-pronouns:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [B-06-direct-object-pronouns]
    notes: ""

  B-08-estar-gerund-progressive:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular, A-02-ser-vs-estar]
    notes: "Estar + gerund (-ando/-iendo). Reinforces estar usage."

  B-09-imperatives:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular, A-07-present-irregular-common]
    notes: "tu/usted commands. Irregular tu forms. Pronoun placement."

  B-10-comparatives-superlatives:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-03-gender-agreement]
    notes: "mas...que, menos...que, tan...como. Irregulars: mejor, peor, mayor, menor."

  B-11-future-ir-a:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular]
    notes: ""

  C-01-present-subjunctive:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular, A-07-present-irregular-common]
    notes: ""

  C-02-subjunctive-triggers:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [C-01-present-subjunctive]
    notes: ""

  C-03-formal-future:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-01-present-regular]
    notes: ""

  C-04-conditional:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [C-03-formal-future]
    notes: ""

  C-05-por-vs-para:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-04-articles-prepositions]
    notes: ""

  C-06-compound-tenses:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [B-01-preterite-regular]
    notes: ""

  C-07-relative-clauses:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [C-01-present-subjunctive]
    notes: ""

  C-08-indirect-speech:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [C-01-present-subjunctive, C-02-subjunctive-triggers, B-04-preterite-vs-imperfect]
    notes: "Me dijo que..., queria saber si... Requires subjunctive/indicative distinction."

  C-09-diminutives-augmentatives:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [A-03-gender-agreement]
    notes: "-ito/-ita, -ote/-ota. Essential for natural speech, especially Mexican Spanish."

  D-01-past-subjunctive:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [C-01-present-subjunctive, B-03-imperfect]
    notes: ""

  D-02-si-clauses:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [C-04-conditional, D-01-past-subjunctive]
    notes: ""

  D-03-subjunctive-all-tenses:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [D-01-past-subjunctive, C-06-compound-tenses]
    notes: ""

  D-04-passive-voice:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: [B-01-preterite-regular]
    notes: ""

  D-05-register-shifting:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: []
    notes: "Grammar forms for tu/usted/vos. Cultural judgment tracked separately in cultural_awareness."

  D-06-nuanced-connectors:
    status: unseen
    introduced_date: null
    last_practiced: null
    practice_count: 0
    error_rate_recent: null
    error_trend: null
    performance_scaffolded: null
    performance_unscaffolded: null
    integration_tested: false
    prerequisites: []
    notes: ""
```

- [ ] **Step 2: Verify grammar section**

Run: `python3 -c "import yaml; yaml.safe_load(open('state/skill-map.yaml')); print('YAML valid')"` from project root.

Check: 34 grammar entries total (A: 8, B: 11, C: 9, D: 6). No entry has `context_gap`. All entries have `performance_scaffolded`, `performance_unscaffolded`, `integration_tested`. C-01 prerequisites reference `A-07-present-irregular-common` (not A-06). B-06 prerequisites include `A-04-articles-prepositions`.

- [ ] **Step 3: Commit**

```
git add state/skill-map.yaml
git commit -m "refactor: update skill-map grammar section — new concepts, context performance fields"
```

---

### Task 2: Rewrite skill-map.yaml — Remaining Sections

**Files:**
- Rewrite: `state/skill-map.yaml` (vocabulary, pronunciation, writing, cultural_awareness, fluency, overall sections + add receptive_skills)

The vocabulary, pronunciation, writing, and fluency sections are unchanged. Cultural awareness gets expanded fields. Receptive skills is a new section inserted after writing.

- [ ] **Step 1: Verify vocabulary/pronunciation/writing/fluency sections are unchanged**

These sections (lines 314-688 in the original) remain exactly as they are. Only `cultural_awareness` changes and `receptive_skills` is added.

- [ ] **Step 2: Replace the cultural_awareness section**

Replace the existing `cultural_awareness` block with:

```yaml
cultural_awareness:
  register_shifting:
    status: unseen
    introduced_at_phase: D
    assessed_through: "conversation behavior, role-play scenarios"
    signs_of_acquisition: "Shifts registers appropriately without prompting in role-play"
    notes: "Pragmatic judgment (when to shift). Grammar forms tracked in D-05-register-shifting."

  politeness_formulas:
    status: unseen
    introduced_at_phase: B
    assessed_through: "request formulation, disagreement handling in conversation"
    signs_of_acquisition: "Softens requests and disagreements naturally without prompting"
    notes: ""

  conversational_rhythm:
    status: unseen
    introduced_at_phase: C
    assessed_through: "conversation flow, back-channeling, turn-taking"
    signs_of_acquisition: "Natural turn-taking, appropriate back-channeling (ah si, claro, ya)"
    notes: ""

  regional_awareness:
    status: unseen
    introduced_at_phase: B
    assessed_through: "recognition of dialect differences, adaptation in conversation"
    signs_of_acquisition: "Recognizes dialect variants and adapts vocabulary to context"
    notes: ""

  humor_and_idioms:
    status: unseen
    introduced_at_phase: C
    assessed_through: "comprehension and use of idioms, humor response"
    signs_of_acquisition: "Uses common idioms naturally, understands humor in context"
    notes: ""
```

- [ ] **Step 3: Add receptive_skills section after writing and before cultural_awareness**

Insert after the `writing` section and before `cultural_awareness`:

```yaml
receptive_skills:
  listening:
    current_level: null
    comprehension_quality: null
    speed_tolerance: null
    last_level_change: null
    notes: ""

  reading:
    current_level: null
    comprehension_quality: null
    lookup_frequency: null
    last_level_change: null
    notes: ""
```

- [ ] **Step 4: Verify complete file**

Run: `python3 -c "import yaml; data=yaml.safe_load(open('state/skill-map.yaml')); print('Sections:', list(data.keys()))"` from project root.

Expected sections: `grammar`, `vocabulary`, `pronunciation`, `writing`, `receptive_skills`, `cultural_awareness`, `fluency_metrics`, `overall_estimates`

- [ ] **Step 5: Commit**

```
git add state/skill-map.yaml
git commit -m "refactor: update skill-map — receptive skills, cultural awareness, context performance"
```

---

### Task 3: Update schedule.yaml and system-health.yaml

**Files:**
- Modify: `state/schedule.yaml`
- Modify: `state/system-health.yaml`

- [ ] **Step 1: Add carryover_concepts and Anki config to schedule.yaml**

After the `sprint` block and before `adjustment_log`, add:

```yaml
carryover_concepts: []  # concepts from prior phase still in active practice

# SRS configuration (moved from system-health.yaml)
anki_new_cards_per_session: 8
anki_retirement_threshold_days: 60
```

- [ ] **Step 2: Remove Anki config from system-health.yaml**

Remove these three lines from `state/system-health.yaml`:

```yaml
anki_new_cards_per_session: 8
anki_retirement_threshold_days: 60
anki_last_deck_audit: null
```

Keep `anki_estimated_deck_size` and `anki_estimated_daily_review_minutes` — these are metrics, not config.

- [ ] **Step 3: Verify both files parse**

Run: `python3 -c "import yaml; yaml.safe_load(open('state/schedule.yaml')); yaml.safe_load(open('state/system-health.yaml')); print('Both valid')"` from project root.

- [ ] **Step 4: Commit**

```
git add state/schedule.yaml state/system-health.yaml
git commit -m "refactor: move Anki config to schedule, add carryover_concepts"
```

---

### Task 4: Update l1-interference.yaml

**Files:**
- Modify: `curriculum/l1-interference.yaml`

- [ ] **Step 1: Update gustar-construction preempt_at**

Change:
```yaml
    preempt_at: A-06-present-irregular-common
```
To:
```yaml
    preempt_at: A-06-gustar-type-verbs
```

- [ ] **Step 2: Add 5 new interference patterns**

Append before the closing of the `interference_patterns` list:

```yaml
  - id: progressive-overuse
    english_cause: "English overuses progressive for habitual actions"
    common_errors:
      - wrong: "Estoy comiendo mucho" (for habitual)
        right: "Como mucho" (present simple for habits)
        explanation: "Spanish progressive is for actions happening right now, not habitual actions"
    preempt_at: B-08-estar-gerund-progressive
    severity: medium
    persistence: "Moderate — resolves with exposure to natural Spanish input"

  - id: imperative-pronoun-placement
    english_cause: "English always puts pronouns before verbs"
    common_errors:
      - wrong: "Me di" (pronoun before affirmative command)
        right: "Dime" (pronoun attaches to affirmative command)
      - wrong: "No dime" (pronoun attached to negative command)
        right: "No me digas" (pronoun precedes negative command)
        explanation: "Affirmative commands: pronoun attaches. Negative commands: pronoun precedes."
    preempt_at: B-09-imperatives
    severity: medium
    persistence: "Takes several weeks of practice to automatize"

  - id: comparative-de-vs-que
    english_cause: "English uses 'than' for all comparisons"
    common_errors:
      - wrong: "Mas que cinco personas"
        right: "Mas de cinco personas"
        explanation: "Use 'de' before numbers, 'que' before nouns/clauses"
    preempt_at: B-10-comparatives-superlatives
    severity: low
    persistence: "Corrects quickly once the rule is explained"

  - id: indirect-speech-subjunctive
    english_cause: "English rarely changes mood in reported speech"
    common_errors:
      - wrong: "Me dijo que viene manana"
        right: "Me dijo que viniera manana"
        explanation: "Reported requests/desires require subjunctive in Spanish"
    preempt_at: C-08-indirect-speech
    severity: medium
    persistence: "Persistent — tied to broader subjunctive acquisition"

  - id: diminutive-underuse
    english_cause: "English has no productive diminutive morphology"
    common_errors:
      - observation: "Learner never uses -ito/-ita forms in casual speech"
        impact: "Sounds overly formal or distant, especially in Mexican Spanish"
        guidance: "Encourage use in affectionate and casual contexts"
    preempt_at: C-09-diminutives-augmentatives
    severity: low
    persistence: "Resolves with exposure and encouragement to try"
```

- [ ] **Step 3: Verify YAML parses**

Run: `python3 -c "import yaml; data=yaml.safe_load(open('curriculum/l1-interference.yaml')); print(len(data['interference_patterns']), 'patterns')"` from project root.

Expected: `15 patterns` (was 10, added 5)

- [ ] **Step 4: Commit**

```
git add curriculum/l1-interference.yaml
git commit -m "feat: update L1 interference — gustar preempt_at fix, 5 new patterns"
```

---

### Task 5: Update dialect-notes.yaml

**Files:**
- Modify: `curriculum/dialect-notes.yaml`

- [ ] **Step 1: Add grammar differences**

Append to the `grammar_differences` list:

```yaml
  - feature: "voseo imperatives"
    regions: [argentina, uruguay, parts of central america]
    introduce_at: Phase C
    description: "Vos imperative forms differ: habla (vos), come (vos), vivi (vos)"
    notes: "Teach alongside B-09 imperatives for recognition, production in Phase C for target dialects"

  - feature: "progressive frequency"
    regions_higher: [caribbean, coastal]
    regions_lower: [highland, mexican standard]
    introduce_at: Phase B
    description: "Caribbean Spanish uses progressive more frequently for ongoing states"
    notes: "Awareness only — don't overuse progressive regardless of dialect"
```

- [ ] **Step 2: Add vocabulary difference**

Append to the `vocabulary_differences` list:

```yaml
  - context: "diminutive suffix"
    mexican: "-ito/-ita (standard)"
    castilian: "-ito/-ita or -illo/-illa"
    argentinian: "-ito/-ita"
    colombian: "-ito/-ita or -ico/-ica"
    notes: "Regional diminutive preferences. Teach target dialect form first."
```

- [ ] **Step 3: Verify and commit**

Run: `python3 -c "import yaml; yaml.safe_load(open('curriculum/dialect-notes.yaml')); print('Valid')"` from project root.

```
git add curriculum/dialect-notes.yaml
git commit -m "feat: add voseo imperatives, progressive frequency, diminutive variation to dialect notes"
```

---

### Task 6: Update topic-bank.yaml

**Files:**
- Modify: `curriculum/topic-bank.yaml`

- [ ] **Step 1: Add 5 new topics**

Append to the `topics` list, after the existing Phase D topics:

```yaml
  # New topics for added concepts
  - name: "Giving directions"
    grammar_alignment: [B-09-imperatives]
    vocabulary_alignment: [tier1-directions-transportation]
    cefr_range: [A2, B1]
    tags: [practical, travel, commands]

  - name: "Comparing cities and countries"
    grammar_alignment: [B-10-comparatives-superlatives]
    vocabulary_alignment: [tier3-travel-culture]
    cefr_range: [A2, B1]
    tags: [travel, descriptions, opinions]

  - name: "What are you doing right now?"
    grammar_alignment: [B-08-estar-gerund-progressive]
    vocabulary_alignment: [tier2-home-household]
    cefr_range: [A2, B1]
    tags: [daily-life, present-moment]

  - name: "Retelling a friend's story"
    grammar_alignment: [C-08-indirect-speech]
    vocabulary_alignment: [tier3-storytelling-narration]
    cefr_range: [B1, B2]
    tags: [storytelling, narrative, social]

  - name: "Terms of endearment and affection"
    grammar_alignment: [C-09-diminutives-augmentatives]
    vocabulary_alignment: [tier2-family-relationships]
    cefr_range: [B1, B2]
    tags: [family, culture, informal]
```

- [ ] **Step 2: Update existing topic alignments**

In "Food and eating out", change:
```yaml
    grammar_alignment: [A-01-present-regular, A-06-present-irregular-common]
```
to:
```yaml
    grammar_alignment: [A-01-present-regular, A-07-present-irregular-common]
```

In "Shopping and money", change:
```yaml
    grammar_alignment: [B-06-direct-object-pronouns, A-06-present-irregular-common]
```
to:
```yaml
    grammar_alignment: [B-06-direct-object-pronouns, A-07-present-irregular-common]
```

In "Work and career", change:
```yaml
    grammar_alignment: [B-01-preterite-regular, B-08-future-ir-a]
```
to:
```yaml
    grammar_alignment: [B-01-preterite-regular, B-11-future-ir-a]
```

In "Weekend plans and activities", change:
```yaml
    grammar_alignment: [B-08-future-ir-a, B-01-preterite-regular]
```
to:
```yaml
    grammar_alignment: [B-11-future-ir-a, B-01-preterite-regular]
```

- [ ] **Step 3: Verify and commit**

Run: `python3 -c "import yaml; data=yaml.safe_load(open('curriculum/topic-bank.yaml')); print(len(data['topics']), 'topics')"` from project root.

Expected: `25 topics` (was 20, added 5)

```
git add curriculum/topic-bank.yaml
git commit -m "feat: add 5 new topics, update concept ID references in topic bank"
```

---

### Task 7: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add validation checks to Step 2**

In the `**Step 2 — Validate state:**` section, after item 4 (`passive_known >= active_known`), add:

```markdown
5. `performance_scaffolded` and `performance_unscaffolded` consistent with `status`? (e.g., scaffolded=struggling but status=acquired is a flag)
6. After session 5, `receptive_skills` levels should be populated
```

- [ ] **Step 2: Update the Main Lesson consolidation path**

In `### Main Lesson (15-25 min)`, find the consolidation bullet:
```markdown
- Consolidation: skip explanation, reduce scaffolding, mix with other concepts.
```

Replace with:
```markdown
- Consolidation: check context performance fields. Scaffolded struggling → controlled practice. Scaffolded competent, unscaffolded struggling → communicative practice. Integration untested → combined exercises with other active concepts.
```

- [ ] **Step 3: Add to State Updates section**

In `## State Updates (Silent, After Every Session)`, after item 2, add:

```markdown
2b. Update `performance_scaffolded` and `performance_unscaffolded` for each practiced concept
2c. Update `integration_tested` if concepts were combined in free practice
2d. Update `receptive_skills` if listening/reading homework was reviewed
```

- [ ] **Step 4: Update and add guardrails**

Replace:
```markdown
- **Never advance to a new concept if 2+ concepts are in "practicing" status.** Consolidate first.
```
With:
```markdown
- **Never advance to a new concept if 2+ concepts (3 when carryover exists) are in "practicing" status.** Consolidate first.
```

Add new guardrails to the list:
```markdown
- **Never mark a concept as "acquired" unless `performance_unscaffolded` is "competent".**
- **Never advance phases unless all prerequisite concepts for the next phase are "acquired".** Non-prerequisite concepts may carry over.
```

- [ ] **Step 5: Commit**

```
git add CLAUDE.md
git commit -m "refactor: update CLAUDE.md — context performance, receptive skills, dependency transitions"
```

---

### Task 8: Update onboarding-guide.md and create pronunciation directory

**Files:**
- Modify: `curriculum/tutor-guides/onboarding-guide.md`
- Create: `curriculum/pronunciation/.gitkeep`

- [ ] **Step 1: Update onboarding-guide.md**

Replace the `## Each Onboarding Session` section content. After "1. Read the corresponding...", add a note about the midpoint consolidation:

After "Follow the plan, but adapt pacing if the learner is faster or slower than expected", add:

```markdown
5. Sessions 6 and 10 are consolidation sessions (no new grammar concept). Use session 6 for midpoint review of sessions 2-5. If the learner has already been consolidating due to pacing adjustments, use the consolidation session for the next planned concept instead.
```

Update the tool introduction schedule to match:
```markdown
   - Sessions 1-2: Anki installed and first deck created
   - Sessions 2-3: SpanishDict bookmarked, Dreaming Spanish bookmarked
   - Sessions 4-5: Language Transfer queued, graded reader obtained
   - Sessions 7: Speechling account created
   - Sessions 9: Whisper transcription script set up (optional, if learner is technical)
```

- [ ] **Step 2: Update At Session 10 to At Session 10 (Final Consolidation)**

Replace "At Session 10" with "At Session 10 (Final Consolidation)" and keep the content the same.

- [ ] **Step 3: Create pronunciation directory**

```bash
mkdir -p curriculum/pronunciation
touch curriculum/pronunciation/.gitkeep
```

- [ ] **Step 4: Commit**

```
git add curriculum/tutor-guides/onboarding-guide.md curriculum/pronunciation/.gitkeep
git commit -m "feat: update onboarding guide for midpoint consolidation, create pronunciation directory"
```

---

### Task 9: Update system-design.md — Architecture and Schemas

**Files:**
- Modify: `docs/system-design.md`

This is a large file (~1600 lines). Changes are targeted to specific sections. This task covers the architecture tree and schema sections. Task 10 covers the decision engine, progression, and file format sections.

- [ ] **Step 1: Update the architecture tree**

In the `## System Architecture` section, update the `resources/` section. Replace the 7 individual YAML files:
```
    ├── listening.yaml
    ├── reading.yaml
    ...
```
With:
```
    └── resource-catalog.yaml        # Structured catalog of all external tools
```

Add to the `curriculum/` section:
```
    ├── pronunciation/               # Pronunciation guide files by target sound
    │   ├── vowel-sounds.md
    │   ├── stress-rules.md
    │   └── ...12 files total
```

- [ ] **Step 2: Update the skill-map schema section**

In `### 3. Skill Map`, update the grammar entry example to show the new fields:

Replace `context_gap: false` with:
```yaml
    performance_scaffolded: null    # null (untested), struggling, competent
    performance_unscaffolded: null  # null (untested), struggling, competent
    integration_tested: false       # tested in combination with other active concepts?
```

Add a comment block above the grammar section explaining the status values and context performance values (matching what's in the new skill-map.yaml header).

Add the `receptive_skills` schema after the writing section.

Update the `cultural_awareness` schema to include the new fields (`introduced_at_phase`, `assessed_through`, `signs_of_acquisition`).

- [ ] **Step 3: Update the schedule schema section**

In `### 4. Schedule`, add:
```yaml
# Carryover concepts from prior phase
carryover_concepts: []

# SRS configuration
anki_new_cards_per_session: 8
anki_retirement_threshold_days: 60
```

- [ ] **Step 4: Update the session log schema**

In `### 5. Session Logs`, add the structured observations to the `session_activities` entry:
```yaml
    observations:
      - concept: ""
        context: ""           # scaffolded or unscaffolded
        attempts: 0           # only for scaffolded
        errors: 0             # only for scaffolded
        assessment: ""        # only for unscaffolded: struggling or competent
```

Update the session log retention note from 30 days to 60 days.

- [ ] **Step 5: Update system-health schema**

Remove `anki_new_cards_per_session`, `anki_retirement_threshold_days`, and `anki_last_deck_audit` from the system-health schema. Add a comment noting these moved to schedule.yaml.

- [ ] **Step 6: Commit**

```
git add docs/system-design.md
git commit -m "docs: update system-design.md — schemas, architecture tree, session retention"
```

---

### Task 10: Update system-design.md — Decision Engine, Progression, and Formats

**Files:**
- Modify: `docs/system-design.md`

- [ ] **Step 1: Update the Advancement Rules section**

Replace the "When to phase transition" rule:
```
All concepts in the current phase are at "acquired" or "automatic"
```
With the dependency-based rule from spec Section 3.2:
```
Phase transition requires ALL of:
1. Every concept that is a prerequisite for any next-phase concept → acquired
2. All remaining concepts → practicing with stable or improving error_trend
3. No concept in regressed status
4. Phase transition assessment passed

Concepts not meeting "acquired" enter schedule.carryover_concepts.
```

Update the "max 2 practicing" guardrail to note it expands to 3 when carryover exists.

- [ ] **Step 2: Update the decision engine GAP description**

In the `### Daily Focus Selection` section, update the GAP factor to include context performance considerations:
```
  GAP (0-10)
    How far is the learner from "acquired" on this?
    Considers context performance:
    - Regressed: highest urgency
    - Scaffolded struggling: high gap
    - Scaffolded competent, unscaffolded struggling: moderate gap
    - Both competent, integration untested: low gap
    - Fully competent and integration tested: maintenance only
```

Add activity type routing after the priority formula:
```
  After selecting focus concept, route activity type:
  - Scaffolded struggling → controlled practice (concept file Stage 2)
  - Scaffolded competent, unscaffolded struggling → communicative practice (Stages 3-4)
  - Integration untested → combined exercises (activities/grammar-in-context.md)
  - All competent → spot-check only, move to next priority
```

- [ ] **Step 3: Update the Grammar Progression tables**

Replace the Phase A, B, C, D grammar tables with the revised versions from the spec (Section 2.2-2.5). This includes:
- Phase A: 8 concepts (was 7)
- Phase B: 11 concepts (was 8)
- Phase C: 9 concepts (was 7)
- Phase D: 6 concepts (unchanged)

- [ ] **Step 4: Update the Grammar Concept File Format**

Replace the format section with the new template from spec Section 7.1 (with Teaching Sequence stages 1-4, Signs of Acquisition with scaffolded/unscaffolded/integrated, Connection Points).

- [ ] **Step 5: Update the Vocabulary Progression**

Update word count targets to reflect the core/exposure distinction:
- Cluster sizes: 40-60 words (30 core + 20 exposure)
- Note that phase targets include all vocabulary sources

Add the vocabulary cluster file format from spec Section 7.2.

- [ ] **Step 6: Update the Onboarding section**

Update the `### Onboarding Period (Sessions 1-10)` section to describe:
- 10 sessions with midpoint consolidation at session 6
- The revised concept sequence (ser/estar at session 5, gustar-type at session 8)
- Pacing escape valve

- [ ] **Step 7: Add pronunciation guide file format and known limitations**

Add a subsection for pronunciation guide file format (spec Section 7.5).

Add a "Known Limitations" section at the end covering text-based tutoring constraints, mitigations, and minimum viable commitment (spec Section 12).

- [ ] **Step 8: Commit**

```
git add docs/system-design.md
git commit -m "docs: update system-design.md — decision engine, progression, file formats, limitations"
```

---

### Task 11: Final Verification

- [ ] **Step 1: Verify all YAML files parse**

```bash
python3 -c "
import yaml, glob
files = glob.glob('state/*.yaml') + glob.glob('curriculum/*.yaml')
for f in files:
    try:
        yaml.safe_load(open(f))
        print(f'OK: {f}')
    except Exception as e:
        print(f'FAIL: {f} — {e}')
"
```

All files should show OK.

- [ ] **Step 2: Cross-reference consistency check**

Verify these cross-references are consistent:
1. Every concept ID in `skill-map.yaml` grammar section exists in the corresponding `curriculum/grammar/` directory name (directories may be empty — that's fine, content comes in Plan 2)
2. Every `preempt_at` in `l1-interference.yaml` references a valid concept ID in `skill-map.yaml`
3. Every concept ID in `topic-bank.yaml` `grammar_alignment` arrays references a valid concept ID in `skill-map.yaml`
4. `schedule.yaml` has `carryover_concepts` field
5. `system-health.yaml` no longer has `anki_new_cards_per_session`

```bash
python3 -c "
import yaml

sm = yaml.safe_load(open('state/skill-map.yaml'))
l1 = yaml.safe_load(open('curriculum/l1-interference.yaml'))
tb = yaml.safe_load(open('curriculum/topic-bank.yaml'))
sc = yaml.safe_load(open('state/schedule.yaml'))
sh = yaml.safe_load(open('state/system-health.yaml'))

grammar_ids = set(sm['grammar'].keys())
print(f'Grammar concepts: {len(grammar_ids)}')

# Check L1 interference preempt_at
for p in l1['interference_patterns']:
    pat = p.get('preempt_at', '')
    if pat and pat not in grammar_ids and not pat.startswith('tier') and not pat.startswith('vocab'):
        print(f'L1 WARNING: {pat} not in grammar IDs')

# Check topic bank alignment
for t in tb['topics']:
    for g in t.get('grammar_alignment', []):
        if g not in grammar_ids:
            print(f'TOPIC WARNING: {g} not in grammar IDs ({t[\"name\"]})')

# Check schedule has carryover
assert 'carryover_concepts' in sc, 'Missing carryover_concepts in schedule'
print('Schedule: carryover_concepts present')

# Check system-health doesn't have anki config
assert 'anki_new_cards_per_session' not in sh, 'anki_new_cards_per_session still in system-health'
print('System-health: anki config removed')

print('All cross-references OK')
"
```

- [ ] **Step 3: Final commit if any fixes were needed**

```
git add -A && git commit -m "fix: resolve any cross-reference issues found during verification"
```

Only commit if there were changes. If verification passed cleanly, skip this step.
