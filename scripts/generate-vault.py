#!/usr/bin/env python3
"""Generate Obsidian vault content from tutoring system state and curriculum files.

Modes:
  --full              Full generation (all vault content)
  --session --date    Per-session update (frontmatter + Roadmap only)
"""

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
CURRICULUM_DIR = ROOT / "curriculum"
VAULT_DIR = ROOT / "vault"

SKILL_MAP_PATH = STATE_DIR / "skill-map.yaml"
SCHEDULE_PATH = STATE_DIR / "schedule.yaml"

PHASE_DIR_MAP = {
    "A": "A-foundation",
    "B": "B-conversational",
    "C": "C-intermediate",
    "D": "D-advanced",
}

PHASE_DISPLAY = {
    "A": "Phase A - Foundation",
    "B": "Phase B - Conversational",
    "C": "Phase C - Intermediate",
    "D": "Phase D - Advanced",
}

TIER_DIR_MAP = {
    "1": "tier1-survival",
    "2": "tier2-daily-life",
    "3": "tier3-social",
    "4": "tier4-abstract",
}

TIER_DISPLAY = {
    "1": "Tier 1 - Survival",
    "2": "Tier 2 - Daily Life",
    "3": "Tier 3 - Social",
    "4": "Tier 4 - Abstract",
}

TIER_CATEGORY = {
    "1": "survival",
    "2": "daily-life",
    "3": "social",
    "4": "abstract",
}

STATUS_ICONS = {
    "unseen": "\u25CB",       # ○
    "introduced": "\u25D0",   # ◐
    "practicing": "\u25D1",   # ◑
    "acquired": "\u25CF",     # ●
    "automatic": "\u2605",    # ★
    "regressed": "\u27F2",    # ⟲
}

GENERATED_BANNER = "%%Auto-generated from tutor state. Edits will be overwritten.%%"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    """Load a YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def today_str() -> str:
    return date.today().isoformat()


def concept_id_to_title(concept_id: str) -> str:
    """Convert a concept ID like 'A-01-present-regular' to 'Present Regular'."""
    # Strip the phase prefix (e.g. "A-01-" or "A-00-")
    parts = concept_id.split("-", 2)
    if len(parts) >= 3:
        name_part = parts[2]
    else:
        name_part = concept_id
    return name_part.replace("-", " ").title()


def cluster_id_to_title(cluster_id: str) -> str:
    """Convert 'tier1-greetings-introductions' to 'Greetings Introductions'."""
    # Strip the tier prefix
    parts = cluster_id.split("-", 1)
    if len(parts) >= 2:
        name_part = parts[1]
    else:
        name_part = cluster_id
    return name_part.replace("-", " ").title()


def sound_id_to_title(sound_id: str) -> str:
    """Convert 'vowel-sounds' to 'Vowel Sounds'."""
    return sound_id.replace("-", " ").title()


def prereq_to_wikilink(prereq_id: str) -> str:
    """Convert a prerequisite concept ID to an Obsidian wiki-link."""
    return f"[[{concept_id_to_title(prereq_id)}]]"


def strip_source_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from source file content if present."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].lstrip("\n")
    return content


def read_source_file(path: Path) -> str:
    """Read a source curriculum file. Return placeholder if missing."""
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return strip_source_frontmatter(f.read())
    return f"*Source file not found: `{path.relative_to(ROOT)}`*\n"


def file_has_generated_marker(path: Path) -> bool:
    """Check if a file has 'generated: true' in its frontmatter."""
    if not path.exists():
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(1024)  # Only need to check the beginning
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                fm = yaml.safe_load(content[3:end])
                return isinstance(fm, dict) and fm.get("generated") is True
    except Exception:
        pass
    return False


def write_vault_file(path: Path, content: str, force: bool = False) -> None:
    """Write a vault file, creating parent directories as needed.

    Only overwrites if the file does not exist, is empty, or has the
    'generated: true' marker, unless force=True.
    """
    if path.exists() and not force and not file_has_generated_marker(path):
        # Protect hand-edited files
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def yaml_frontmatter(data: dict) -> str:
    """Render a dict as YAML frontmatter with --- delimiters.

    Uses manual serialization for deterministic field ordering.
    """
    lines = ["---"]
    for key, value in data.items():
        lines.append(f"{key}: {_yaml_value(value)}")
    lines.append("---")
    return "\n".join(lines)


def _yaml_value(value) -> str:
    """Format a single value for YAML frontmatter."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Only quote strings that might be misinterpreted by YAML parsers
        if value in ("true", "false", "null", "yes", "no", "") or \
           any(c in value for c in (":", "#", "[", "]", "{", "}", ",")):
            return f'"{value}"'
        return value
    if isinstance(value, list):
        if not value:
            return "[]"
        items = ", ".join(f'"{v}"' if isinstance(v, str) else _yaml_value(v) for v in value)
        return f"[{items}]"
    return str(value)


