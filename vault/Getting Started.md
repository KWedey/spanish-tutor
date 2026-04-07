---
generated: true
last_generated: "2026-04-07"
tags: ["guide"]
---
%%Auto-generated from tutor state. Edits will be overwritten.%%

# Getting Started

Welcome to your Spanish learning vault. This Obsidian vault is auto-generated from your tutoring system's curriculum and progress data.

> For a complete overview of the program — daily workflow, tools, what to expect — see **[[STUDENT-GUIDE]]** in the project root.

## Setup

1. **Install Obsidian** from [obsidian.md](https://obsidian.md/) if you haven't already.
2. **Open this project as a vault**: In Obsidian, choose "Open folder as vault" and select the **project root directory** (not the `vault/` subdirectory). This allows Obsidian to see your journal and parking lot files alongside the generated vault content.
3. **Trust community plugins** when prompted by Obsidian.
4. **Install required plugins** (Settings > Community Plugins > Browse):
   - **Dataview** -- powers all dashboards, progress tables, and filtered views
   - **Homepage** -- opens Home.md automatically when you launch the vault (set to `vault/Home.md`)
5. **Install recommended plugins:**
   - **Calendar** -- visual calendar in the sidebar showing session days. Set daily notes folder to `vault/Daily`.
   - **Templater** -- templates for journal entries. Set template folder to `vault/Templates`.

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
