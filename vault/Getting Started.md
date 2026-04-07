---
generated: true
last_generated: "2026-04-06"
tags: ["guide"]
---
%%Auto-generated from tutor state. Edits will be overwritten.%%

# Getting Started

Welcome to your Spanish learning vault. This Obsidian vault is auto-generated from your tutoring system's curriculum and progress data.

## Setup

1. **Install Obsidian** from [obsidian.md](https://obsidian.md/) if you haven't already.
2. **Open this vault**: In Obsidian, choose "Open folder as vault" and select the `vault/` directory.
3. **Install community plugins** (recommended):
   - **Dataview** (required for dashboards) -- enables the live queries on Home, Progress, and Roadmap pages.
4. **Set Home as your start page**: Settings > Core Plugins > enable "Home" and set to `Home.md`.

## Orientation

| Section | What's There |
|---------|-------------|
| **Home** | Dashboard with active concepts, homework, quick links |
| **Grammar/** | One note per grammar concept, organized by phase |
| **Vocabulary/** | One note per vocabulary cluster, organized by tier |
| **Pronunciation/** | One note per sound |
| **Progress/** | Dataview-powered dashboards for grammar and vocabulary |
| **Roadmap** | Visual overview of all phases with prerequisite flowcharts |
| **Daily/** | Session notes (created per session) |
| **Templates/** | Templates for daily notes and journal entries |

## How It Works

- The vault is generated from `state/skill-map.yaml` and the curriculum files in `curriculum/`.
- Run `python3 scripts/generate-vault.py --full` to regenerate everything.
- Run `python3 scripts/generate-vault.py --session --date YYYY-MM-DD` after a session to update progress.
- Notes with `generated: true` in frontmatter will be overwritten on regeneration.
- You can safely create your own notes anywhere in the vault -- they will not be touched.

## Tags

The vault uses tags to help you filter and search:
- `grammar`, `vocabulary`, `pronunciation` -- skill type
- `phase-a` through `phase-d` -- grammar phase
- `tier-1` through `tier-4` -- vocabulary tier
- `unseen`, `introduced`, `practicing`, `acquired`, `automatic`, `regressed` -- status