# ---------------------------------------------------------------------------
# Grammar note generation
# ---------------------------------------------------------------------------

def grammar_source_path(concept_id: str) -> Path:
    """Resolve a grammar concept ID to its curriculum source file path."""
    phase = concept_id[0]
    phase_dir = PHASE_DIR_MAP.get(phase, "")
    # Strip phase letter and dash to get the number-name portion
    file_stem = concept_id[2:]  # e.g. "01-present-regular"
    return CURRICULUM_DIR / "grammar" / phase_dir / f"{file_stem}.md"


def generate_grammar_note(concept_id: str, data: dict) -> tuple[Path, str]:
    """Generate a grammar note and return (output_path, content)."""
    phase = concept_id[0]
    title = concept_id_to_title(concept_id)
    source_path = grammar_source_path(concept_id)
    phase_display = PHASE_DISPLAY.get(phase, f"Phase {phase}")

    prereqs = data.get("prerequisites") or []
    prereq_links = [prereq_to_wikilink(p) for p in prereqs]

    status = data.get("status", "unseen")
    tags = ["grammar", f"phase-{phase.lower()}", status]

    fm = {
        "generated": True,
        "source": str(source_path.relative_to(ROOT)),
        "last_generated": today_str(),
        "concept_id": concept_id,
        "title": title,
        "phase": phase,
        "status": status,
        "error_rate_drills": data.get("error_rate_drills"),
        "error_rate_production": data.get("error_rate_production"),
        "error_trend": data.get("error_trend"),
        "last_practiced": data.get("last_practiced"),
        "practice_count": data.get("practice_count", 0),
        "integration_tested_with": data.get("integration_tested_with", []),
        "prerequisites": prereq_links,
        "tags": tags,
    }

    body = read_source_file(source_path)
    content = f"{yaml_frontmatter(fm)}\n{GENERATED_BANNER}\n\n{body}"

    output_path = VAULT_DIR / "Grammar" / phase_display / f"{title}.md"
    return output_path, content


# ---------------------------------------------------------------------------
# Vocabulary note generation
# ---------------------------------------------------------------------------

def vocab_source_path(cluster_id: str) -> Path:
    """Resolve a vocabulary cluster ID to its curriculum source file path."""
    # cluster_id like "tier1-greetings-introductions"
    tier_num = cluster_id[4]  # character after "tier"
    tier_dir = TIER_DIR_MAP.get(tier_num, "")
    # Cluster name is everything after "tierN-"
    cluster_name = cluster_id[6:]  # e.g. "greetings-introductions"
    return CURRICULUM_DIR / "vocabulary" / tier_dir / f"{cluster_name}.md"


