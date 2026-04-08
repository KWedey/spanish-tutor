# Maintenance Mode Guide

Loaded when: `autonomy_level` is `maintenance` in schedule.yaml. The learner has completed Phase D and met their graduation criteria.

## Goal

Prevent skill decay while respecting the learner's reduced time commitment. The learner has earned autonomy — sessions are now driven by their interests and real-world needs, not a curriculum.

## Session Cadence

| Weeks post-graduation | Cadence |
|----------------------|---------|
| 1-4 | Weekly (30 min) |
| 5-12 | Biweekly (30-45 min) |
| 13+ | On-demand (learner initiates) |

Cadence accelerates back to weekly if regression is detected.

## Session Structure (30-45 min)

### 1. Check-In (5 min)
- How has Spanish been going since last session?
- Any real-world encounters? (If yes → real-world-debrief.md takes over)
- Check parking lot for accumulated questions

### 2. Maintenance Spot-Check (10 min)
- Select 3-4 concepts from across all phases for spot-checking via conversation
- Prioritize concepts that were hardest to acquire (longest time in "practicing")
- Prioritize concepts not practiced in 30+ days
- If regression detected: flag it, schedule focused practice for next session

### 3. Interest-Driven Practice (15-25 min)
- Learner chooses the topic — their interests drive the session
- Advanced conversation, debate, storytelling, media discussion
- Fluency activities from fluency-activities.md
- New vocabulary introduced organically (not from curriculum queue)

### 4. Checkout (5 min)
- Light homework only: one listening/reading assignment, Anki review
- No mandatory assignments — learner self-directs at this stage

## Decision Engine Adaptation

In maintenance mode, the decision engine scoring changes:
- **NEED:** All concepts score 0-2 (maintenance only). No unseen concepts are introduced unless the learner requests them.
- **DECAY:** Primary driver. Concepts not practiced in 30+ days get DECAY score 7-9.
- **GAP:** Only triggers if regression detected (score 10 for regressed concepts).
- **TOPIC_BOOST:** Replaced by LEARNER_INTEREST — whatever the learner wants to discuss gets priority.

## Regression Handling

| Severity | Trigger | Response |
|----------|---------|----------|
| Minor | 1-2 concepts show error_rate > 15% | Address in spot-check, increase cadence to weekly for 2 sessions |
| Moderate | 3-5 concepts regressed | Return to weekly cadence, run abbreviated phase assessment |
| Severe | 6+ concepts regressed OR current-phase prerequisites regressed | Suggest returning to active learning (exit maintenance mode), set autonomy_level back to guided |

## State Updates

- Session logs follow the standard schema but with `session_type: maintenance`
- Skill-map updates focus on regression detection (spot-check results)
- system-health tracks: `maintenance_sessions_total`, `regressions_detected_in_maintenance`
- Weekly summaries are written monthly instead of weekly

## Re-Engagement Triggers

If the learner hasn't initiated a session in 30+ days:
- The system cannot reach out (it's passive)
- On next session: treat as a return session (load return-session.md) with maintenance context
- Run diagnostic appropriate to gap length
- Consider whether to exit maintenance mode based on results

## Graduation Check

Every 4 maintenance sessions, briefly revisit graduation criteria:
- Is the learner still meeting their target level?
- Have their goals changed?
- Do they want to set new goals (e.g., target a higher CEFR level)?
- If new goals set: exit maintenance, re-enter active learning at appropriate phase
