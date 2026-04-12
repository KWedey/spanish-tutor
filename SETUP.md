# Setup

## Prerequisites

| Requirement | Details |
|------------|---------|
| **Claude Code** | [claude.ai/download](https://claude.ai/download) — requires a Pro or Max subscription |
| **Python 3.10+** | For utility scripts (uses modern syntax: `dict | None`, `list[tuple]`). Check with `python3 --version` |
| **Git** | To clone the repo and receive curriculum updates |
| **Obsidian** *(optional)* | [obsidian.md](https://obsidian.md) — visual progress dashboard |

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/KWedey/spanish-tutor.git language
cd language

# 2. Run setup (installs dependencies, initializes state, generates vault)
python3 scripts/setup.py

# 3. Start your first session
claude
```

That's it. The tutor detects it's your first session and walks you through onboarding — your goals, experience level, schedule, and tool setup.

## What Setup Does

- Installs PyYAML if missing
- Creates blank learner state files from schemas
- Generates the Obsidian vault (grammar notes, vocabulary pages, roadmap)
- Validates everything is well-formed

## Obsidian (Optional)

After setup, you can open this folder as an Obsidian vault for a visual dashboard of your progress — grammar roadmap, vocabulary tracking, daily session notes.

1. Install [Obsidian](https://obsidian.md)
2. Open vault → select this project folder
3. Install the **Dataview** community plugin when prompted (used for progress tables)

You don't need Obsidian to use the system. Everything works from the terminal alone.

## Receiving Curriculum Updates

Your learning progress is stored locally and won't conflict with upstream changes. To pull curriculum updates:

```bash
git pull
python3 scripts/generate-vault.py --full   # regenerate vault with new content
```

Your state files, session logs, and journal entries are untouched.

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/setup.py` | One-command setup for new users | `python3 scripts/setup.py` |
| `scripts/init-student.py` | Reset learner state to blank templates | `python3 scripts/init-student.py [--force]` |
| `scripts/validate-state.py` | Validate state file integrity | `python3 scripts/validate-state.py [--verbose]` |
| `scripts/generate-vault.py` | Generate/update Obsidian vault | `python3 scripts/generate-vault.py --full` |
| `scripts/migrate-state.py` | Run schema migrations | `python3 scripts/migrate-state.py [--dry-run]` |

## Starting Over

To reset all progress and start fresh:

```bash
python3 scripts/init-student.py
python3 scripts/generate-vault.py --full
```

## Handing Off to a New Learner

The system stores one learner's state per checkout. If you want a second person to use it (a family member, a friend, a new student after an old one finishes), **do not share the same folder** — the tutor reads a single set of state files and can't tell two learners apart.

Instead, give them a fresh clone:

```bash
# Each learner gets their own copy
git clone https://github.com/KWedey/spanish-tutor.git spanish-for-alice
cd spanish-for-alice
python3 scripts/setup.py
```

Each clone has its own `state/`, `vault/`, `journal/`, `transcripts/`, `feedback/`, and `parking-lot.md`. Curriculum updates (`git pull`) still work in every clone — only the learner-specific files diverge.

**If you want to reuse an existing checkout for a new learner** (not recommended, but possible):

```bash
python3 scripts/init-student.py --force   # wipes state back to blank templates
python3 scripts/generate-vault.py --full  # regenerates the vault
```

This deletes the previous learner's profile, skill map, schedule, sessions, and vault content. Back up anything you want to keep first (`journal/`, `transcripts/`, `state/sessions/`) — `init-student.py --force` does not preserve it.

## First Session

See [STUDENT-GUIDE.md](STUDENT-GUIDE.md) for a full overview of how the system works, what tools you'll use, and what to expect over time.
