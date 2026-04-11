---
generated: true
last_generated: "2026-04-10"
tags: ["dashboard"]
---
%%Auto-generated from tutor state. Edits will be overwritten.%%

# Spanish Fluency Tutor

## Right Now

| | |
|---|---|
| **Phase** | A-foundation |
| **Week** | 1 |

## Today's Homework

```dataview
TASK
FROM "Daily"
SORT file.name DESC
LIMIT 1
```

## Active Concepts

```dataview
TABLE status, last_practiced, error_rate_production
FROM "Grammar" OR "Vocabulary"
WHERE status != "unseen" AND status != "automatic"
SORT status ASC
```

## Recent Milestones

*Milestones will appear here as you progress.*

## Quick Links

- [[Roadmap]]
- [[Parking Lot]]
- [[Progress/Grammar Progress|Grammar Progress]]
- [[Progress/Vocabulary Progress|Vocabulary Progress]]

## Input Progress

| Skill | Level | Comprehension | Total Hours |
|-------|-------|--------------|-------------|
| Listening | L1 | not assessed | 0 |
| Reading | R1 | not assessed | 0 |
