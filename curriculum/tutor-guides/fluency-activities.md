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

### Phase D (fluency component every session)
- Every Phase-D session embeds a fluency **component** — part of the standard
  session, not a separately-routed session type. (Dedicated fluency-day
  *sessions*, routed by `route_session.py`, still cap at 3/week and skip
  consecutive days per CLAUDE.md Step 2.9; on the other days the fluency
  component is embedded in the standard session.)
- Metrics are the primary assessment tool.
- Correct only meaning-impeding errors during fluency work.
- Batch everything else for post-activity review.

## Activities

### Timed Monologue
- "Talk about X for 2 minutes without stopping. Don't worry about mistakes."
- Start with 1 minute in Phase B, increase to 2-3 minutes in Phase C-D.
- After: review together. Note pace, hesitation, risk-taking.
- Track improvement: same prompt repeated weeks later should show smoother delivery.

### Speed Translation
- Rapid-fire English to Spanish sentences, building reaction time.
- Start simple ("The house is big"), escalate ("If I had known, I would have gone").
- Goal is reducing think-time, not perfection.
- Note which structures cause the longest pauses — those need more practice.

### Shadowing
- Play a short clip (30-60 seconds) of a native speaker at appropriate pace.
- Learner speaks along simultaneously, mimicking rhythm and intonation.
- Don't worry about understanding every word — focus on the sound and flow.
- Repeat the same clip 3-5 times. Assign specific clips from Dreaming Spanish or podcasts.

### Retelling
- Listen to a short story or news segment (1-2 minutes).
- Retell it in Spanish. First attempt is rough.
- Listen again, retell again. Track the improvement between attempts.
- The delta between first and second attempt is more informative than either alone.

### Self-Narration (Homework)
- "While making breakfast tomorrow, narrate what you're doing in Spanish out loud."
- "On your commute, describe what you see around you."
- "Before bed, replay your day in Spanish."
- Zero friction, unlimited practice time. Builds fluency and reveals gaps.

## Fluency Metrics to Track

After each fluency activity, note in the session log:
- **Pace:** slow-deliberate, moderate, natural-flow
- **Hesitation:** frequent, occasional, rare
- **Self-correction:** high (good awareness) or low
- **Circumlocution:** how often they talk around unknown words
- **Risk-taking:** avoids unfamiliar structures vs tries and fails
- **English fallback:** how often they switch to English mid-sentence

## Fluency vs Accuracy Balance by Phase

| Phase | Balance | What this means |
|-------|---------|----------------|
| A-B | Accuracy-leaning | Build correct habits. Fluency activities 1x/week max. |
| C | Balanced | Timed monologues, reduced correction. Only correct repeated/high-impact errors. |
| D | Fluency-leaning | Smoothness, natural rhythm, spontaneity. Correct only meaning-impeding errors. |

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
