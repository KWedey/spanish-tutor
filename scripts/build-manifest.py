#!/usr/bin/env python3
"""Build curriculum/manifest.yaml — the machine-readable index of every teachable concept.

Scans the curriculum tree (grammar, vocabulary, pronunciation, cultural) and emits one
manifest entry per concept with a stable id, H1 title, category, phase-or-tier, repo-relative
path, prerequisites (grammar only), and the l1-interference pattern ids that preempt it.

Output is deterministic — fixed category order, ids sorted within each category, stable key
order, no YAML anchors — so regeneration is byte-for-byte diff-stable. See docs/engine-api.md:
the manifest is the curriculum package index a port bundles as versioned content.

Id conventions (aligned with state/skill-map.template.yaml concept keys):
  grammar        A-00-communication-repair .. D-06-nuanced-connectors  (phase + filename stem)
  vocabulary     vocab-t1-greetings-introductions .. vocab-t4-...       (tier + cluster slug)
  pronunciation  vowel-sounds, rr-trill, ...                            (filename stem)
  cultural       register_shifting, politeness_formulas, ...            (underscored stem)

Usage:
  build-manifest.py               # write curriculum/manifest.yaml (default)
  build-manifest.py -o PATH       # write to a different path (used by the idempotency test)
  build-manifest.py --stdout      # print to stdout, write nothing
  build-manifest.py --check       # exit 1 if curriculum/manifest.yaml is stale (CI drift guard)
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

from shared import (ROOT, CURRICULUM_DIR, PHASE_DIRS, TIER_DIRS,
                    load_yaml, atomic_write, green, red)

MANIFEST_PATH = CURRICULUM_DIR / "manifest.yaml"
L1_PATH = CURRICULUM_DIR / "l1-interference.yaml"

SCHEMA_VERSION = 1

HEADER = """\
# Curriculum Manifest — machine-readable index of every teachable concept.
#
# GENERATED FILE — do not edit by hand. Regenerate with:
#   .venv/bin/python scripts/build-manifest.py
#
# One entry per teachable concept across the grammar, vocabulary, pronunciation, and
# cultural tracks. Consumed as the curriculum package index (see docs/engine-api.md). Ids
# align with state/skill-map.template.yaml concept keys for grammar and cultural. Entries are
# emitted in a fixed category order (grammar, vocabulary, pronunciation, cultural), sorted by
# id within each category, so regeneration is diff-stable.
"""

# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------
#
# A grammar concept ID is "<phase>-<NN>-<slug>" — a slug is lowercase letters and hyphens
# only (no digits), which lets us harvest real prereq ids from a free-text Prerequisites line
# while ignoring bare phase-number mentions like "A-00 communication repair assumed".
_CONCEPT_ID_RE = re.compile(r"[A-D]-\d{2}-[a-z][a-z-]*")
_PREREQ_LINE_RE = re.compile(r"(?im)^\s*-?\s*Prerequisites:(.*)$")
# Pronunciation files carry a "## Phase" section whose body reads "Phase B — ...".
_PRON_PHASE_RE = re.compile(r"(?m)^Phase\s+([A-D])\b")
# Cultural (and grammar) files carry a "When to Teach" bullet "- Phase: C (...)".
_COLON_PHASE_RE = re.compile(r"(?m)^\s*-?\s*Phase:\s*([A-D])\b")


def _read_h1(path: Path) -> str:
    """Return the file's H1 title (first '# ' line), stripped of the marker."""
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    raise ValueError(f"No H1 title found in {path}")


def _relpath(path: Path) -> str:
    """Repo-relative POSIX path (portable across host filesystems)."""
    return path.relative_to(ROOT).as_posix()


def _parse_prereqs(path: Path) -> list[str]:
    """Extract grammar prerequisite ids from a grammar file's Prerequisites line.

    Returns [] when the line says None / [] / is absent. Only tokens shaped like a full
    grammar id (phase-NN-slug) are captured, so parenthetical prose is ignored.
    """
    m = _PREREQ_LINE_RE.search(path.read_text(encoding="utf-8"))
    if not m:
        return []
    return _CONCEPT_ID_RE.findall(m.group(1))


def _parse_phase(path: Path, patterns) -> str:
    """Return the phase letter (A-D) declared in *path* using the first matching pattern."""
    text = path.read_text(encoding="utf-8")
    for pat in patterns:
        m = pat.search(text)
        if m:
            return m.group(1)
    raise ValueError(f"No phase declaration found in {path}")


# ---------------------------------------------------------------------------
# Per-category entry builders
# ---------------------------------------------------------------------------

def _grammar_entries() -> list[dict]:
    base = CURRICULUM_DIR / "grammar"
    entries = []
    for phase, dirname in PHASE_DIRS.items():
        for md in sorted((base / dirname).glob("*.md")):
            entries.append({
                "id": f"{phase}-{md.stem}",
                "category": "grammar",
                "phase": phase,
                "title": _read_h1(md),
                "path": _relpath(md),
                "prerequisites": _parse_prereqs(md),
                "l1_interference": [],
            })
    return entries


