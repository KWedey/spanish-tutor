# Resource Ecosystem — External Tools & Integration

## Overview

The tutor orchestrates external tools and resources to fill gaps that conversational AI cannot cover alone. This document catalogs available resources, how they integrate with the tutoring system, and how the tutor selects and manages them.

The tutor's unique value isn't delivering content — it's **knowing what you need, picking the right resource, and adapting based on what happened.** The actual practice happens across a mix of tools, and the tutor ties them together.

---

## Resource Categories

### 1. Spaced Repetition / Vocabulary

#### Anki (Primary Recommendation)
- **What:** Flashcard app with spaced repetition algorithm
- **Cost:** Free (desktop), $25 (iOS), Free (Android via AnkiDroid)
- **Why Anki:** Best-in-class spacing algorithm, fully customizable, learner owns their data
- **Integration:**
  - Tutor tells the learner exactly which cards to create after each session
  - Tutor specifies card format: front = Spanish word/phrase, back = English + personal example sentence
  - Learner does daily reviews independently (10-15 min)
  - At session start, tutor asks: "Any Anki cards you kept missing?" → updates skill-map weak items
  - Optional: learner exports Anki stats periodically for tutor to analyze retention rates
- **Setup guidance:** Tutor walks learner through Anki setup in first or second session
- **When to assign:** Every session. SRS review is a daily non-negotiable.
- **Deck health management:**
  - Tutor monitors estimated deck size and daily review time via `state/system-health.yaml`
  - When daily review exceeds 20 min: reduce new cards to 3-5 per session
  - When daily review is under 10 min: can increase new card rate
  - Cards with intervals > 60 days and no recent errors: suggest retiring (remove from active rotation)
  - Retired vocabulary gets spot-checked during sessions periodically
  - If a retired word comes up wrong in conversation, it re-enters the deck
  - Maximum 10 new cards per session regardless of conditions

#### Clozemaster (Supplementary)
- **What:** Gap-fill sentences using real-world context
- **Cost:** Free tier (limited), Pro $8/month
- **Why:** Sees vocabulary in natural sentences rather than isolation
- **Integration:**
  - Tutor assigns when vocabulary is in "practicing" stage and needs more context exposure
  - Useful for reinforcing recently learned words through varied sentences
  - Learner reports which sentences were difficult → tutor extracts grammar or vocab gaps
- **When to assign:** 2-3x per week during vocabulary-heavy phases

---

### 2. Pronunciation

#### Speechling (Primary Recommendation)
- **What:** Record yourself, get feedback from human coaches within 24 hours
- **Cost:** Free tier (10 recordings/month), Unlimited $20/month
- **Why:** Only tool that provides human pronunciation feedback asynchronously
- **Integration:**
  - Tutor assigns specific sentences or phrases to record (targeted to current pronunciation focus)
  - Tutor asks for coach feedback at next session → updates pronunciation state
  - Particularly valuable for sounds that don't exist in English (rr, ñ, soft d/g)
- **Assignment format:** "Record yourself saying these 3 sentences on Speechling: [specific sentences that contain target sounds]"
- **When to assign:** 2-3x per week, more during pronunciation-focused periods

#### Forvo
- **What:** Native speaker audio dictionary — hear any word pronounced by real people
- **Cost:** Free
- **Why:** Reference tool for hearing correct pronunciation of specific words
- **Integration:**
  - Tutor assigns word lists to listen to on Forvo when introducing new vocabulary
  - Learner listens, imitates, and self-evaluates
  - "Listen to these 10 words on Forvo, practice each one 3 times"
- **When to assign:** When new vocabulary clusters are introduced

#### Pimsleur
- **What:** Audio-based course using call-and-response method
- **Cost:** $15-21/month (subscription), or per-level purchase
- **Why:** Excellent for building pronunciation rhythm, intonation, and listening in a structured format
- **Integration:**
  - Tutor assigns specific lessons that align with current grammar/vocab phase
  - Not a primary curriculum — used as supplementary pronunciation and listening practice
  - Good for commute/walk time when screen-free learning is needed
- **Limitation:** Fixed curriculum, can't customize. Tutor assigns it as a supplement, not a core track.
- **When to assign:** Early phases (A-B), especially for learners who commute

