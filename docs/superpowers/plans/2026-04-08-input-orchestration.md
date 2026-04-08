# Input Orchestration & Decision Engine Enhancements — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add structured input orchestration (listening/reading levels, comprehension debriefs, resource tracking) and three decision engine enhancements (interleaving, carryover escalation, vocabulary production tracking) to the Spanish tutoring system.

**Architecture:** This is a content-heavy implementation — YAML schemas, markdown tutor guides, and Python validation scripts. No application code. State files define the data model, tutor guides define behavior, and scripts validate consistency. Changes are additive to existing schemas and guides.

**Tech Stack:** YAML, Markdown, Python 3 (PyYAML for validation/generation scripts)

**Spec:** `docs/superpowers/specs/2026-04-08-input-orchestration-design.md`

---

### Task 1: Schema Updates — system-design.md

Update the canonical schemas that all state files and tutor behavior reference.

**Files:**
- Modify: `docs/system-design.md:373-383` (vocabulary cluster template)
- Modify: `docs/system-design.md:444-456` (receptive_skills schema)
- Modify: `docs/system-design.md:581-582` (carryover_concepts schema)
- Modify: `docs/system-design.md:620-745` (session log schema — add sections)
- Modify: `docs/system-design.md:161` (resource-tracker description — add schema)

- [ ] **Step 1: Add error_tracking to vocabulary cluster schema**

In `docs/system-design.md`, find the vocabulary cluster template (the `tier1-greetings-introductions` example). Add `error_tracking` fields after `notes`:

Replace:
```yaml
    weak_recognition: []        # can't recognize at all — need input exposure
    last_practiced: null
    notes: ""

  # ... (one entry per vocabulary cluster in curriculum/vocabulary/)
```

With:
```yaml
    weak_recognition: []        # can't recognize at all — need input exposure
    last_practiced: null
    notes: ""
    error_tracking:
      error_rate_production: null  # rolling avg, last 5 in-session observations (null = unobserved)
      common_errors: []            # e.g., "gender: 'el mano' → 'la mano'", "false cognate: 'realizar' for 'to realize'"
      last_observed: null          # date of last in-session production observation

  # ... (one entry per vocabulary cluster in curriculum/vocabulary/)
```

- [ ] **Step 2: Replace receptive_skills schema**

In `docs/system-design.md`, replace the entire `receptive_skills` block:

Replace:
```yaml
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
```

With:
```yaml
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
```

- [ ] **Step 3: Add detailed carryover_concepts schema**

In `docs/system-design.md`, replace the carryover_concepts line:

Replace:
```yaml
# Carryover — concepts from prior phase still in active practice
carryover_concepts: []
```

With:
```yaml
# Carryover — concepts from prior phase still in active practice
# Each entry tracks escalation state for stalled-concept intervention.
# Populated during phase transitions for concepts not yet "acquired".
carryover_concepts: []
  # Entry structure when populated:
  # - concept_id: A-05           # skill-map key
  #   carryover_date: ""         # date concept entered carryover
  #   sessions_in_carryover: 0   # incremented each session the concept is practiced
  #   current_approach: ""       # rule_based / example_based / communicative / context_shift — tracks instructional approach for escalation
  #   is_prerequisite: false     # true if this concept blocks introduction of current-phase concepts
  #   escalation_stage: normal   # normal / flagged / approach_changed / sprint / surfaced
```

- [ ] **Step 4: Add resource-tracker schema section**

In `docs/system-design.md`, find the line:
```
│   ├── resource-tracker.yaml        # Which external resources are in rotation
```

After the schedule section (after line 614, before the session log section), add a new subsection:

```markdown
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
  #   comprehension_trend: null    # improving / stable / declining (updated each debrief for this resource)
  #   vocabulary_extracted: 0      # count of words surfaced in debriefs
  #   last_assigned: null
  #   last_completed: null
  #   learner_engagement: null     # enthusiastic / neutral / reluctant
  #   notes: ""
```
```

- [ ] **Step 5: Add input_reviewed and interleaved_concepts to session log schema**

In `docs/system-design.md`, inside the session log YAML block, add two new sections. Insert after the `assignment_review` section (after line 640, before `session_activities`):

```yaml
# Input comprehension debrief — what the learner consumed since last session
input_reviewed: []
  # Entry structure when populated:
  # - resource: ""                          # resource name (e.g., "Dreaming Spanish - Beginner: Mi rutina")
  #   type: listening                       # listening / reading
  #   duration_minutes: 0
  #   passes: 1                             # multi-pass count (L2-L3: recommend 2-3 passes)
  #   comprehension_assessment: null        # gist / main_ideas / details / inference
  #   vocabulary_extracted: []              # words/phrases learner reported picking up
  #   production_gaps_observed: []          # words learner reached for but couldn't produce
  #   difficulty_self_report: null          # too_easy / just_right / too_hard
  #   level_at_time: ""                     # learner's listening/reading level when this was assigned
```

Insert after `skill_map_updates` section (after line 666, before `assignments`):

```yaml
# Interleaving — which prior concepts were woven into today's primary concept practice
interleaved_concepts: []
  # Entry structure when populated:
  # - concept_id: ""                        # skill-map key of the interleaved concept
  #   interleave_context: ""                # e.g., "embedded ser/estar usage in preterite drill sentences"
  #   errors_observed: 0                    # error count for this concept during interleaved practice
```

- [ ] **Step 6: Validate YAML examples parse correctly**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('docs/system-design.md').read().split('```yaml')[1].split('```')[0])" 2>&1 || echo "Check embedded YAML blocks manually — multi-block files need individual validation"
```