def generate_vocab_note(cluster_id: str, data: dict) -> tuple[Path, str]:
    """Generate a vocabulary note and return (output_path, content)."""
    tier_num = cluster_id[4]
    title = cluster_id_to_title(cluster_id)
    source_path = vocab_source_path(cluster_id)
    tier_display = TIER_DISPLAY.get(tier_num, f"Tier {tier_num}")
    category = TIER_CATEGORY.get(tier_num, "unknown")

    status = data.get("status", "unseen")
    tags = ["vocabulary", f"tier-{tier_num}", category, status]

    fm = {
        "generated": True,
        "source": str(source_path.relative_to(ROOT)),
        "last_generated": today_str(),
        "cluster_id": cluster_id,
        "title": title,
        "tier": int(tier_num),
        "category": category,
        "status": status,
        "words_total": data.get("words_total", 0),
        "words_introduced": data.get("words_introduced", 0),
        "passive_known": data.get("passive_known", 0),
        "active_known": data.get("active_known", 0),
        "last_practiced": data.get("last_practiced"),
        "tags": tags,
    }

    body = read_source_file(source_path)
    content = f"{yaml_frontmatter(fm)}\n{GENERATED_BANNER}\n\n{body}"

    output_path = VAULT_DIR / "Vocabulary" / tier_display / f"{title}.md"
    return output_path, content


# ---------------------------------------------------------------------------
# Pronunciation note generation
# ---------------------------------------------------------------------------

def pronunciation_source_path(sound_id: str) -> Path:
    return CURRICULUM_DIR / "pronunciation" / f"{sound_id}.md"


def generate_pronunciation_note(sound_id: str, data: dict) -> tuple[Path, str]:
    """Generate a pronunciation note and return (output_path, content)."""
    title = sound_id_to_title(sound_id)
    source_path = pronunciation_source_path(sound_id)

    status = data.get("status", "unseen")
    tags = ["pronunciation", status]

    fm = {
        "generated": True,
        "source": str(source_path.relative_to(ROOT)),
        "last_generated": today_str(),
        "sound_id": sound_id,
        "title": title,
        "status": status,
        "last_practiced": data.get("last_practiced"),
        "tags": tags,
    }

    body = read_source_file(source_path)
    content = f"{yaml_frontmatter(fm)}\n{GENERATED_BANNER}\n\n{body}"

    output_path = VAULT_DIR / "Pronunciation" / f"{title}.md"
    return output_path, content


# ---------------------------------------------------------------------------
# Cultural note generation
# ---------------------------------------------------------------------------

def cultural_source_path(concept_id: str) -> Path:
    """Resolve a cultural concept ID (snake_case) to its curriculum source file."""
    # Convert snake_case key to kebab-case filename
    file_stem = concept_id.replace("_", "-")
    return CURRICULUM_DIR / "cultural" / f"{file_stem}.md"


def cultural_id_to_title(concept_id: str) -> str:
    """Convert 'register_shifting' to 'Register Shifting'."""
    return concept_id.replace("_", " ").title()


def generate_cultural_note(concept_id: str, data: dict) -> tuple[Path, str]:
    """Generate a cultural awareness note and return (output_path, content)."""
    title = cultural_id_to_title(concept_id)
    source_path = cultural_source_path(concept_id)

    status = data.get("status", "unseen")
    phase = data.get("introduced_at_phase", "B")
    tags = ["cultural", f"phase-{phase.lower()}", status]

    fm = {
        "generated": True,
        "source": str(source_path.relative_to(ROOT)),
        "last_generated": today_str(),
        "concept_id": concept_id,
        "title": title,
        "introduced_at_phase": phase,
        "status": status,
        "assessed_through": data.get("assessed_through", ""),
        "signs_of_acquisition": data.get("signs_of_acquisition", ""),
        "tags": tags,
    }

    body = read_source_file(source_path)
    content = f"{yaml_frontmatter(fm)}\n{GENERATED_BANNER}\n\n{body}"

    output_path = VAULT_DIR / "Cultural" / f"{title}.md"
    return output_path, content


# ---------------------------------------------------------------------------
# Home.md
# ---------------------------------------------------------------------------