#### Local Whisper Transcription
- **What:** OpenAI's speech-to-text model, runs locally for free
- **Cost:** Free (local), requires initial setup
- **Why:** Tests intelligibility — if the machine understands you, humans probably will
- **Integration:**
  - A shell script in the repo records audio and transcribes via Whisper
  - Tutor prompts: "Record yourself describing X, paste the transcription"
  - Tutor compares transcription to intended message — discrepancies reveal pronunciation issues
  - Not a replacement for human feedback, but a quick daily check
- **Setup:** Tutor provides the script and walks through installation in early session
- **When to assign:** Can be used daily as a quick pronunciation self-check

---

### 3. Listening Comprehension

#### Dreaming Spanish (Primary for Beginners-Intermediate)
- **What:** YouTube channel and app with comprehensible input videos graded by level
- **Cost:** Free (YouTube), Premium $8/month (app with progress tracking)
- **Why:** Best implementation of comprehensible input theory for Spanish. Visual context supports understanding. Clearly graded levels.
- **Levels:** Superbeginner → Beginner → Intermediate → Advanced
- **Integration:**
  - Tutor assigns specific videos or levels matching learner's current comprehension
  - When possible, selects videos aligned with the weekly narrow topic
  - Assignment: "Watch 15 minutes of Dreaming Spanish at [level]. Don't pause, don't look things up."
  - Next session verification: "What were the videos about? Tell me in Spanish." (tests claim AND production)
  - If < 75% comprehension → step down a level. If > 90% → step up.
- **When to assign:** Daily listening homework in Phases A-C

#### Language Transfer (Primary for Grammar Intuition)
- **What:** Free audio course using Socratic method, builds Spanish from English cognates
- **Cost:** Free
- **Why:** Exceptional at building grammatical intuition. Teaches HOW to think in Spanish, not just what to memorize.
- **Integration:**
  - Tutor assigns 1-2 episodes at a time, sequenced with curriculum grammar progression
  - "Listen to Language Transfer episodes 12-13 (covers preterite basics). Pause when prompted and try to answer before the student in the recording does."
  - Tutor debriefs: "What clicked? What was confusing?"
- **Limitation:** Fixed sequence, 90 episodes total, covers roughly A1-B1 grammar
- **When to assign:** Phases A-B, 2-3 episodes per week alongside tutor sessions

#### News in Slow Spanish
- **What:** Current events podcast spoken at reduced speed with clear pronunciation
- **Cost:** Free (limited episodes), Premium $12/month
- **Why:** Bridge between graded content and native-speed media. Real topics, accessible speed.
- **Integration:**
  - Tutor assigns specific episodes related to the weekly narrow topic when possible
  - Assignment: "Listen to this episode. Write a 3-sentence summary in Spanish."
  - Tutor reviews the summary next session — assesses listening AND writing
- **When to assign:** Phase B-C, when learner outgrows beginner content but isn't ready for native speed

#### Radio Ambulante (Advanced Listening)
- **What:** NPR's Spanish-language narrative journalism podcast
- **Cost:** Free
- **Why:** Excellent long-form storytelling from across Latin America. Real Spanish at natural speed.
- **Integration:**
  - Tutor assigns episodes matching learner's interests and the weekly narrow topic
  - Assignment: "Listen to [episode]. What was the main story? What surprised you? Were there accents or words you couldn't understand?"
  - Introduces regional accent variation naturally
- **When to assign:** Phase C-D, when learner can handle native-speed content

#### TV Shows and Movies
- **What:** Spanish-language media for immersion
- **Cost:** Varies (Netflix, YouTube, etc.)
- **Recommended starters:**
  - *Extra en español* (YouTube, free) — beginner sitcom, designed for learners
  - *Destinos* (free, Annenberg Foundation) — classic learning telenovela
  - *Club de Cuervos* (Netflix) — intermediate+, Mexican comedy
  - *La Casa de Papel* (Netflix) — intermediate+, Castilian Spanish thriller
  - *Narcos* (Netflix) — intermediate+, Colombian Spanish (note: significant English too)
- **Integration:**
  - Phase A-B: Watch with Spanish subtitles (NOT English)
  - Phase C: Watch without subtitles, rewatch tricky scenes with subtitles
  - Phase D: No subtitles
  - Tutor assigns specific episodes, asks for summaries and discussion
