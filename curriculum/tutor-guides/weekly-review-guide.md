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

### 9. Motivation Check
What's feeling good? What's feeling tedious? Check for plateau risk.

### 10. Maintenance
- Archive daily session logs older than 60 days to `state/sessions/archive/` (see Session Archive section below)
- Reset `fluency_days_this_week: 0` in schedule.yaml
- Update `input_hours` in learner-profile.yaml (sum listening/reading minutes from this week's assignments)
- Run `python3 scripts/validate-state.py` to catch any data inconsistencies
- Update schedule.yaml with next week's plan

### 11. Fun Activity
End with something enjoyable — a song, a short video, a game, casual conversation about something they care about. Weekly review should feel like a celebration, not an audit.

## Session Archive

During weekly review, archive session logs older than 60 days:

1. Move files from `state/sessions/` to `state/sessions/archive/`.
2. Archive = move, don't delete. Archived sessions are still accessible but not loaded at startup.
3. The 60-day window provides buffer for monthly reviews and regression analysis.
4. The tutor's startup protocol reads only the "3 most recent" sessions, so archiving adds no cognitive load.