def generate_home(schedule: dict, skill_map: dict) -> tuple[Path, str]:
    phase = schedule.get("current_phase", "A-foundation")
    week = schedule.get("current_week", 1)
    listening = skill_map.get('receptive_skills', {}).get('listening', {})
    reading = skill_map.get('receptive_skills', {}).get('reading', {})
    listening_level = listening.get('current_level', 'L1')
    reading_level = reading.get('current_level', 'R1')
    listening_quality = listening.get('comprehension_quality') or 'not assessed'
    reading_quality = reading.get('comprehension_quality') or 'not assessed'
    listening_hours = listening.get('hours_total', 0)
    reading_hours = reading.get('hours_total', 0)

    content = f"""\
---
generated: true
last_generated: "{today_str()}"
tags: ["dashboard"]
---
{GENERATED_BANNER}

# Spanish Fluency Tutor

## Right Now

| | |
|---|---|
| **Phase** | {phase} |
| **Week** | {week} |

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
| Listening | {listening_level} | {listening_quality} | {listening_hours} |
| Reading | {reading_level} | {reading_quality} | {reading_hours} |
"""
    return VAULT_DIR / "Home.md", content


# ---------------------------------------------------------------------------
# Roadmap.md
# ---------------------------------------------------------------------------

def generate_roadmap(skill_map: dict) -> tuple[Path, str]:
    grammar = skill_map.get("grammar", {})

    # Group concepts by phase
    phases: dict[str, list[tuple[str, dict]]] = {}
    for cid, data in grammar.items():
        phase = cid[0]
        phases.setdefault(phase, []).append((cid, data))

    lines = [
        "---",
        f'generated: true',
        f'last_generated: "{today_str()}"',
        'tags: ["roadmap"]',
        "---",
        GENERATED_BANNER,
        "",
        "# Roadmap",
        "",
    ]

    for phase_letter in ("A", "B", "C", "D"):
        concepts = phases.get(phase_letter, [])
        phase_name = PHASE_DISPLAY.get(phase_letter, f"Phase {phase_letter}")

        # Progress fraction
        total = len(concepts)
        acquired = sum(1 for _, d in concepts if d.get("status") in ("acquired", "automatic"))
        lines.append(f"## {phase_name}")
        lines.append(f"**Progress:** {acquired}/{total}")
        lines.append("")

        # Concept list with status icons
        for cid, data in concepts:
            status = data.get("status", "unseen")
            icon = STATUS_ICONS.get(status, "\u25CB")
            title = concept_id_to_title(cid)
            lines.append(f"- {icon} [[{title}]] *({status})*")
        lines.append("")

        # Mermaid flowchart for prerequisites
        lines.append("```mermaid")
        lines.append("flowchart LR")
        for cid, data in concepts:
            node_label = concept_id_to_title(cid)
            safe_id = cid.replace("-", "_")
            lines.append(f'    {safe_id}["{node_label}"]')
        # Collect all defined node IDs for this flowchart
        defined_nodes = {cid.replace("-", "_") for cid, _ in concepts}
        for cid, data in concepts:
            prereqs = data.get("prerequisites") or []
            for prereq in prereqs:
                src = prereq.replace("-", "_")
                dst = cid.replace("-", "_")
                # Only add arrow if source node is defined in this chart
                if src in defined_nodes:
                    lines.append(f"    {src} --> {dst}")
        lines.append("```")
        lines.append("")

    # Input levels section
    listening_level = skill_map.get('receptive_skills', {}).get('listening', {}).get('current_level', 'L1')
    reading_level = skill_map.get('receptive_skills', {}).get('reading', {}).get('current_level', 'R1')
    lines.append("## Input Levels")
    lines.append("")
    lines.append("### Listening")
    lines.append("L1 (Simplified) → L2 (Slow/Structured) → L3 (Moderate) → L4 (Natural + Subtitles) → L5 (Native Media)")
    lines.append("")
    lines.append("### Reading")
    lines.append("R1 (Cognates/Labels) → R2 (Graded Readers L1) → R3 (Graded L2-3) → R4 (Authentic Articles) → R5 (Literature)")
    lines.append("")
    lines.append(f"**Current:** Listening {listening_level} | Reading {reading_level}")
    lines.append("")

    return VAULT_DIR / "Roadmap.md", "\n".join(lines)