- **When to assign:** Phase B onward, 1-2 episodes per week

#### Spanish-Language YouTube
- **What:** YouTube content in Spanish on topics the learner cares about
- **Cost:** Free
- **Why:** Most engaging content is content you'd watch anyway. Motivation + immersion.
- **Integration:**
  - During learner profile setup, tutor asks about interests/hobbies
  - Tutor suggests Spanish-language channels in those areas
  - Assignment: "Watch one video from [channel]. What did you learn?"
- **When to assign:** Phase B onward, as supplementary immersion

---

### 4. Reading

#### Olly Richards Graded Readers (Primary for Beginners)
- **What:** Short story collections written for Spanish learners, graded by CEFR level
- **Cost:** $10-15 per book (Kindle/paperback)
- **Why:** Natural storytelling at controlled difficulty. Vocabulary and grammar matched to level.
- **Titles by level:**
  - A1-A2: *Short Stories in Spanish for Beginners*
  - B1: *Short Stories in Spanish for Intermediate Learners*
  - B2: *Short Stories in Spanish for Advanced Learners* (despite title, fits intermediate-high)
- **Integration:**
  - Tutor assigns specific stories or chapters matching current phase
  - "Read story 3 tonight. Write down 5 words you didn't know and try to guess meaning from context."
  - Tutor reviews word lists and incorporates into Anki assignments
- **When to assign:** Phase A-C, 2-3 reading sessions per week

#### Beelinguapp
- **What:** App with side-by-side bilingual texts and audio
- **Cost:** Free tier (limited), Premium $3/month
- **Why:** Training wheels for reading — English right there when you need it, plus audio
- **Integration:**
  - Good for early Phase A when reading full Spanish text is daunting
  - Tutor assigns texts, instructs: "Try to read the Spanish side first. Only glance at English if truly stuck."
  - Phase B+: transition away from bilingual texts to Spanish-only
- **When to assign:** Phase A, transition to graded readers in Phase B

#### LingQ
- **What:** Import any Spanish text, app highlights unknown words and tracks vocabulary
- **Cost:** Free tier (limited), Premium $13/month
- **Why:** Makes any text into a learning tool. Tracks which words you know across all content.
- **Integration:**
  - Useful in Phase C+ when the learner graduates from graded readers to real content
  - Import news articles, blog posts, book chapters
  - Tutor suggests specific articles aligned with weekly narrow topic; LingQ provides vocabulary support
- **When to assign:** Phase C-D

#### Books in Spanish (Previously Read in English)
- **What:** Novels the learner has already read in English, now in Spanish translation
- **Cost:** Varies
- **Why:** Familiar plot reduces cognitive load — you're not guessing what's happening, just processing language
- **Good starters:** Harry Potter (*Harry Potter y la piedra filosofal*), The Little Prince (*El Principito*), any favorite novel
- **Integration:**
  - Tutor suggests when learner reaches solid B1
  - Assignment: "Read one chapter. Don't look up every word — only look up words that appear 3+ times."
  - Tutor discusses the chapter in Spanish next session
- **When to assign:** Phase B-C transition onward

#### News Articles
- **What:** Spanish-language news (BBC Mundo, El País, CNN en Español)
- **Cost:** Free (most)
- **Why:** Real-world content, current topics, formal register
- **Integration:**
  - Tutor assigns articles aligned with weekly narrow topic and learner interests
  - "Read this BBC Mundo article about [topic]. Summarize the main points in Spanish."
  - Good for introducing formal/written register and topic-specific vocabulary
- **When to assign:** Phase C-D

---

### 5. Writing

#### Journal (Built into the system)
- **What:** Daily writing practice in `journal/` directory
- **Cost:** Free
- **Why:** Writing is the highest-signal assessment tool — learner has time to think, so errors reveal genuine gaps. Also builds a tangible progress record.
- **Integration:**
  - Tutor assigns journal prompts aligned with current grammar focus and weekly topic
  - Prompts escalate with level:
    - Phase A: "Write 5 sentences about your family using ser and estar"
    - Phase B: "Write a paragraph about what you did last weekend"
    - Phase C: "Write a short email accepting a dinner invitation"
    - Phase D: "Summarize the Radio Ambulante episode and give your opinion"
  - Tutor reviews entries at session start — 2-3 corrections max, quality notes, trend tracking
  - Over months, the journal becomes a visible progress record the learner can look back on

