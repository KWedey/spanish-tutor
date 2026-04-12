# Spanish Fluency Tutor

A personal Spanish tutor that runs in your terminal. It tracks your progress in plain YAML files, adapts sessions to your energy and goals, assigns homework using real tools (Anki, Dreaming Spanish, Language Transfer), and picks up exactly where you left off every session.

The tutor is [Claude Code](https://claude.ai/download) — Anthropic's CLI — running against a curated curriculum, a schema-validated learner state, and a 19-step post-session protocol. You own all the data. It lives in this folder. Nothing is uploaded anywhere.

## Quick start

```bash
# 1. Install Claude Code (Pro or Max subscription required)
#    https://claude.ai/download

# 2. Clone this repo
git clone https://github.com/KWedey/spanish-tutor.git language
cd language

# 3. Run setup — installs dependencies, initializes your learner state,
#    generates the Obsidian vault
python3 scripts/setup.py

# 4. Verify everything is ready
python3 scripts/preflight.py

# 5. Start your first session
claude
```

Your first session walks you through onboarding — goals, target dialect, schedule, tool setup. After that, sessions are ~30-45 minutes daily, with assigned homework between.

## What you get

- **Daily sessions** that adapt to your level, energy, and available time
- **Progress tracking** in readable YAML (`state/skill-map.yaml`, session logs, weekly summaries)
- **An Obsidian vault** with your roadmap, daily notes, grammar/vocab pages, and progress dashboards — auto-generated after each session
- **Homework** pulled from a curated media bank (shows, podcasts, graded readers, Anki decks) matched to your level
- **L1 interference tracking** — common English→Spanish mistakes are preempted before they become habits
- **Weekly reviews** that summarize progress and adjust the plan
- **A feedback channel** (`feedback/`) and a parking lot (`parking-lot.md`) for dropping notes between sessions

## Requirements

| Requirement | Details |
|-------------|---------|
| Claude Code | [claude.ai/download](https://claude.ai/download) — Pro or Max subscription |
| Python 3.10+ | For setup and maintenance scripts |
| Git | To clone and receive curriculum updates |
| Obsidian *(optional)* | [obsidian.md](https://obsidian.md) — visual progress dashboard |

## Documentation

- **[STUDENT-GUIDE.md](STUDENT-GUIDE.md)** — how the system works, what tools you'll use, what to expect over time, what to do when something goes wrong
- **[SETUP.md](SETUP.md)** — detailed setup, scripts reference, handing off to a new learner
- **[docs/first-session-dryrun.md](docs/first-session-dryrun.md)** — developer-only: manual checklist for a fresh-install QA pass before handing the project to a test user
- **[CLAUDE.md](CLAUDE.md)** — the system prompt driving the tutor (useful if you want to understand or modify the tutor's behavior)

## How your data works

Everything is local:

- `state/` — your learner profile, skill map, schedule, session logs, weekly summaries
- `journal/` — your daily Spanish journal entries
- `transcripts/` — full conversation transcripts of each session
- `progress-reports/` — human-readable weekly progress reports
- `vault/` — Obsidian-browsable dashboard (auto-generated)
- `feedback/` — your notes to the tutor about the program experience

All of these are gitignored by default — they won't accidentally leak if you push your clone somewhere. Curriculum updates (`git pull`) don't touch them.

## Handing off to a new learner

**Do not share the same folder between two learners.** Each learner gets their own fresh clone:

```bash
git clone https://github.com/KWedey/spanish-tutor.git spanish-for-alice
cd spanish-for-alice
python3 scripts/setup.py
```

See [SETUP.md](SETUP.md#handing-off-to-a-new-learner) for details.

## Status

This is a personal tutoring system built for a single learner and now being shared with a small test group. It's functional but not battle-tested across many users. If you hit a bug, drop a note in `feedback/` or open an issue.

## Getting Help

Hit a bug or have feedback? Open an issue at https://github.com/KWedey/spanish-tutor/issues, or drop a note in `feedback/` and mention it at the start of your next session.

## License

MIT — see [LICENSE](LICENSE).