# ---------------------------------------------------------------------------
# Progress dashboards
# ---------------------------------------------------------------------------

def generate_grammar_progress() -> tuple[Path, str]:
    content = f"""\
---
generated: true
last_generated: "{today_str()}"
tags: ["progress", "grammar"]
---
{GENERATED_BANNER}

# Grammar Progress

```dataview
TABLE phase, status, error_rate_drills, error_rate_production, error_trend, practice_count, last_practiced
FROM "Grammar"
WHERE generated = true
SORT concept_id ASC
```
"""
    return VAULT_DIR / "Progress" / "Grammar Progress.md", content


def generate_vocab_progress() -> tuple[Path, str]:
    content = f"""\
---
generated: true
last_generated: "{today_str()}"
tags: ["progress", "vocabulary"]
---
{GENERATED_BANNER}

# Vocabulary Progress

```dataview
TABLE tier, category, status, words_total, words_introduced, passive_known, active_known, last_practiced
FROM "Vocabulary"
WHERE generated = true
SORT cluster_id ASC
```
"""
    return VAULT_DIR / "Progress" / "Vocabulary Progress.md", content


def generate_weekly_reports() -> tuple[Path, str]:
    content = f"""\
---
generated: true
last_generated: "{today_str()}"
tags: ["progress", "weekly"]
---
{GENERATED_BANNER}

# Weekly Reports

*Weekly reports will be generated here after each weekly review session.*
"""
    return VAULT_DIR / "Progress" / "Weekly Reports.md", content


def generate_milestones() -> tuple[Path, str]:
    content = f"""\
---
generated: true
last_generated: "{today_str()}"
tags: ["progress", "milestones"]
---
{GENERATED_BANNER}

# Milestones

*Milestones will be recorded here as you achieve them.*
"""
    return VAULT_DIR / "Progress" / "Milestones.md", content


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def generate_daily_note_template() -> tuple[Path, str]:
    content = """\
---
generated: true
date: "{{date}}"
session_number: null
energy_level: null
available_time: null
homework_completed: []
tags: ["daily"]
---

# {{date}} - Session Notes

## Homework Review

## Lesson Notes

## Conversation Practice

## Homework Assigned

- [ ]

## Reflection

"""
    return VAULT_DIR / "Templates" / "Daily Note.md", content


def generate_journal_template() -> tuple[Path, str]:
    content = """\
---
generated: true
date: "{{date}}"
prompt: ""
word_count: null
corrections: null
tags: ["journal"]
---

# Journal Entry - {{date}}

**Prompt:**

---


"""
    return VAULT_DIR / "Templates" / "Journal Entry.md", content


# ---------------------------------------------------------------------------
# Getting Started guide
# ---------------------------------------------------------------------------

def generate_getting_started() -> tuple[Path, str]:
    content = f"""\
---
generated: true
last_generated: "{today_str()}"
tags: ["guide"]
---
{GENERATED_BANNER}

# Getting Started

Welcome to your Spanish learning vault. This Obsidian vault is auto-generated from your tutoring system's curriculum and progress data.

## Setup

1. **Install Obsidian** from [obsidian.md](https://obsidian.md/) if you haven't already.
2. **Open this project as a vault**: In Obsidian, choose "Open folder as vault" and select the **project root directory** (not the `vault/` subdirectory). This allows Obsidian to see your journal and parking lot files alongside the generated vault content.
3. **Trust community plugins** when prompted by Obsidian.
4. **Install required plugins** (Settings > Community Plugins > Browse):
   - **Dataview** -- powers all dashboards, progress tables, and filtered views
   - **Homepage** -- opens Home.md automatically when you launch the vault (set to `vault/Home.md`)
5. **Install recommended plugins:**
   - **Terminal** (by polyipseity) -- embedded terminal panel so you can run tutoring sessions inside Obsidian. Open it with `Ctrl+`` `, type `claude`, and your tutor session runs alongside your vault notes in one window.
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
"""
    return VAULT_DIR / "Getting Started.md", content