Expected: Embedded YAML blocks may not be independently parseable (they're documentation examples). Verify by visual inspection that all new YAML follows existing formatting conventions.

- [ ] **Step 7: Commit**

```bash
git add docs/system-design.md
git commit -m "docs: add input orchestration and vocabulary tracking schemas to system-design"
```

---

### Task 2: Apply State File Changes

Apply the new schemas to actual state files.

**Files:**
- Modify: `state/skill-map.yaml:829-841` (receptive_skills)
- Modify: `state/skill-map.yaml:531-751` (all 20 vocabulary clusters — add error_tracking)
- Modify: `state/resource-tracker.yaml` (full rewrite)

- [ ] **Step 1: Replace receptive_skills in skill-map.yaml**

In `state/skill-map.yaml`, replace:

```yaml
receptive_skills:
  listening:
    current_level: null
    comprehension_quality: null
    speed_tolerance: null
    last_level_change: null
    notes: ''
  reading:
    current_level: null
    comprehension_quality: null
    lookup_frequency: null
    last_level_change: null
    notes: ''
```

With:
```yaml
receptive_skills:
  listening:
    current_level: L1
    comprehension_quality: null
    hours_at_level: 0
    hours_total: 0
    level_up_evidence: []
    level_history: []
  reading:
    current_level: R1
    comprehension_quality: null
    lookup_frequency: frequent
    hours_at_level: 0
    hours_total: 0
    level_up_evidence: []
    level_history: []
```

- [ ] **Step 2: Add error_tracking to all 20 vocabulary clusters**

For each of the 20 vocabulary clusters in `state/skill-map.yaml`, add `error_tracking` after the `notes` field. Each cluster follows the same pattern. Here's the exact addition for each — append after `notes: ''`:

```yaml
    error_tracking:
      error_rate_production: null
      common_errors: []
      last_observed: null
```

The 20 clusters to update (all follow identical structure):
1. `tier1-greetings-introductions` (line 531)
2. `tier1-numbers-time-dates` (line 541)
3. `tier1-food-restaurant` (line 551)
4. `tier1-directions-transportation` (line 561)
5. `tier1-basic-descriptions` (line 571)
6. `tier2-home-household` (line 581)
7. `tier2-work-office` (line 591)
8. `tier2-family-relationships` (line 601)
9. `tier2-shopping-money` (line 611)
10. `tier2-weather-seasons` (line 621)
11. `tier2-health-body` (line 631)
12. `tier3-opinions-agreement` (line 641)
13. `tier3-emotions-feelings` (line 651)
14. `tier3-plans-future` (line 661)
15. `tier3-storytelling-narration` (line 671)
16. `tier3-hobbies-interests` (line 681)
17. `tier3-travel-culture` (line 691)
18. `tier4-politics-society` (line 701)
19. `tier4-philosophy-ideas` (line 711)
20. `tier4-hypotheticals-debate` (line 721)
21. `tier4-humor-idioms` (line 731)
22. `tier4-professional-specialized` (line 741)

(Note: 22 clusters, not 20 — count from the actual file.)

- [ ] **Step 3: Rewrite resource-tracker.yaml**

Replace the entire content of `state/resource-tracker.yaml`:

```yaml
# Resource Tracker — input resource engagement and comprehension trends
# Entries created on first assignment, not pre-populated from media-bank.
# Schema defined in docs/system-design.md

schema_version: 1

input_summary:
  total_listening_hours: 0
  total_reading_hours: 0
  current_listening_level: L1
  current_reading_level: R1

resources: []
```

- [ ] **Step 4: Validate state files parse**

Run:
```bash
python3 -c "
import yaml
for f in ['state/skill-map.yaml', 'state/resource-tracker.yaml']:
    data = yaml.safe_load(open(f))
    print(f'{f}: OK ({type(data).__name__})')
"
```

Expected: Both files report OK (dict).

- [ ] **Step 5: Validate vocabulary clusters have error_tracking**

Run:
```bash
python3 -c "
import yaml
sm = yaml.safe_load(open('state/skill-map.yaml'))
vocab = sm.get('vocabulary', {})
missing = [k for k, v in vocab.items() if 'error_tracking' not in v]
if missing:
    print(f'MISSING error_tracking: {missing}')
else:
    print(f'All {len(vocab)} vocabulary clusters have error_tracking')
"
```

Expected: `All 22 vocabulary clusters have error_tracking`

- [ ] **Step 6: Commit**

```bash
git add state/skill-map.yaml state/resource-tracker.yaml
git commit -m "feat: apply input orchestration schemas to state files"
```

---

### Task 3: Create Listening Progression

Define the 5-level listening progression with sources, criteria, and calibration data.

**Files:**
- Create: `curriculum/listening-progression.yaml`

- [ ] **Step 1: Create listening-progression.yaml**

```yaml
# Listening Progression — 5 levels from simplified speech to native media
# Referenced by input-orchestration.md and decision engine (Step 6b).
# Levels advance independently of grammar phases — driven by debrief quality and hours.

levels:
  L1:
    name: Simplified tutor speech
    description: >
      Learner processes isolated words and short memorized phrases.
      Input comes primarily from in-session tutor speech (slowed, simplified)
      and audio on Anki cards. Forvo for pronunciation reference.
    speed: simplified
    support: full_context
    comprehension_target: gist
    comprehension_description: Recognize individual words and memorized phrases
    sources:
      - name: In-session tutor speech
        type: session
        notes: Tutor uses simplified Spanish during practice
      - name: Anki card audio
        type: srs
        notes: Pronunciation audio on flashcards
      - name: Forvo
        type: reference
        notes: Native pronunciation of individual words
    multi_pass: false
    level_up:
      criteria:
        - Recognizes 50+ words in spoken context (not just flashcards)
        - Can follow simplified tutor instructions in Spanish
        - Comprehension debrief shows word-level recognition is consistent
      minimum_hours: 5
      consecutive_weeks_at_target: 1
    notes: >
      Most learners pass through L1 quickly (sessions 1-3) since it overlaps
      with initial vocabulary building. No dedicated input homework at this level.

  L2:
    name: Slow, structured speech
    description: >
      Learner processes slow, clearly enunciated speech with heavy visual support
      and repetition. Content is designed for learners — simplified vocabulary,
      clear context, visual reinforcement of meaning.
    speed: slow
    support: heavy_visual_and_repetition
    comprehension_target: gist
    comprehension_description: "Can answer 'what was it about?' with a general topic"
    sources:
      - name: Dreaming Spanish
        type: youtube
        level_within_source: [Super Beginner, Beginner]
        notes: Primary L2 resource. 2000+ videos. Heavily visual, comprehensible input method.
      - name: News in Slow Spanish
        type: podcast
        notes: Graded speed. Two editions (Latino, Peninsular). Bridge to faster content.
      - name: Coffee Break Spanish
        type: podcast
        notes: Structured lessons. Strong for travel-topic vocabulary.
      - name: Cuentos de Hadas
        type: podcast
        notes: Fairy tales narrated slowly. Low-pressure listening.
      - name: Duolingo Spanish Podcast
        type: podcast
        notes: Bilingual format (English narrator, Spanish story). Good bridge.
      - name: Extra en Español
        type: tv
        notes: Sitcom for learners. Very simplified language.
      - name: Destinos
        type: tv
        notes: Educational telenovela. Slow, clear, graded.
    multi_pass: true
    multi_pass_protocol:
      pass_1: Listen for gist — what is the general topic?
      pass_2: Listen for details — what specifically happened or was described?
      pass_3: Listen for vocabulary — what new words can you pick out from context?
    level_up:
      criteria:
        - Comprehension debrief consistently shows gist-level understanding
        - Can name the topic and 1-2 specifics from assigned content
        - Self-reports "just right" or "too easy" for 2+ consecutive weeks
      minimum_hours: 20
      consecutive_weeks_at_target: 2
    notes: >
      This is where most early learners spend significant time. Multi-pass listening
      is strongly recommended. Prescriptive assignments — tutor selects specific episodes.

  L3:
    name: Moderate, semi-structured speech
    description: >
      Learner processes moderate-speed speech with some visual support but less
      repetition. Content may be designed for learners or be simplified native content.
      Speaker may use natural connectors and some colloquial phrasing.
    speed: moderate
    support: visual_support_less_repetition
    comprehension_target: main_ideas
    comprehension_description: "Can summarize main ideas and some supporting details"
    sources:
      - name: Dreaming Spanish
        type: youtube
        level_within_source: [Intermediate]
        notes: Step up from Beginner. Less visual scaffolding, more natural speech.
      - name: Notes in Spanish
        type: podcast
        level_within_source: [Intermediate]
        notes: Three tiers available. Intermediate tier matches L3 well.
      - name: Españolistos
        type: podcast
        notes: Natural conversations with vocabulary explanations inline.
      - name: Hoy Hablamos
        type: podcast
        notes: Short daily episodes with transcripts. Good for building habit.
      - name: Easy Spanish
        type: youtube
        notes: Street interviews with subtitles. Real accents, natural speech.
    multi_pass: true
    multi_pass_protocol:
      pass_1: Listen for main ideas — what are the key points?
      pass_2: Listen for details and new vocabulary
    level_up:
      criteria:
        - Comprehension debrief shows main-idea understanding with some details
        - Can discuss content beyond surface-level summary
        - Self-reports "just right" or "too easy" for 2+ consecutive weeks
      minimum_hours: 40
      consecutive_weeks_at_target: 2
    notes: >
      The L2→L3 transition is the biggest hurdle. If a learner struggles, don't level
      down immediately — try different L3 sources first. Españolistos and Hoy Hablamos
      offer more scaffolding than Dreaming Spanish Intermediate.

  L4:
    name: Natural speed with text support
    description: >
      Learner processes natural-speed speech with subtitle or transcript support
      available. Content is native media consumed with Language Reactor, Spanish
      subtitles, or transcript-provided podcasts.
    speed: natural
    support: text_support_available
    comprehension_target: details
    comprehension_description: "Can follow narrative, catch details, make basic inferences"
    sources:
      - name: Language Reactor
        type: browser_extension
        notes: Netflix/YouTube with dual subtitles. Primary L4 tool.
      - name: Duolingo Spanish Podcast
        type: podcast
        notes: Still useful at L4 for the full-Spanish segments.
      - name: No Hay Tos
        type: podcast
        notes: Mexican-American duo. Slang, idioms. Natural pace.
      - name: Club de Cuervos
        type: tv
        notes: Comedy. Natural Mexican speech. Use Spanish subtitles.
      - name: Las Chicas del Cable
        type: tv
        notes: Period drama. Clear enunciation, formal register.
      - name: Nada (2023)
        type: tv
        notes: Simple dialogue, cultural depth. Good L4 entry.
    multi_pass: false
    level_up:
      criteria:
        - Comprehension debrief shows detail-level understanding
        - Can discuss plot points, character motivations, or argument structure
        - Increasingly comfortable without subtitles for familiar content
        - Self-reports "just right" or "too easy" for 2+ consecutive weeks
      minimum_hours: 60
      consecutive_weeks_at_target: 2
    notes: >
      At L4, the learner starts engaging with content for enjoyment, not just study.
      Guided assignments — tutor suggests 2-3 options, learner picks.

  L5:
    name: Native media, varied accents
    description: >
      Learner processes native-speed speech across varied accents, registers, and
      speaking styles without text support. Content is authentic media chosen by the
      learner for interest, not for study.
    speed: natural_varied
    support: none
    comprehension_target: inference
    comprehension_description: "Full comprehension with inference, humor, subtext"
    sources:
      - name: Radio Ambulante
        type: podcast
        notes: NPR-quality narrative journalism. Full transcripts available but not needed.
      - name: El Hilo
        type: podcast
        notes: Weekly deep-dive journalism. Challenging vocabulary.
      - name: La Casa de Papel
        type: tv
        notes: Fast speech, complex plot. No subtitles at this level.
      - name: Narcos
        type: tv
        notes: Colombian dialect. Mixed English/Spanish.
      - name: El Internado
        type: tv
        notes: Mystery/thriller. Complex dialogue. Advanced listening stamina.
      - name: Calle 13 / Residente
        type: music
        notes: Rapid-fire lyrics, social commentary. Advanced vocabulary.
    multi_pass: false
    level_up:
      criteria:
        - This is the terminal level. No level-up.
        - Mastery indicators: follows humor and wordplay, catches regional expressions,
          comfortable with unfamiliar accents after brief adjustment
      minimum_hours: null
      consecutive_weeks_at_target: null
    notes: >
      Autonomous assignments — learner chooses their own input. Debrief focuses on
      what they found interesting, new expressions encountered, cultural observations.

# Level-down criteria (applies to all levels L2+):
# - Comprehension debrief shows gist-only at a level targeting details, for 2+ sessions
# - OR learner reports sustained struggle for 2+ sessions
# - Level-down is never framed as failure.
# - Before leveling down, try a different source at the same level first.

# Hour minimums are soft guidelines, not hard gates.
# A learner consistently excelling before the hour target should not be held back.
```

- [ ] **Step 2: Validate YAML parses**

Run:
```bash
python3 -c "
import yaml
data = yaml.safe_load(open('curriculum/listening-progression.yaml'))
levels = data['levels']
print(f'Loaded {len(levels)} listening levels: {list(levels.keys())}')
"
```

Expected: `Loaded 5 listening levels: ['L1', 'L2', 'L3', 'L4', 'L5']`

- [ ] **Step 3: Commit**

```bash
git add curriculum/listening-progression.yaml
git commit -m "feat: add listening progression levels L1-L5"
```

---

### Task 4: Create Reading Progression

Define the 5-level reading progression with sources, criteria, and calibration data.

**Files:**
- Create: `curriculum/reading-progression.yaml`

- [ ] **Step 1: Create reading-progression.yaml**

```yaml
# Reading Progression — 5 levels from cognate recognition to authentic literature
# Referenced by input-orchestration.md and decision engine (Step 6b).
# Levels advance independently of grammar phases and listening levels.

levels:
  R1:
    name: Cognates, labels, short familiar-topic texts
    description: >
      Learner recognizes cognates, reads labels, menus, and single sentences
      on familiar topics. Heavy reliance on English-Spanish cognate overlap.
      Reading happens primarily in-session and on Anki cards.
    comprehension_target: gist
    comprehension_description: Word-level recognition, cognate identification
    sources:
      - name: In-session materials
        type: session
        notes: Tutor-created sentences, vocabulary lists in context
      - name: Anki card context sentences
        type: srs
        notes: Example sentences on flashcards
      - name: SpanishDict
        type: reference
        notes: Dictionary with example sentences and conjugation tables
    level_up:
      criteria:
        - Recognizes 80%+ of common cognates in short texts
        - Can read simple sentences with known vocabulary without dictionary
        - Ready to engage with short paragraphs
      minimum_hours: 3
      consecutive_weeks_at_target: 1
    notes: >
      Brief level — most learners pass through R1 during sessions 1-5 as vocabulary
      builds. No dedicated reading homework at this level beyond Anki.

  R2:
    name: Short paragraphs, graded readers L1
    description: >
      Learner reads short paragraphs and entry-level graded readers.
      Dictionary support is expected and normal. Content uses controlled
      vocabulary with glossaries.
    comprehension_target: gist
    comprehension_description: Gist comprehension with dictionary support
    sources:
      - name: "Short Stories in Spanish for Beginners (Olly Richards)"
        type: graded_reader
        cefr: [A2, B1]
        notes: "8 stories with glossaries. Primary Phase A-B reading resource."
      - name: "Practice Makes Perfect — Spanish Reading and Comprehension"
        type: graded_reader
        cefr: [A1, A2, B1]
        notes: Textbook-style graded readings with exercises.
      - name: SpanishDict articles
        type: web
        notes: Grammar and culture articles written for learners.
    level_up:
      criteria:
        - Can read a full graded reader chapter and summarize the main idea
        - Dictionary lookups decreasing (from every sentence to every few sentences)
        - Comprehension debrief shows gist understanding of assigned reading
      minimum_hours: 15
      consecutive_weeks_at_target: 2
    notes: >
      Prescriptive assignments — tutor assigns specific chapters or passages.
      Encourage the learner to read through unknown words before looking them up.

  R3:
    name: Graded readers L2-3, simple articles
    description: >
      Learner reads higher-level graded readers and simple authentic articles.
      Dictionary lookup is occasional, not constant. Content uses natural
      language with some simplification.
    comprehension_target: main_ideas
    comprehension_description: Main ideas with limited dictionary lookup
    sources:
      - name: "Short Stories in Spanish for Intermediate Learners (Olly Richards)"
        type: graded_reader
        cefr: [B1, B2]
        notes: Longer stories, less hand-holding than beginner volume.
      - name: "El Principito (Antoine de Saint-Exupéry)"
        type: adapted_classic
        cefr: [B1]
        notes: Simple prose, deep themes. Bilingual editions available.
      - name: "Cajas de Cartón (Francisco Jiménez)"
        type: authentic_literature
        cefr: [B1, B2]
        notes: Autobiographical. Simple language, powerful content.
      - name: News in Slow Spanish articles
        type: web
        notes: Companion articles to the podcast. Graded language.
      - name: Simple blog posts
        type: web
        notes: Lifestyle, travel, food blogs written in accessible Spanish.
    level_up:
      criteria:
        - Comprehension debrief shows main-idea understanding
        - Can discuss themes and key events from assigned reading
        - Dictionary lookup is occasional (a few times per page, not per sentence)
      minimum_hours: 30
      consecutive_weeks_at_target: 2
    notes: >
      Guided assignments — tutor suggests 2-3 options, learner picks.
      Journal prompts can reference reading content for deeper processing.

  R4:
    name: Authentic articles, blog posts, short stories
    description: >
      Learner reads authentic (non-graded) content written for native speakers.
      Dictionary lookup is infrequent. Content includes opinion pieces, news
      articles, and short literary fiction.
    comprehension_target: details
    comprehension_description: Detail comprehension with infrequent dictionary lookup
    sources:
      - name: BBC Mundo
        type: web
        notes: International news in clear, standard Spanish.
      - name: "Crónica de una Muerte Anunciada (García Márquez)"
        type: authentic_literature
        cefr: [B2, C1]
        notes: Short novel (~120 pages). Good first authentic novel.
      - name: "Como Agua para Chocolate (Laura Esquivel)"
        type: authentic_literature
        cefr: [B2, C1]
        notes: Mexican magical realism. Food and family. Rich but accessible.
      - name: Medium-length articles and essays
        type: web
        notes: Opinion pieces, cultural commentary, long-form journalism.
    level_up:
      criteria:
        - Can read an article and discuss specific arguments or narrative details
        - Dictionary lookup is rare (a few times per article, for specialized vocabulary)
        - Comprehension debrief shows detail-level understanding
      minimum_hours: 40
      consecutive_weeks_at_target: 2
    notes: >
      Autonomous-leaning assignments. The learner should be choosing reading material
      based on interest. Tutor may suggest specific articles aligned with weekly topic.

  R5:
    name: Literature, journalism, technical content
    description: >
      Learner reads complex authentic texts — novels, longform journalism,
      academic or professional content. Full comprehension with rare dictionary use.
    comprehension_target: inference
    comprehension_description: Full comprehension including inference, style, subtext
    sources:
      - name: "La Sombra del Viento (Carlos Ruiz Zafón)"
        type: authentic_literature
        cefr: [C1]
        notes: Gothic mystery in Barcelona. Beautiful prose. Capstone read.
      - name: Longform journalism
        type: web
        notes: Radio Ambulante transcripts, El País longform, Gatopardo.
      - name: Academic or professional content
        type: web
        notes: Content in the learner's professional domain.
    level_up:
      criteria:
        - Terminal level. No level-up.
        - Mastery indicators: reads for pleasure without study intent,
          appreciates literary style and wordplay, comfortable across registers
      minimum_hours: null
      consecutive_weeks_at_target: null
    notes: >
      Fully autonomous. Learner chooses all reading. Debrief is conversational —
      what they're reading, what they found interesting, new expressions encountered.
```

- [ ] **Step 2: Validate YAML parses**

Run:
```bash
python3 -c "
import yaml
data = yaml.safe_load(open('curriculum/reading-progression.yaml'))
levels = data['levels']
print(f'Loaded {len(levels)} reading levels: {list(levels.keys())}')
"
```

Expected: `Loaded 5 reading levels: ['R1', 'R2', 'R3', 'R4', 'R5']`

- [ ] **Step 3: Commit**

```bash
git add curriculum/reading-progression.yaml
git commit -m "feat: add reading progression levels R1-R5"
```

---

### Task 5: Media Bank Annotations

Add `level_range` to existing source-level entries and create a `prescriptive_episodes` section with content summaries for L2-L3 staples.

**Files:**
- Modify: `curriculum/media-bank.yaml`

- [ ] **Step 1: Add level_range to youtube_channels**

Add a `level_range` field to each youtube channel entry after `phase_range`. The level_range maps to our L1-L5 listening levels:

| Channel | level_range |
|---------|------------|
| Dreaming Spanish | [L2, L4] |
| Easy Spanish | [L3, L4] |
| SpanishPod101 | [L2, L3] |
| Why Not Spanish | [L2, L4] |
| Butterfly Spanish | [L2, L3] |
| Español con Juan | [L3, L4] |
| Hola Spanish | [L2, L3] |
| SpanishWithPaul | [L2, L3] |
| Superholly | [L4, L5] |
| Academia Play | [L4, L5] |

For each entry, add `level_range: [XX, XX]` on the line after `phase_range`. Example for the first entry:

Replace:
```yaml
  - name: Dreaming Spanish
    dialect: mixed
    phase_range: [A, B, C]
    levels: [superbeginner, beginner, intermediate, advanced]
```

With:
```yaml
  - name: Dreaming Spanish
    dialect: mixed
    phase_range: [A, B, C]
    level_range: [L2, L4]
    levels: [superbeginner, beginner, intermediate, advanced]
```

Apply similar additions to all 10 youtube channel entries.

- [ ] **Step 2: Add level_range to podcasts**

| Podcast | level_range |
|---------|------------|
| News in Slow Spanish | [L2, L3] |
| Radio Ambulante | [L5] |
| Duolingo Spanish Podcast | [L2, L3] |
| Notes in Spanish | [L2, L4] |
| Coffee Break Spanish | [L2, L3] |
| Hoy Hablamos | [L3, L4] |
| Españolistos | [L3, L4] |
| No Hay Tos | [L4, L5] |
| El Hilo | [L5] |
| Cuentos de Hadas | [L2] |

Add `level_range` after `phase_range` for each podcast entry.

- [ ] **Step 3: Add level_range to tv_shows**

| TV Show | level_range |
|---------|------------|
| Extra en Español | [L2] |
| Destinos | [L2, L3] |
| Club de Cuervos | [L4] |
| Elite | [L4, L5] |
| Las Chicas del Cable | [L4] |
| Nada (2023) | [L3, L4] |
| Siempre Bruja | [L3, L4] |
| La Casa de Papel | [L5] |
| Narcos | [L5] |
| El Internado | [L5] |

- [ ] **Step 4: Add level_range to books**

| Book | level_range |
|------|------------|
| Short Stories Beginners (Olly Richards) | [R2] |
| Practice Makes Perfect Reading | [R1, R2] |
| Short Stories Intermediate (Olly Richards) | [R3] |
| El Principito | [R3] |
| Cajas de Cartón | [R3, R4] |
| Crónica de una Muerte Anunciada | [R4] |
| Como Agua para Chocolate | [R4] |
| La Sombra del Viento | [R5] |

- [ ] **Step 5: Add prescriptive_episodes section**

Append to the end of `curriculum/media-bank.yaml`:

```yaml

# Prescriptive episodes — specific content for L2-L3 assignments with summaries
# Content summaries enable informed comprehension debriefs.
# These must be human-authored (from episode descriptions or manual review).
# The tutor cannot generate summaries — it cannot watch/listen to content.
# Add entries incrementally as resources enter regular rotation.

prescriptive_episodes:
  listening:
    - source: Dreaming Spanish
      title: "Super Beginner — Mi rutina diaria"
      level: L2
      dialect: neutral_latam
      duration_minutes: 7
      topic_alignment: [my-daily-routine]
      content_summary: >
        Speaker acts out a complete morning routine using present tense.
        Key vocabulary: despertarse, levantarse, ducharse, vestirse, desayunar,
        salir de casa. Heavily visual with each action demonstrated physically.
        Simple sentence structure: "Primero me despierto. Después me levanto."

    - source: Dreaming Spanish
      title: "Super Beginner — Mi familia"
      level: L2
      dialect: neutral_latam
      duration_minutes: 6
      topic_alignment: [childhood-and-family]
      content_summary: >
        Speaker introduces family members using photos/drawings. Key vocabulary:
        madre, padre, hermano, hermana, abuelo, abuela, tío, tía. Uses ser for
        descriptions ("Mi madre es alta") and tener for age ("Mi hermano tiene
        veinte años"). Slow, clear, repetitive.

    - source: Dreaming Spanish
      title: "Beginner — Qué hago los fines de semana"
      level: L2
      dialect: neutral_latam
      duration_minutes: 9
      topic_alignment: [weekend-plans-and-activities]
      content_summary: >
        Speaker describes weekend activities with visual support. Key vocabulary:
        ir al parque, cocinar, leer, ver películas, salir con amigos. Uses gustar
        construction ("Me gusta cocinar") and ir + a + infinitive for plans.
        Moderate visual support, slightly less repetitive than Super Beginner.

    - source: News in Slow Spanish
      title: "Weekly News — sample beginner episode"
      level: L2
      dialect: peninsular
      duration_minutes: 10
      topic_alignment: [current-events-and-society]
      content_summary: >
        Current events presented at reduced speed with simplified vocabulary.
        Each story is 2-3 minutes. Grammar structures are present tense dominant.
        Useful for building news vocabulary: país, gobierno, personas, problema.
        Peninsular pronunciation and vocabulary.

    - source: Duolingo Spanish Podcast
      title: "Sample beginner episode"
      level: L2
      dialect: mixed_latin_american
      duration_minutes: 20
      topic_alignment: [telling-stories, childhood-and-family]
      content_summary: >
        Bilingual format — English narrator provides context, Spanish speaker
        tells personal story. The Spanish segments use past tense (preterite/
        imperfect) but at slow, clear pace with context from English framing.
        Good for passive exposure to past tense before formal introduction.

    - source: Coffee Break Spanish
      title: "Sample lesson episode"
      level: L2
      dialect: peninsular
      duration_minutes: 20
      topic_alignment: [greetings-and-introductions, getting-around-town]
      content_summary: >
        Structured lesson with native speaker. Introduces situational vocabulary
        (greetings, directions, ordering) with repetition and explanation.
        Teacher-student format — the English-speaking host learns alongside listener.

    - source: Dreaming Spanish
      title: "Intermediate — Una historia de mi infancia"
      level: L3
      dialect: neutral_latam
      duration_minutes: 12
      topic_alignment: [childhood-and-family, telling-stories]
      content_summary: >
        Speaker narrates a childhood memory using past tenses. Key grammar:
        preterite for events ("Un día fui al parque"), imperfect for descriptions
        ("Hacía mucho calor"). Less visual support than Beginner — relies more
        on narrative context. Natural connectors: entonces, después, pero.

    - source: Dreaming Spanish
      title: "Intermediate — Comparando ciudades"
      level: L3
      dialect: neutral_latam
      duration_minutes: 10
      topic_alignment: [comparing-cities-and-countries]
      content_summary: >
        Speaker compares two cities they've lived in. Key grammar: comparatives
        (más...que, menos...que, tan...como), ser vs estar for city descriptions.
        Moderate speed, some natural filler words (bueno, pues, o sea). Good for
        opinion vocabulary: creo que, me parece, en mi opinión.

    - source: Easy Spanish
      title: "Street interview sample — ¿Qué comes normalmente?"
      level: L3
      dialect: mixed
      duration_minutes: 8
      topic_alignment: [food-and-eating-out]
      content_summary: >
        Street interviews with multiple speakers about eating habits. Varied
        accents and speaking speeds. Subtitles available. Key vocabulary: comida,
        desayuno, almuerzo, cena, cocinar, restaurante. Some speakers are fast —
        subtitles help. Good exposure to natural speech variety.

    - source: Españolistos
      title: "Sample conversation episode"
      level: L3
      dialect: colombian
      duration_minutes: 25
      topic_alignment: [emotions-and-relationships]
      content_summary: >
        American-Colombian couple discusses a relationship topic naturally.
        Vocabulary explanations embedded in conversation (Andrea explains Colombian
        expressions to her husband). Moderate pace, natural back-and-forth.
        Good model for conversational rhythm and back-channeling.
```

- [ ] **Step 6: Validate YAML parses**

Run:
```bash
python3 -c "
import yaml
data = yaml.safe_load(open('curriculum/media-bank.yaml'))
sections = list(data.keys())
eps = data.get('prescriptive_episodes', {})
listening_eps = eps.get('listening', [])
print(f'Sections: {sections}')
print(f'Prescriptive listening episodes: {len(listening_eps)}')
for ep in listening_eps:
    print(f'  - {ep[\"source\"]}: {ep[\"title\"]} (L{ep[\"level\"][-1]})')
"
```

Expected: Shows all sections including `prescriptive_episodes`, with 10 listening episodes listed.

- [ ] **Step 7: Commit**

```bash
git add curriculum/media-bank.yaml
git commit -m "feat: add level_range and prescriptive episodes with content summaries to media-bank"
```

---

### Task 6: Input Orchestration Tutor Guide

The main new tutor guide — loaded post-onboarding alongside the decision engine.

**Files:**
- Create: `curriculum/tutor-guides/input-orchestration.md`

- [ ] **Step 1: Create input-orchestration.md**

```markdown
# Input Orchestration Guide

Loaded when: Standard session (post-onboarding), alongside decision-engine.md. Governs input homework selection, comprehension debriefs, level calibration, and input-to-production feedback.

## Overview

Input (listening and reading) is a first-class instructional pathway, not just homework. The system selects level-appropriate resources, debriefs comprehension each session, tracks progression through 5 levels, and feeds observations back into the skill map.

**Key files:**
- `curriculum/listening-progression.yaml` — L1-L5 level definitions with sources and criteria
- `curriculum/reading-progression.yaml` — R1-R5 level definitions with sources and criteria
- `curriculum/media-bank.yaml` — resource catalog with `level_range` and `prescriptive_episodes`
- `state/resource-tracker.yaml` — per-resource engagement tracking
- `state/skill-map.yaml > receptive_skills` — current levels and evidence

## 1. Input Selection (During Homework Assignment)

Run this during the Checkout phase when assigning homework.

### Step 1 — Get current levels

Read `receptive_skills.listening.current_level` and `receptive_skills.reading.current_level` from skill-map.

### Step 2 — Filter resources

From `curriculum/media-bank.yaml`, select resources whose `level_range` includes the learner's current level or one level above (i+1). Apply:
- **Dialect preference:** Prefer resources matching `target_dialect` from learner-profile. Accept neutral-dialect resources.
- **Topic alignment:** Score by overlap with the weekly narrow topic (direct match > adjacent > unrelated).
- **Freshness:** Check `resource-tracker.yaml` — prefer resources not assigned in the last 2 sessions. Avoid resources with `learner_engagement: reluctant`.

### Step 3 — Apply autonomy level

| Phase | Assignment Style | Example |
|-------|-----------------|---------|
| A–B | Prescriptive | "Watch Dreaming Spanish — 'Mi rutina diaria' (7 min). Listen twice: once for gist, once for new words." |
| C | Guided | "Choose one of these podcast episodes about [topic]: Españolistos, Hoy Hablamos, or Notes in Spanish Intermediate." |
| D | Autonomous | "Spend 20 minutes on L5 input of your choice. Tell me about it next session." |

### Step 4 — Calibrate to available time

Input homework must fit within the learner's available homework time. Input's share grows with phase:
- **Phase A:** Input is supplementary — most time goes to Anki and exercises
- **Phase B:** Input becomes a regular assignment, roughly equal with Anki and exercises
- **Phase C:** Input is the primary homework — Anki decreases as vocabulary self-sustains through exposure
- **Phase D:** Input dominates — Anki is maintenance only

Never assign more input than the learner's remaining homework time after required items (Anki, any writing assignments).

### Step 5 — Record assignment

In the session log `assignments` section, include:
- `type: listening` or `type: reading`
- `resource:` specific resource name
- `task:` specific instructions (what to listen for, how many passes)
- `input_minutes:` estimated duration
- `narrow_topic_aligned:` true if aligned with weekly topic

## 2. Comprehension Debrief (During Review & Warm-up)

3-5 minutes. Conversational — not a quiz. Conducted increasingly in Spanish as phase advances.

### Flow

**a) What did you consume?**
Ask what they listened to or read since last session. Log: resource name, estimated duration, number of passes.

**b) Topic probe**
"¿De qué se trataba?" / "What was it about?"

Assess gist comprehension. If they can't summarize the general topic, the level may be too high.

**c) Detail probe**
Ask 1-2 follow-up questions natural to the content.

For resources with a `content_summary` in `media-bank.yaml > prescriptive_episodes`: load the summary before asking, so you can probe specific details (e.g., "You watched the one about daily routines — what was the first thing the speaker did in the morning?").

For resources without summaries: rely on the learner's depth-of-elaboration as the comprehension proxy. Can they go beyond a one-sentence summary? Can they describe specifics?

**d) Vocabulary extraction**
"¿Aprendiste alguna palabra nueva?" / "Pick up any new words?"

Record words/phrases they report. If the learner reports none at a level where they should be encountering unknowns:
- If level might be too low → consider level-up assessment
- If level is appropriate → they may not be noticing. Suggest active listening strategies: pause and repeat new words, keep a notepad while listening

**Note:** Most passive vocabulary acquisition is subconscious. The learner won't report most of what they absorbed. The real signal is comprehension quality at level, not word count.

**e) Difficulty self-report**
"¿Cómo te pareció el nivel?" / "How was the difficulty?"

Cross-reference against observed comprehension quality. If the learner says "fine" but couldn't summarize the content, the calibration is off — note in `learner_observations.calibration_note`.

### Recording

Write the debrief results to the session log's `input_reviewed` section:

```yaml
input_reviewed:
  - resource: "Dreaming Spanish - Beginner: Mi rutina"
    type: listening
    duration_minutes: 7
    passes: 2
    comprehension_assessment: main_ideas
    vocabulary_extracted: ["ducharse", "desayunar"]
    production_gaps_observed: ["cepillarse"]
    difficulty_self_report: just_right
    level_at_time: L2
```

## 3. Skipped Input Homework

- **Single skip:** No intervention. Life happens. Assign normally next session.
- **2 consecutive skips:** Reduce input assignment load — the time budget may be wrong. Do a brief in-session listening moment (2-3 min): describe a short scenario or play a brief segment, then discuss.
- **3+ skips:** Ask the learner what's getting in the way. The assignment format may need to change (different resource type, shorter segments, different time of day), not just the quantity. Adjust and re-engage.

## 4. Level Calibration

### Level-up assessment

All three must be met:
1. Comprehension debrief shows consistent target-quality performance for 2+ consecutive weeks
2. Learner self-reports "just right" or "too easy"
3. Minimum hours at current level reached (see progression YAML for thresholds)

Hour minimums prevent premature level-up from a few good sessions. But a learner consistently excelling before the hour target should not be held back — use judgment.

When leveling up:
1. Update `receptive_skills.[listening/reading].current_level` in skill-map
2. Record the level change in `level_up_evidence` with date and observation
3. Move the old level to `level_history` with `hours_spent`
4. Reset `hours_at_level` to 0
5. Update `resource-tracker.yaml > input_summary`

### Level-down assessment

Either trigger:
1. Comprehension debrief shows gist-only at a level targeting details, for 2+ sessions
2. Learner reports sustained struggle for 2+ sessions

**Before leveling down:** Try a different source at the same level first. If Dreaming Spanish Intermediate is too fast, try Españolistos or Hoy Hablamos (more scaffolding). Only level down if multiple sources at the level are too challenging.

Frame level-down positively: "Let's build more foundation at this level before jumping up."

## 5. State Updates

After each session, update:

| State File | What to Update |
|-----------|---------------|
| `resource-tracker.yaml` | Increment `hours_logged` and `sessions_completed` for debriefed resources. Update `comprehension_trend` (compare last 3-4 debriefs for this resource). Update `learner_engagement` based on how they talked about the resource. |
| `skill-map > receptive_skills` | Update `hours_at_level` and `hours_total` from debrief data. Update `comprehension_quality` to reflect most recent assessment. Add to `level_up_evidence` if relevant. |
| `skill-map > vocabulary_clusters` | Increment `passive_known` for clusters containing words extracted during debrief. Add confirmed production gaps to `weak_production` if the same word appears in `production_gaps_observed` across 2+ sessions. |

## 6. Input → Production Pipeline

When the decision engine selects vocabulary clusters for practice (Step 6b in decision-engine.md), boost clusters where passive input exposure has been logged:

- If `passive_known` has increased for a cluster in the last 2 sessions → the learner has encountered these words in input and is primed for production practice
- This creates a natural flow: input exposure → passive recognition → active production practice
- Don't introduce vocabulary "cold" — prefer clusters the learner has already encountered in context

This integration happens in the decision engine's vocabulary scoring, not in this guide. See decision-engine.md Step 6b.
```

- [ ] **Step 2: Commit**

```bash
git add curriculum/tutor-guides/input-orchestration.md
git commit -m "feat: add input orchestration tutor guide"
```

---

### Task 7: Decision Engine Updates

Add interleaving, carryover escalation, vocabulary scoring, and input selection integration.

**Files:**
- Modify: `curriculum/tutor-guides/decision-engine.md`

- [ ] **Step 1: Add interleaving protocol after Step 5**

In `curriculum/tutor-guides/decision-engine.md`, after the "Step 5 — Route to Activity" section (after the new concept introduction paragraph ending with "Stage 1 (noticing) from concept file."), add:

```markdown
## Step 5b — Select Interleaved Concepts

After selecting the primary concept and routing to an activity stage, select 1-3 prior concepts to weave into the practice activities. Interleaving exercises prior concepts organically during new learning — replacing separate review blocks.

### Selection

1. Query skill-map for concepts with status "acquired" or "practicing" at Stage 3+ (guided production or later)
2. Rank by DECAY score (highest = longest since practiced)
3. Prefer stalled carryover concepts (serves double duty as escalation — see Step 0b)
4. Select count based on primary concept's stage:

| Primary Concept Stage | Interleaved Count | Rule |
|----------------------|-------------------|------|
| Stage 1-2 (first session with concept) | 0-1 | At most 1 acquired concept. New concepts need focused attention. |
| Stage 2 (controlled practice, subsequent sessions) | 1 | 1 acquired concept embedded in drill sentences |
| Stage 3 (guided production) | 2 | 1 acquired + 1 practicing (Stage 3+) woven into prompts |
| Stage 4 (integration) | 2-3 | Concepts across status levels combined in conversation |

### How to Interleave

Don't create separate review activities. Embed prior concepts in the primary concept's practice:

- **Stage 2 drills:** Write drill sentences that require both the primary concept and the interleaved concept. Example: preterite drills where sentences also require correct ser/estar.
- **Stage 3 prompts:** Design conversation prompts that naturally elicit both. Example: "Tell me about a trip you took" targets preterite but requires prepositions and object pronouns.
- **Stage 4 scenarios:** Create scenarios that demand the primary concept plus 2-3 others. Example: giving advice about a problem (conditional + subjunctive + opinion vocabulary).

### Guardrails

- Never interleave a concept the learner hasn't reached Stage 3+ on
- Never interleave more than 3 concepts in a single activity
- If the primary concept is brand new (Stage 1-2, first session), interleave at most 1 acquired concept

### Recording

Log interleaved concepts in the session log:

```yaml
interleaved_concepts:
  - concept_id: A-02
    interleave_context: "embedded ser/estar usage in preterite drill sentences"
    errors_observed: 0
```

Reset the DECAY clock for interleaved concepts — they count as practiced.
```

- [ ] **Step 2: Add carryover escalation check as Step 0b**

At the top of `decision-engine.md`, before "Step 1 — Gather Candidates", add:

```markdown
## Step 0b — Carryover Escalation Check

Run at session start for each concept in `schedule.yaml > carryover_concepts`. Check `sessions_in_carryover` against the escalation ladder.

### Prerequisite Carryover (is_prerequisite: true)

| Sessions | Stage | Action |
|----------|-------|--------|
| 1-5 | normal | Normal carryover allocation. No special treatment. |
| 6 | flagged | Flag in system-health. Review error patterns: same mistake repeating → explanation isn't landing. Varied errors → insufficient practice volume. |
| 8 | approach_changed | Try a different instructional approach. If rule-based before, try example-based. If drills, try communicative. If always same context, try new context. Update `current_approach` in schedule. |
| 10 | sprint | Auto-trigger a 2-session mini-sprint on this concept. Log sprint rationale in adjustment_log. |
| 12+ | surfaced | Surface to learner: "This concept is taking longer than expected. That's normal — [concept] is genuinely hard for English speakers. Let's talk about what's not clicking." Use learner input to redesign approach. |

### Non-Prerequisite Carryover (is_prerequisite: false)

| Sessions | Stage | Action |
|----------|-------|--------|
| 1-8 | normal | Normal allocation. |
| 9 | flagged | Flag in system-health. Review error patterns. |
| 12 | approach_changed | Try different approach. |
| 15 | sprint or deprioritize | If learner is progressing well on prerequisites, deprioritization is valid. Otherwise, mini-sprint. |
| 18+ | surfaced | Surface to learner. |

**Key principle:** Each escalation step changes the approach, not just the intensity. Repeating the same thing harder doesn't fix a stall.

**Integration with interleaving:** Stalled carryover concepts should be prioritized as interleaving targets in Step 5b. Practicing them woven into other activities (rather than in isolation) may help with transfer.

After checking, increment `sessions_in_carryover` for each carryover concept that was practiced this session. Update `escalation_stage` if a threshold was crossed.
```

- [ ] **Step 3: Update Step 2 — add vocabulary GAP scoring**

In the GAP scoring table in Step 2, add a note after the table:

```markdown
### Vocabulary GAP Scoring

Vocabulary clusters with `error_tracking` data are now scored using the same GAP formula as grammar:

| State | Score |
|-------|-------|
| error_rate_production > 0.30 | 8 |
| error_rate_production 0.15-0.30 | 5 |
| error_rate_production < 0.15 | 3 |
| error_rate_production null (unobserved) | 4 |
| No error_tracking data and last_observed null | 2 |

**Weight vocabulary GAP below grammar GAP** — vocabulary production errors are observed less frequently (incidentally during conversation, not in dedicated drills). Specific weight ratio should be tuned after 20+ sessions of real data. Until then, treat vocabulary GAP as roughly 70% of equivalent grammar GAP when comparing cross-category candidates.

Vocabulary clusters where `passive_known` has increased in the last 2 sessions (input exposure logged) receive a +2 TOPIC_BOOST — the learner has encountered these words in context and is primed for production.
```

- [ ] **Step 4: Update Step 6b — reference input orchestration guide**

In Step 6b, replace the current content:

Replace:
```markdown
## Step 6b — Media Selection for Homework

When assigning listening or reading homework, select from `curriculum/media-bank.yaml` using:

1. **Phase filter:** Only resources whose `phase_range` includes the learner's current phase
2. **Dialect preference:** Prefer resources matching `target_dialect` from learner-profile. Accept neutral-dialect resources.
3. **Topic alignment:** Score by overlap with the current weekly narrow topic (direct match > adjacent > unrelated)
4. **Level calibration:** Match to `receptive_skills.listening.current_level` or `receptive_skills.reading.current_level` — assign at-level or one step above
5. **Freshness:** Avoid assigning the same channel/source 3 sessions in a row. Rotate.

If multiple resources tie, prefer the one the learner has engaged with before (check `resource-tracker.yaml` engagement data). For new learners, start with the most accessible option in each category.
```

With:
```markdown
## Step 6b — Input Selection for Homework

**Full protocol in `curriculum/tutor-guides/input-orchestration.md` Section 1.** Summary:

1. **Level filter:** Resources whose `level_range` includes current listening/reading level or one above (i+1)
2. **Dialect preference:** Prefer resources matching `target_dialect`. Accept neutral-dialect.
3. **Topic alignment:** Score by overlap with weekly narrow topic
4. **Freshness:** Check `resource-tracker.yaml` — prefer resources not assigned in last 2 sessions. Avoid `learner_engagement: reluctant`.
5. **Autonomy:** Prescriptive (Phase A-B), guided (Phase C), autonomous (Phase D)
6. **Time budget:** Fit to remaining homework time after Anki and writing assignments. Input share increases with phase.

For L2-L3 prescriptive assignments, check `media-bank.yaml > prescriptive_episodes` for entries with `content_summary` — these enable informed comprehension debriefs.

**Vocabulary boost:** If a vocabulary cluster's `passive_known` increased recently (from input exposure), boost that cluster for production practice. Input primes production.
```

- [ ] **Step 5: Commit**

```bash
git add curriculum/tutor-guides/decision-engine.md
git commit -m "feat: add interleaving, carryover escalation, and vocabulary scoring to decision engine"
```

---

### Task 8: CLAUDE.md Session Flow and Guardrail Updates

Wire the new systems into the main session protocol.

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add input debrief to Review & Warm-up**

In `CLAUDE.md`, in the "Review & Warm-up (5-8 min)" section, add after "Review homework: what was completed, how did it go, verify claims naturally.":

```markdown
- Input debrief: if listening/reading was assigned, run comprehension debrief per `curriculum/tutor-guides/input-orchestration.md` Section 2 (3-5 min). Record in session log `input_reviewed`.
```

- [ ] **Step 2: Add input selection to Checkout**

In the Checkout section, add after "For media homework, consult `curriculum/media-bank.yaml` for specific recommendations matching phase, dialect, and topic.":

```markdown
- For input homework, follow `curriculum/tutor-guides/input-orchestration.md` Section 1. Select level-appropriate resources from media-bank using `level_range`, topic alignment, and learner autonomy level. For L2-L3, use prescriptive episodes with content summaries when available.
```

- [ ] **Step 3: Add input-orchestration.md to conditional loads**

In the "Step 4 — Check for conditional loads" section, add after "Standard session (post-onboarding)? Also read `curriculum/tutor-guides/decision-engine.md`":

```markdown
- Standard session (post-onboarding)? Also read `curriculum/tutor-guides/input-orchestration.md`
```

- [ ] **Step 4: Add carryover escalation to guardrails**

In the Guardrails section, add after the line about never advancing phases:

```markdown
- **Monitor carryover escalation.** Check `sessions_in_carryover` for each carryover concept against the escalation ladder in `decision-engine.md` Step 0b. Change approach, don't just increase intensity.
```

- [ ] **Step 5: Update State Updates section**

In the State Updates section, update item 2d and item 4:

Replace:
```markdown
2d. Update `receptive_skills` if listening/reading homework was reviewed
```

With:
```markdown
2d. Update `receptive_skills` with input debrief data: `hours_at_level`, `hours_total`, `comprehension_quality`, `level_up_evidence` if relevant. Apply level changes per input-orchestration.md Section 4.
2e. Update vocabulary cluster `passive_known` and `weak_production` from input debrief vocabulary extraction
2f. Update vocabulary cluster `error_tracking` fields if production errors were observed during conversation
```

Replace:
```markdown
4. Update `state/resource-tracker.yaml` if resource engagement changed
```

With:
```markdown
4. Update `state/resource-tracker.yaml`: increment `hours_logged` and `sessions_completed` for debriefed resources, update `comprehension_trend`, `learner_engagement`
4b. Update `sessions_in_carryover` and `escalation_stage` for each carryover concept practiced
```

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "feat: integrate input orchestration into session flow and guardrails"
```

---

### Task 9: Validation Script Updates

Add validation checks for the new schema fields.

**Files:**
- Modify: `scripts/validate-state.py`

- [ ] **Step 1: Add receptive skills level validation**

In `scripts/validate-state.py`, add a new check function after the existing check functions (before `main()`):

```python
def check_receptive_skills(skill_map):
    """Validate receptive_skills schema and level values."""
    rs = skill_map.get('receptive_skills', {})
    if not rs:
        warn('receptive_skills section missing from skill-map')
        return

    valid_listening = {'L1', 'L2', 'L3', 'L4', 'L5'}
    valid_reading = {'R1', 'R2', 'R3', 'R4', 'R5'}
    valid_quality = {None, 'gist', 'main_ideas', 'details', 'inference'}
    valid_lookup = {None, 'frequent', 'occasional', 'rare', 'none'}

    listening = rs.get('listening', {})
    reading = rs.get('reading', {})

    level = listening.get('current_level')
    if level and level not in valid_listening:
        fail(f'receptive_skills.listening.current_level invalid: {level} (expected L1-L5)')
    else:
        pass_('receptive_skills.listening.current_level valid')

    quality = listening.get('comprehension_quality')
    if quality not in valid_quality:
        fail(f'receptive_skills.listening.comprehension_quality invalid: {quality}')

    level = reading.get('current_level')
    if level and level not in valid_reading:
        fail(f'receptive_skills.reading.current_level invalid: {level} (expected R1-R5)')
    else:
        pass_('receptive_skills.reading.current_level valid')

    lookup = reading.get('lookup_frequency')
    if lookup not in valid_lookup:
        fail(f'receptive_skills.reading.lookup_frequency invalid: {lookup}')

    # Hours should be non-negative
    for skill_name, skill in [('listening', listening), ('reading', reading)]:
        for field in ['hours_at_level', 'hours_total']:
            val = skill.get(field, 0)
            if val is not None and val < 0:
                fail(f'receptive_skills.{skill_name}.{field} is negative: {val}')

    # hours_total >= hours_at_level
    for skill_name, skill in [('listening', listening), ('reading', reading)]:
        total = skill.get('hours_total', 0) or 0
        at_level = skill.get('hours_at_level', 0) or 0
        if at_level > total:
            warn(f'receptive_skills.{skill_name}.hours_at_level ({at_level}) > hours_total ({total})')
```

- [ ] **Step 2: Add vocabulary error tracking validation**

Add another check function:

```python
def check_vocab_error_tracking(skill_map):
    """Validate vocabulary cluster error_tracking fields."""
    vocab = skill_map.get('vocabulary', {})
    for cluster_id, cluster in vocab.items():
        et = cluster.get('error_tracking')
        if et is None:
            warn(f'vocabulary.{cluster_id} missing error_tracking section')
            continue

        rate = et.get('error_rate_production')
        if rate is not None:
            if not (0.0 <= rate <= 1.0):
                fail(f'vocabulary.{cluster_id}.error_tracking.error_rate_production out of range: {rate}')

        if not isinstance(et.get('common_errors', []), list):
            fail(f'vocabulary.{cluster_id}.error_tracking.common_errors should be a list')

    pass_(f'vocabulary error_tracking validated for {len(vocab)} clusters')
```

- [ ] **Step 3: Add resource-tracker validation**

Add another check function:

```python
def check_resource_tracker(resource_tracker):
    """Validate resource-tracker schema."""
    summary = resource_tracker.get('input_summary', {})
    if not summary:
        warn('resource-tracker missing input_summary section')
        return

    valid_listening = {'L1', 'L2', 'L3', 'L4', 'L5'}
    valid_reading = {'R1', 'R2', 'R3', 'R4', 'R5'}

    cl = summary.get('current_listening_level')
    if cl and cl not in valid_listening:
        fail(f'resource-tracker.input_summary.current_listening_level invalid: {cl}')

    cr = summary.get('current_reading_level')
    if cr and cr not in valid_reading:
        fail(f'resource-tracker.input_summary.current_reading_level invalid: {cr}')

    for field in ['total_listening_hours', 'total_reading_hours']:
        val = summary.get(field, 0)
        if val is not None and val < 0:
            fail(f'resource-tracker.input_summary.{field} is negative: {val}')

    resources = resource_tracker.get('resources', [])
    valid_types = {'listening', 'reading', 'mixed'}
    valid_trends = {None, 'improving', 'stable', 'declining'}
    valid_engagement = {None, 'enthusiastic', 'neutral', 'reluctant'}

    for r in resources:
        name = r.get('name', 'unknown')
        if r.get('type') not in valid_types:
            fail(f'resource-tracker resource "{name}" has invalid type: {r.get("type")}')
        if r.get('comprehension_trend') not in valid_trends:
            warn(f'resource-tracker resource "{name}" has invalid comprehension_trend')
        if r.get('learner_engagement') not in valid_engagement:
            warn(f'resource-tracker resource "{name}" has invalid learner_engagement')

    pass_(f'resource-tracker validated ({len(resources)} resources)')
```

- [ ] **Step 4: Register new checks in main()**

In the `main()` function, add calls to the new check functions. Find where existing skill-map checks are called and add after them:

```python
    # After existing skill-map checks:
    check_receptive_skills(skill_map)
    check_vocab_error_tracking(skill_map)

    # After resource-tracker is loaded (add loading if not already present):
    resource_tracker = load_yaml('state/resource-tracker.yaml')
    if resource_tracker:
        check_resource_tracker(resource_tracker)
```

- [ ] **Step 5: Run validation**

Run:
```bash
python3 scripts/validate-state.py
```

Expected: All new checks PASS (state files were updated in Task 2 to match new schemas).

- [ ] **Step 6: Commit**

```bash
git add scripts/validate-state.py
git commit -m "feat: add validation for receptive skills, vocabulary tracking, and resource-tracker"
```

---

### Task 10: Vault Generation Updates

Add input progress display to the vault dashboard.

**Files:**
- Modify: `scripts/generate-vault.py`

- [ ] **Step 1: Add input progress to Home.md dashboard**

In `scripts/generate-vault.py`, find the `generate_home()` function. In the dashboard content, add an "Input Progress" section after the existing active concepts section. The exact insertion point depends on the function structure — look for where it builds the main dashboard content string.

Add this section to the Home.md content:

```python
    # Input Progress section
    listening = skill_map.get('receptive_skills', {}).get('listening', {})
    reading = skill_map.get('receptive_skills', {}).get('reading', {})

    listening_level = listening.get('current_level', 'L1')
    reading_level = reading.get('current_level', 'R1')
    listening_quality = listening.get('comprehension_quality', 'not assessed')
    reading_quality = reading.get('comprehension_quality', 'not assessed')
    listening_hours = listening.get('hours_total', 0)
    reading_hours = reading.get('hours_total', 0)

    content += f"""
## Input Progress

| Skill | Level | Comprehension | Total Hours |
|-------|-------|--------------|-------------|
| Listening | {listening_level} | {listening_quality or 'not assessed'} | {listening_hours} |
| Reading | {reading_level} | {reading_quality or 'not assessed'} | {reading_hours} |

"""
```

- [ ] **Step 2: Add input progress to Roadmap.md**

In the `generate_roadmap()` function, add a section showing the listening and reading level progression. After the phase flowcharts, add:

```python
    # Input levels section
    content += """
## Input Levels

### Listening
L1 (Simplified) → L2 (Slow/Structured) → L3 (Moderate) → L4 (Natural + Subtitles) → L5 (Native Media)

### Reading
R1 (Cognates/Labels) → R2 (Graded Readers L1) → R3 (Graded L2-3) → R4 (Authentic Articles) → R5 (Literature)

"""
    # Mark current levels
    listening_level = skill_map.get('receptive_skills', {}).get('listening', {}).get('current_level', 'L1')
    reading_level = skill_map.get('receptive_skills', {}).get('reading', {}).get('current_level', 'R1')
    content += f"**Current:** Listening {listening_level} | Reading {reading_level}\n\n"
```

- [ ] **Step 3: Update frontmatter in session updates**

In the `run_session()` function, ensure that when updating generated files, the receptive skills data is included in frontmatter updates for relevant notes. Check if the function updates the Home.md — if so, ensure it regenerates with the new input progress section.

The `run_session()` function likely calls `generate_home()` or similar. Verify that the Home.md regeneration picks up the new section automatically (it should, since we modified `generate_home()`).

- [ ] **Step 4: Test vault generation**

Run:
```bash
python3 scripts/generate-vault.py --full
```

Expected: Vault generates successfully. Check `vault/Home.md` contains the "Input Progress" section. Check `vault/Roadmap.md` contains the "Input Levels" section.

```bash
grep -A 5 "Input Progress" vault/Home.md
grep -A 5 "Input Levels" vault/Roadmap.md
```

- [ ] **Step 5: Commit**

```bash
git add scripts/generate-vault.py
git commit -m "feat: add input progress display to vault dashboard and roadmap"
```

---

### Post-Implementation Checklist

After all tasks are complete, verify:

- [ ] `python3 scripts/validate-state.py` passes with no failures
- [ ] `python3 scripts/generate-vault.py --full` generates vault successfully
- [ ] All YAML files parse: `python3 -c "import yaml; [yaml.safe_load(open(f)) for f in ['state/skill-map.yaml', 'state/resource-tracker.yaml', 'state/schedule.yaml', 'curriculum/listening-progression.yaml', 'curriculum/reading-progression.yaml', 'curriculum/media-bank.yaml']]"`
- [ ] `curriculum/tutor-guides/input-orchestration.md` exists and is referenced in CLAUDE.md conditional loads
- [ ] `curriculum/tutor-guides/decision-engine.md` contains Steps 0b, 5b, and updated 6b
- [ ] CLAUDE.md Review & Warm-up references input debrief
- [ ] CLAUDE.md Checkout references input-orchestration.md for input selection
- [ ] CLAUDE.md Guardrails includes carryover escalation monitoring
- [ ] CLAUDE.md State Updates includes items 2d-2f and 4b