#### LanguageTool (Supplementary)
- **What:** Free grammar and spell checker that supports Spanish
- **Cost:** Free (basic), Premium $5/month
- **Why:** Gives immediate feedback on writing without waiting for next session
- **Integration:**
  - Tutor suggests using LanguageTool while writing journal entries
  - Learner can self-correct before the tutor sees it — builds autonomy
  - Tutor still reviews for errors LanguageTool wouldn't catch (register, naturalness, word choice)
- **When to suggest:** Phase B onward

---

### 6. Speaking Practice (Human Partners)

#### italki (Primary Recommendation)
- **What:** Platform connecting learners with professional tutors and community tutors worldwide
- **Cost:** Community tutors $5-10/hour, Professional tutors $10-25/hour
- **Why:** Real human conversation practice at affordable rates. Learner chooses their tutor.
- **Integration:**
  - AI tutor prepares the learner before each italki session:
    - "This week, try to use subjunctive at least 3 times. Here are scenarios that will naturally prompt it."
    - "Tell your tutor about [weekly narrow topic] — this practices [grammar concept] and [vocabulary cluster]."
  - AI tutor debriefs after:
    - "How did the session go? What did your tutor correct? Were there moments you got stuck?"
    - Updates skill-map based on the report
  - Recommended frequency: 1-2x per week starting Phase B
- **When to assign:** Phase B onward

#### Tandem / HelloTalk (Free Alternative)
- **What:** Language exchange apps — you teach English, they teach Spanish
- **Cost:** Free (premium features available)
- **Why:** Free conversation practice, cultural exchange, text messaging for writing practice
- **Integration:**
  - Tutor suggests conversation topics aligned with weekly narrow topic and current learning goals
  - "This week on Tandem, try to have a conversation about your weekend plans (future tense practice)"
  - Learner reports corrections received from partners
- **Limitation:** Partner quality varies. Not a substitute for a trained tutor.
- **When to assign:** Phase A onward for text chat, Phase B onward for voice calls

#### Self-Talk and Narration
- **What:** Speaking Spanish to yourself during daily activities
- **Cost:** Free
- **Why:** The most underrated practice method. Zero friction, unlimited practice time. Builds fluency.
- **Integration:**
  - Tutor assigns specific narration tasks:
    - "While making breakfast tomorrow, narrate what you're doing in Spanish out loud."
    - "On your commute, describe what you see around you in Spanish (in your head or aloud)."
    - "Before bed, mentally replay your day in Spanish — what did you do today?"
  - No external feedback, but builds fluency and reveals gaps (you'll notice when you can't say something)
  - Excellent fluency-building exercise — the goal is continuous speech, not accuracy
- **When to assign:** Daily, from Phase A onward. Scales with the learner's level.

---

### 7. Fluency-Specific Tools

#### Shadowing Practice
- **What:** Listen to native speech and repeat simultaneously — builds rhythm, pace, and intonation
- **Cost:** Free (use any audio source)
- **How to do it:**
  1. Choose a short clip (30-60 seconds) of a native speaker at an appropriate pace
  2. Play it and speak along at the same time, mimicking rhythm and intonation
  3. Don't worry about understanding every word — focus on the sound and flow
  4. Repeat the same clip 3-5 times
- **Integration:**
  - Tutor assigns specific clips from Dreaming Spanish, podcasts, or shows
  - Best done with Phase B+ content where the learner recognizes most words
  - "Shadow the first minute of today's Dreaming Spanish video. Focus on matching the speaker's rhythm."
- **When to assign:** Phase B onward, 2-3x per week. Essential in Phase C-D for fluency building.

#### Timed Speaking Prompts
- **What:** Speak about a topic for a set time without stopping
- **Cost:** Free
- **How to do it:**
  1. Set a timer for 1-2 minutes
  2. Start talking about the prompt in Spanish
  3. Do NOT stop. If you don't know a word, talk around it. If you lose your train of thought, describe something else.
  4. Record yourself (optional but valuable)
  5. Listen back, note where you hesitated or switched to English