# ---------------------------------------------------------------------------
# Full generation
# ---------------------------------------------------------------------------

def run_full(skill_map: dict, schedule: dict) -> None:
    """Generate all vault content."""
    files_written = 0

    # Grammar notes
    grammar = skill_map.get("grammar", {})
    for concept_id, data in grammar.items():
        path, content = generate_grammar_note(concept_id, data)
        write_vault_file(path, content, force=True)
        files_written += 1

    # Vocabulary notes
    vocabulary = skill_map.get("vocabulary", {})
    for cluster_id, data in vocabulary.items():
        path, content = generate_vocab_note(cluster_id, data)
        write_vault_file(path, content, force=True)
        files_written += 1

    # Pronunciation notes
    pronunciation = skill_map.get("pronunciation", {})
    for sound_id, data in pronunciation.items():
        path, content = generate_pronunciation_note(sound_id, data)
        write_vault_file(path, content, force=True)
        files_written += 1

    # Cultural awareness notes
    cultural = skill_map.get("cultural_awareness", {})
    for concept_id, data in cultural.items():
        path, content = generate_cultural_note(concept_id, data)
        write_vault_file(path, content, force=True)
        files_written += 1

    # Home
    path, content = generate_home(schedule, skill_map)
    write_vault_file(path, content, force=True)
    files_written += 1

    # Roadmap
    path, content = generate_roadmap(skill_map)
    write_vault_file(path, content, force=True)
    files_written += 1

    # Progress dashboards
    for gen_fn in (generate_grammar_progress, generate_vocab_progress,
                   generate_weekly_reports, generate_milestones):
        path, content = gen_fn()
        write_vault_file(path, content, force=True)
        files_written += 1

    # Templates
    for gen_fn in (generate_daily_note_template, generate_journal_template):
        path, content = gen_fn()
        write_vault_file(path, content, force=True)
        files_written += 1

    # Getting Started
    path, content = generate_getting_started()
    write_vault_file(path, content, force=True)
    files_written += 1

    print(f"Full generation complete: {files_written} files written to {VAULT_DIR}")


# ---------------------------------------------------------------------------
# Session update
# ---------------------------------------------------------------------------