def _vocabulary_entries() -> list[dict]:
    base = CURRICULUM_DIR / "vocabulary"
    entries = []
    for tier, dirname in TIER_DIRS.items():
        for md in sorted((base / dirname).glob("*.md")):
            entries.append({
                "id": f"vocab-t{tier}-{md.stem}",
                "category": "vocabulary",
                "tier": int(tier),
                "title": _read_h1(md),
                "path": _relpath(md),
                "prerequisites": [],
                "l1_interference": [],
            })
    return entries


def _pronunciation_entries() -> list[dict]:
    base = CURRICULUM_DIR / "pronunciation"
    entries = []
    for md in sorted(base.glob("*.md")):
        entries.append({
            "id": md.stem,
            "category": "pronunciation",
            "phase": _parse_phase(md, [_PRON_PHASE_RE, _COLON_PHASE_RE]),
            "title": _read_h1(md),
            "path": _relpath(md),
            "prerequisites": [],
            "l1_interference": [],
        })
    return entries


def _cultural_entries() -> list[dict]:
    base = CURRICULUM_DIR / "cultural"
    entries = []
    for md in sorted(base.glob("*.md")):
        entries.append({
            "id": md.stem.replace("-", "_"),
            "category": "cultural",
            "phase": _parse_phase(md, [_COLON_PHASE_RE, _PRON_PHASE_RE]),
            "title": _read_h1(md),
            "path": _relpath(md),
            "prerequisites": [],
            "l1_interference": [],
        })
    return sorted(entries, key=lambda e: e["id"])


# ---------------------------------------------------------------------------
# L1-interference cross-reference
# ---------------------------------------------------------------------------

def _attach_l1_interference(entries: list[dict]) -> None:
    """Append preempting l1-interference pattern ids to each concept's l1_interference list.

    A pattern's ``preempt_at`` targets either a grammar concept id directly, or a vocabulary
    cluster in skill-map form (``tierN-slug``, which maps to this manifest's ``vocab-tN-slug``).
    preempt_at values that target neither (e.g. ``vocabulary-introduction``, ``media-bank:*``)
    are left unmapped by design.
    """
    data = load_yaml(L1_PATH) or {}
    patterns = data.get("interference_patterns") or []

    target_map: dict[str, dict] = {}
    for e in entries:
        if e["category"] == "grammar":
            target_map[e["id"]] = e
        elif e["category"] == "vocabulary":
            # vocab-tN-slug -> tierN-slug (the l1-interference preempt_at form)
            target_map[e["id"].replace("vocab-t", "tier", 1)] = e

    for p in patterns:
        pid = p.get("id")
        target = p.get("preempt_at")
        entry = target_map.get(target)
        if entry is not None and pid:
            entry["l1_interference"].append(pid)

    for e in entries:
        e["l1_interference"] = sorted(e["l1_interference"])


# ---------------------------------------------------------------------------
# Build + render
# ---------------------------------------------------------------------------

def build_manifest() -> dict:
    """Scan the curriculum tree and return the manifest document (dict)."""
    entries: list[dict] = []
    entries += _grammar_entries()
    entries += _vocabulary_entries()
    entries += _pronunciation_entries()
    entries += _cultural_entries()
    _attach_l1_interference(entries)
    return {"schema_version": SCHEMA_VERSION, "concepts": entries}


class _NoAliasDumper(yaml.SafeDumper):
    """Never emit YAML anchors/aliases — keeps repeated empty lists inline and diff-stable."""

    def ignore_aliases(self, data):
        return True


def render(doc: dict) -> str:
    """Serialize the manifest document to its canonical, deterministic YAML text."""
    body = yaml.dump(
        doc,
        Dumper=_NoAliasDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=4096,
    )
    return HEADER + body


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build curriculum/manifest.yaml — the curriculum concept index."
    )
    parser.add_argument("-o", "--output", type=Path, default=MANIFEST_PATH,
                        help="Output path (default: curriculum/manifest.yaml)")
    parser.add_argument("--stdout", action="store_true",
                        help="Print the manifest to stdout instead of writing a file")
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if curriculum/manifest.yaml is stale (write nothing)")
    args = parser.parse_args()

    content = render(build_manifest())

    if args.check:
        current = MANIFEST_PATH.read_text(encoding="utf-8") if MANIFEST_PATH.exists() else None
        if current == content:
            print(green(f"manifest up to date ({MANIFEST_PATH.relative_to(ROOT)})"))
            return 0
        print(red(f"manifest is STALE: {MANIFEST_PATH.relative_to(ROOT)} differs from a fresh "
                  "build. Regenerate with: .venv/bin/python scripts/build-manifest.py"))
        return 1

    if args.stdout:
        sys.stdout.write(content)
        return 0

    atomic_write(args.output, content)
    n = content.count("\n- id:")
    print(green(f"Wrote {args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output} "
                f"({n} concepts)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
