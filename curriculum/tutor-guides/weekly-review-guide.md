# Weekly Review Guide

Loaded when: Today is the learner's designated weekly review day (from learner-profile.yaml).

This replaces the standard session. It's equal parts progress review, system maintenance, and motivation.

## Flow

### 1. Progress Summary (10 min)
Read through the week's session logs. Summarize:
- Concepts practiced and their trajectory
- Vocabulary growth (both passive and active — note the production gap)
- Homework completion rate
- Journal quality improvement
- Fluency metric changes
- Notable improvements or persistent challenges

### 2. Write Weekly Summary
Write to `state/summaries/YYYY-WNN.yaml` following the schema in system-design.md.

### 3. Write Progress Report
Write to `progress-reports/YYYY-WNN.md` — human-readable, motivating, specific. This is for the learner to read. Include:
- Sessions completed, streak status
- What improved (with specific examples)
- What's still in progress
- Vocabulary and grammar stats
- What's ahead next week
- Highlight of the week (a specific moment or achievement)

### 4. Skill Map Audit
Review all "acquired" items. Randomly spot-check 2-3 by testing in conversation. If regression detected, update status.

**If `placement_validation.active` is true:** Skip the random spot-checks — the validation protocol is already systematically checking concepts. Instead, review the validation queue progress and report on validation findings so far (pass/downgrade counts, any adjustments made). The validation guide handles spot-checks for this session.

### 5. Resource Review
Are current resources at the right level? Any to swap? Check engagement rates in resource-tracker.yaml.

### 6. System Health Review
Check `state/system-health.yaml`:
- `concepts_requiring_reteach` rising? Advancement criteria may be too loose.
- `homework_completion_rate` dropping? Reduce load or add variety.
- `sessions_rated_too_easy` high? Push harder.

### 7. Next Week Planning
- Select next week's narrow topic from `curriculum/topic-bank.yaml`
- Align with current grammar focus and vocabulary cluster
- Plan rough focus areas for the week

### 8. Goal Check
Are we on track for stated milestones? If behind, discuss with learner — adjust timeline or intensity.

### 8a. Goal Tracking Update

Update `goal_tracking` in system-health.yaml:
1. Calculate `current_acquisition_rate` (concepts acquired in last 30 days / 4.3 weeks)
2. Count `concepts_remaining_for_next_phase` (current phase prerequisites not yet acquired)
3. Count `concepts_remaining_for_target_level` (all prerequisites between current phase and `target_level`)
4. Estimate `estimated_weeks_remaining` = concepts_remaining / current_acquisition_rate (rough — flag if rate is 0)
5. Set `primary_goal_progress`: on-track if estimate ≤ target date margin, behind if exceeding by 20%+, ahead if under by 20%+, at-risk if rate is 0 or declining
6. Update `milestone_progress` with any milestones achieved this week
7. Set `last_goal_review` to today's date

### 8b. Phase D Stall Detection

If the learner is in Phase D and `days_in_current_phase` (from system-health.yaml) exceeds 120 days without approaching graduation criteria:

1. Flag in system-health: `phase_d_stall: true`
2. Review: Are graduation criteria realistic? Has the learner's goal changed?
3. Discuss honestly with the learner: "You've been in Phase D for [N] weeks. Let's talk about what 'done' looks like for you."
4. Options: adjust graduation criteria, set a concrete target date, shift to maintenance mode if the learner is satisfied with current level, or identify specific blockers to address.
5. Re-check every 4 weeks until resolved.

### 9. Session Calibration Review

Review the week's `session_difficulty_rating` values. Track the `just_right_streak` counter in `schedule.yaml`:
- If all sessions this week were "just-right," increment the streak. At 3+ consecutive just-right ratings, note: current calibration is working. Do not adjust challenge level up or down unless the learner explicitly requests it or a phase transition is approaching.
- If any session was "too-easy" or "too-hard," reset the streak to 0. Two consecutive "too-easy" → plan to increase challenge next week. Two consecutive "too-hard" → plan to reduce load next week.
- Record the streak value and any calibration adjustment in the weekly summary.

### 10. Motivation Check
What's feeling good? What's feeling tedious? Check for plateau risk.

### 11. Maintenance
- Archive daily session logs older than 60 days to `state/sessions/archive/` (see Session Archive section below)
- Reset `fluency_days_this_week: 0` and increment `current_week` by 1 in schedule.yaml
- Update `input_hours` in learner-profile.yaml (sum listening/reading minutes from this week's assignments)
- Run `python3 scripts/validate-state.py` to catch any data inconsistencies
- Update schedule.yaml with next week's plan

### 12. Fun Activity
End with something enjoyable — a song, a short video, a game, casual conversation about something they care about. Weekly review should feel like a celebration, not an audit.

## Session Archive

During weekly review, archive session logs older than 60 days:

1. Move files from `state/sessions/` to `state/sessions/archive/`.
2. Archive = move, don't delete. Archived sessions are still accessible but not loaded at startup.
3. The 60-day window provides buffer for monthly reviews and regression analysis.
4. The tutor's startup protocol reads only the "3 most recent" sessions, so archiving adds no cognitive load.