def update_frontmatter_in_file(path: Path, updates: dict) -> bool:
    """Update specific frontmatter fields in an existing vault note.

    Returns True if the file was updated, False if skipped.
    """
    if not path.exists():
        return False
    if not file_has_generated_marker(path):
        return False

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return False

    end = content.find("---", 3)
    if end == -1:
        return False

    fm_str = content[3:end]
    fm = yaml.safe_load(fm_str) or {}
    body = content[end + 3:]

    fm.update(updates)
    fm["last_generated"] = today_str()

    new_content = yaml_frontmatter(fm) + body

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def run_session(skill_map: dict, session_date: str) -> None:
    """Per-session update: refresh frontmatter and regenerate Roadmap."""
    updates = 0

    # Update grammar notes
    grammar = skill_map.get("grammar", {})
    for concept_id, data in grammar.items():
        phase = concept_id[0]
        title = concept_id_to_title(concept_id)
        phase_display = PHASE_DISPLAY.get(phase, f"Phase {phase}")
        note_path = VAULT_DIR / "Grammar" / phase_display / f"{title}.md"

        status = data.get("status", "unseen")
        tags = ["grammar", f"phase-{phase.lower()}", status]
        prereqs = [prereq_to_wikilink(p) for p in (data.get("prerequisites") or [])]

        fm_updates = {
            "status": status,
            "error_rate_drills": data.get("error_rate_drills"),
            "error_rate_production": data.get("error_rate_production"),
            "error_trend": data.get("error_trend"),
            "last_practiced": data.get("last_practiced"),
            "practice_count": data.get("practice_count", 0),
            "integration_tested_with": data.get("integration_tested_with", []),
            "prerequisites": prereqs,
            "tags": tags,
        }
        if update_frontmatter_in_file(note_path, fm_updates):
            updates += 1

    # Update vocabulary notes
    vocabulary = skill_map.get("vocabulary", {})
    for cluster_id, data in vocabulary.items():
        tier_num = cluster_id[4]
        title = cluster_id_to_title(cluster_id)
        tier_display = TIER_DISPLAY.get(tier_num, f"Tier {tier_num}")
        note_path = VAULT_DIR / "Vocabulary" / tier_display / f"{title}.md"

        status = data.get("status", "unseen")
        category = TIER_CATEGORY.get(tier_num, "unknown")
        tags = ["vocabulary", f"tier-{tier_num}", category, status]

        fm_updates = {
            "status": status,
            "words_total": data.get("words_total", 0),
            "words_introduced": data.get("words_introduced", 0),
            "passive_known": data.get("passive_known", 0),
            "active_known": data.get("active_known", 0),
            "last_practiced": data.get("last_practiced"),
            "tags": tags,
        }
        if update_frontmatter_in_file(note_path, fm_updates):
            updates += 1

    # Update pronunciation notes
    pronunciation = skill_map.get("pronunciation", {})
    for sound_id, data in pronunciation.items():
        title = sound_id_to_title(sound_id)
        note_path = VAULT_DIR / "Pronunciation" / f"{title}.md"

        status = data.get("status", "unseen")
        tags = ["pronunciation", status]

        fm_updates = {
            "status": status,
            "last_practiced": data.get("last_practiced"),
            "tags": tags,
        }
        if update_frontmatter_in_file(note_path, fm_updates):
            updates += 1

    # Update cultural awareness notes
    cultural = skill_map.get("cultural_awareness", {})
    for concept_id, data in cultural.items():
        title = cultural_id_to_title(concept_id)
        note_path = VAULT_DIR / "Cultural" / f"{title}.md"

        status = data.get("status", "unseen")
        phase = data.get("introduced_at_phase", "B")
        tags = ["cultural", f"phase-{phase.lower()}", status]

        fm_updates = {
            "status": status,
            "introduced_at_phase": phase,
            "assessed_through": data.get("assessed_through", ""),
            "signs_of_acquisition": data.get("signs_of_acquisition", ""),
            "tags": tags,
        }
        if update_frontmatter_in_file(note_path, fm_updates):
            updates += 1

    # Regenerate Home and Roadmap
    schedule = load_yaml(SCHEDULE_PATH) if SCHEDULE_PATH.exists() else {}
    path, content = generate_home(schedule, skill_map)
    write_vault_file(path, content, force=True)

    path, content = generate_roadmap(skill_map)
    write_vault_file(path, content, force=True)

    print(f"Session update for {session_date}: {updates} notes updated, Home + Roadmap regenerated")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate Obsidian vault content from tutoring system state."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--full", action="store_true",
                       help="Full generation of all vault content")
    group.add_argument("--session", action="store_true",
                       help="Per-session update (frontmatter + Roadmap)")
    parser.add_argument("--date", type=str, default=None,
                        help="Session date (YYYY-MM-DD), required with --session")
    args = parser.parse_args()

    if args.session and not args.date:
        parser.error("--session requires --date YYYY-MM-DD")

    # Validate date format if provided
    if args.date:
        try:
            from datetime import datetime
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            parser.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD.")

    # Load state
    if not SKILL_MAP_PATH.exists():
        print(f"Error: skill-map not found at {SKILL_MAP_PATH}", file=sys.stderr)
        sys.exit(1)

    skill_map = load_yaml(SKILL_MAP_PATH)
    schedule = load_yaml(SCHEDULE_PATH) if SCHEDULE_PATH.exists() else {}

    if args.full:
        run_full(skill_map, schedule)
    elif args.session:
        run_session(skill_map, args.date)


if __name__ == "__main__":
    main()
