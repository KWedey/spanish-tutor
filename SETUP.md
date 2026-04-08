# Setup

## Prerequisites

- Python 3.6+ (for utility scripts)
- Git

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/init-student.py` | Reset learner state to blank templates | `python3 scripts/init-student.py [--force]` |
| `scripts/validate-state.py` | Validate state file integrity | `python3 scripts/validate-state.py [--verbose]` |
| `scripts/generate-vault.py` | Generate/update Obsidian vault | `python3 scripts/generate-vault.py --full` or `--session --date YYYY-MM-DD` |
| `scripts/migrate-state.py` | Run schema migrations | `python3 scripts/migrate-state.py [--dry-run]` |

## Obsidian Setup

See `vault/Getting Started.md` after running `python3 scripts/generate-vault.py --full`.

## First Session

Open a Claude Code session in this directory. The tutor will detect it's the first session and guide you through setup.