- **Integration:**
  - Tutor assigns prompts aligned with current grammar/vocabulary focus
  - "Set a timer for 2 minutes. Describe your ideal vacation. Don't stop talking."
  - Next session: tutor asks about the experience. "Where did you get stuck?"
- **When to assign:** Phase B onward for 1-minute prompts, Phase C+ for 2+ minutes

---

### 8. Grammar Reference

#### StudySpanish.com
- **What:** Free grammar explanations with quizzes organized by topic
- **Cost:** Free
- **Why:** Clear, comprehensive reference. Good when the learner wants to review a concept independently.
- **Integration:**
  - Tutor assigns specific pages when a concept needs reinforcement from a different angle
  - "If you want to review indirect object pronouns, read this page: [topic]. Then try the quiz."
  - Supplement to, not replacement for, the tutor's explanation

#### SpanishDict
- **What:** Dictionary + grammar guides + conjugation tables
- **Cost:** Free
- **Why:** Best all-in-one reference tool. Conjugation tables for every verb in every tense.
- **Integration:**
  - Tutor recommends as the learner's go-to dictionary and conjugation reference
  - "When you're writing or doing Anki, use SpanishDict to check conjugations."
  - Not assigned as homework — it's a tool the learner should bookmark and use freely

#### Kwiziq (Assessment)
- **What:** Adaptive grammar quizzes organized by CEFR level
- **Cost:** Free tier (limited), Premium $10/month
- **Why:** Provides objective grammar assessment by topic and level
- **Integration:**
  - Tutor assigns Kwiziq placement test at phase transitions for an objective benchmark
  - "Take the Kwiziq A2 quiz this week. Share your results so I can see if there are gaps we missed."
  - Results feed back into skill-map validation and calibration
- **When to assign:** At phase transitions (every few months) and when the tutor suspects calibration drift

---

### 9. Immersion and Culture

#### Changing Phone/Device Language
- **What:** Set phone, computer, or apps to Spanish
- **Cost:** Free
- **Why:** Passive daily exposure. Forces reading common UI words. Low effort, high exposure.
- **When to suggest:** Phase B onward. Phase A may be too frustrating.

#### Spanish Music with Lyrics
- **What:** Listen to Spanish music while reading lyrics (Genius, Musixmatch)
- **Cost:** Free (with existing music streaming)
- **Why:** Fun, memorable, exposes learner to colloquial language and culture
- **Integration:**
  - Tutor suggests artists matching learner's music taste and target dialect
  - Assignment: "Listen to [song] and read the lyrics. Pick 3 phrases you didn't know and add them to Anki."
  - Good low-energy homework option for tired days
  - Can align with weekly narrow topic (e.g., love song during emotions/feelings vocabulary week)

#### Language Reactor (Browser Extension)
- **What:** Dual subtitles for Netflix/YouTube + popup dictionary
- **Cost:** Free tier, Pro $6/month
- **Why:** Turns any streaming content into a learning tool
- **Integration:**
  - Tutor suggests installing at Phase B
  - Enables watching shows with both Spanish subtitles and English reference
  - Learner can pause and look up words without leaving the video

---

## Narrow Topic Alignment

When selecting resources for homework, the tutor prioritizes content aligned with the weekly narrow topic. This means the learner encounters the same vocabulary across multiple contexts within a week:

```
Example Week — Topic: "Childhood and Family"
Grammar Focus: Imperfect tense

Monday session homework:
  - Dreaming Spanish video about someone's childhood (listening + imperfect exposure)
  - Anki: 6 family/childhood vocabulary cards

Tuesday session homework:
  - Graded reader: story involving family dynamics (reading + vocabulary reinforcement)
  - Journal: "Describe what your weekends were like as a child" (writing + imperfect practice)

Wednesday session homework:
  - Speechling: record 3 sentences about childhood using imperfect (pronunciation + grammar)
  - Self-narration: describe a childhood memory aloud (fluency + imperfect)

Thursday session homework:
  - News in Slow Spanish: episode about family traditions in Latin America (listening + culture)
  - Anki review (includes this week's family vocabulary)

Friday session homework:
  - italki prep: "Tell your tutor about your family and childhood" (speaking + integration)
  - Music: listen to a nostalgic Spanish song, read lyrics (fun + vocabulary)
```

