# Setup

## Prerequisites

| Requirement | Details |
|------------|---------|
| **Claude Code** | [claude.ai/download](https://claude.ai/download) — requires a Pro or Max subscription |
| **Python 3.6+** | For utility scripts. Check with `python3 --version` |
| **Git** | To clone the repo and receive curriculum updates |
| **Obsidian** *(optional)* | [obsidian.md](https://obsidian.md) — visual progress dashboard |

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url>
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

## First Session

See [STUDENT-GUIDE.md](STUDENT-GUIDE.md) for a full overview of how the system works, what tools you'll use, and what to expect over time.