Same vocabulary (infancia, crecer, recuerdos, hermanos, costumbres, jugaba, vivía) appears in 6+ different contexts. This is far more effective than varied unrelated content.

---

## Resource Selection Algorithm

When the tutor assigns homework, it selects resources by:

1. **Narrow topic alignment:** Does the resource have content related to this week's theme?
2. **Skill match:** Does the resource target the skill that needs work?
   - **Passive vs active distinction:** If the learner has a large production gap (many words recognized but not produced), prioritize output-focused resources (speaking, writing). If they have recognition gaps, prioritize input-focused resources (listening, reading).
3. **Level match:** Is the resource at the right difficulty (85% comprehension target)?
4. **Dialect match:** Is the content in the learner's target dialect? (Check `curriculum/dialect-notes.yaml` — prefer Mexican Spanish media for a learner targeting Mexican Spanish)
5. **Already set up:** Has the learner already installed/subscribed to this tool? (Minimize friction)
6. **Engagement history:** Does the learner actually use this resource when assigned? (Check resource-tracker.yaml)
7. **Time fit:** Does the time requirement fit the learner's available homework time?
8. **Variety:** Has this resource been assigned too many times recently?
9. **Energy match:** Is this appropriate for the learner's current energy level?

If a resource has a completion rate below 50% over 2+ weeks, the tutor investigates: too hard? too boring? too time-consuming? It then swaps for an alternative.

---

## Resource Onboarding by Phase

### Phase A (First 2 weeks — stagger introduction)
Set up the core toolkit progressively:
- **Session 1-2:** Anki installed and first deck created
- **Session 3-4:** Dreaming Spanish bookmarked (Superbeginner level), SpanishDict bookmarked
- **Session 5-6:** Language Transfer queued (episodes 1-5), graded reader obtained (A1-A2)
- **Session 7-8:** Speechling account created
- **Session 9-10:** Whisper transcription script set up (optional, if learner is technical)

Don't introduce all tools at once — that's overwhelming. One new tool every 2-3 sessions.

### Phase B (When transitioning)
Add conversation and intermediate listening:
- [ ] italki or Tandem account set up
- [ ] First conversation session scheduled
- [ ] News in Slow Spanish bookmarked
- [ ] Language Reactor installed (if using Netflix)
- [ ] Phone language changed to Spanish (if ready)
- [ ] Journal writing begins (daily prompt from tutor)
- [ ] Shadowing practice introduced

### Phase C (When transitioning)
Add native content and formal assessment:
- [ ] Radio Ambulante subscribed
- [ ] LingQ set up (optional)
- [ ] Kwiziq account for grammar assessment
- [ ] First Spanish novel obtained
- [ ] Spanish YouTube channels identified in learner's interest areas
- [ ] LanguageTool suggested for journal self-correction
- [ ] Timed speaking prompts introduced (2-minute monologues)

### Phase D (When transitioning)
Shift to full immersion resources:
- [ ] Primary media consumption partially in Spanish
- [ ] Spanish-language news as regular reading
- [ ] DELE practice materials (if certification is a goal)
- [ ] Learner selecting own resources (autonomy progression)

---

## Resource Budget

Realistic monthly cost for a well-equipped learner:

| Resource | Cost | Essential? |
|----------|------|-----------|
| Anki | Free (desktop) | Yes |
| Speechling Free | Free | Yes |
| Dreaming Spanish | Free (YouTube) | Yes |
| Language Transfer | Free | Yes |
| SpanishDict | Free | Yes |
| Forvo | Free | Yes |
| Graded reader | $10-15 one-time | Yes |
| italki (4 sessions/month) | $20-60/month | Highly recommended |
| News in Slow Spanish | Free tier | Recommended |
| Anki (mobile) | $25 one-time (iOS) | Convenient |
| **Total minimum** | **~$10-15 one-time** | |
| **Total recommended** | **~$30-75/month + one-time book costs** | |

The system works entirely with free tools. Paid tools (primarily italki) significantly accelerate progress but aren't required.
