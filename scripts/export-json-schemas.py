#!/usr/bin/env python3
"""Export the bespoke ``schemas/*.schema.yaml`` dialect to JSON Schema.

The tutor's state files are validated in-repo by ``scripts/validate-state.py``
against a hand-rolled schema dialect (``type`` / ``required`` / ``default`` /
``enum`` / ``description`` / ``children`` / ``item_shape``). That dialect is the
authoritative source of truth, but it is not consumable by off-the-shelf
tooling. This script projects it into **JSON Schema Draft 2020-12** so any port
target — a TypeScript web app, a mobile client — can validate state and generate
types from the same contracts (see ``docs/engine-api.md`` porting checklist:
"Ship ``schemas/json/`` (JSON Schema exports) for client-side validation /
typegen").

Dialect -> JSON Schema mapping (mirrors validate-state.py's schema walk):

* ``type: map`` with ``children``  -> ``{"type": "object", "properties": ...}``
* ``type: map`` with no ``children`` (free-form) -> ``{"type": "object",
  "additionalProperties": true}``
* ``type: list`` with ``item_shape``/``item_schema`` -> ``{"type": "array",
  "items": {"type": "object", ...}}``
* ``type: list`` with no item shape -> ``{"type": "array"}`` (unconstrained items)
* ``string``/``int``/``float``/``bool``/``date`` -> scalar JSON types
  (``date`` additionally carries ``"format": "date"``)
* ``enum``/``default``/``description`` -> carried through verbatim; an ``enum``
  that admits ``null`` widens the declared type to ``["<type>", "null"]`` so the
  exported schema is never internally contradictory.

Two top-level conventions are supported: schemas that wrap their fields in a
``fields:`` block (learner-profile, resource-tracker, schedule, session-log,
system-health) and skill-map, whose top-level keys ARE the schema content (a mix
of a scalar field plus per-entry template blocks and inline section maps). A node
is treated as a field spec when its ``type`` is a string; otherwise it is a bag
of field definitions and projects to an object.

Output is deterministic (``sort_keys``, two-space indent) so the committed
``schemas/json/*.schema.json`` artifacts diff cleanly and regenerate idempotently.
Run ``--check`` in CI to fail loudly when the committed artifacts drift from the
YAML source.
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML required. Install with: pip install pyyaml")

from shared import ROOT, SCHEMAS_DIR, atomic_write, dim, green, red, yellow

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_SUFFIX = ".schema.yaml"
JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"

# Base URI for each exported schema's ``$id``. Identity only — it need not
# resolve. A port can rebrand via ``--id-base`` (e.g. its own domain) without
# changing any of the schema bodies. A trailing slash is enforced in main().
DEFAULT_ID_BASE = "https://spanish-tutor.dev/schemas/"

# Bespoke scalar type name -> JSON Schema primitive type.
SCALAR_JSON_TYPES = {
    "string": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "date": "string",  # narrowed with format: date below
}

_TITLE_HEADER_RE = re.compile(r"^#\s*Schema:\s*(.+?)\s*$")


# ---------------------------------------------------------------------------
# Title extraction
# ---------------------------------------------------------------------------

def _title_from_header(text: str) -> str | None:
    """Return the ``# Schema: <Title>`` header title, or None if absent.

    PyYAML strips comments, so the human title lives only in the raw text.
    """
    for line in text.splitlines():
        m = _TITLE_HEADER_RE.match(line)
        if m:
            return m.group(1)
        if line.strip() and not line.lstrip().startswith("#"):
            break  # header block ended before a Schema: line
    return None


def _title_from_name(name: str) -> str:
    """Fallback title: 'skill-map' -> 'Skill Map'."""
    return " ".join(word.capitalize() for word in name.replace("_", "-").split("-"))


# ---------------------------------------------------------------------------
# Dialect -> JSON Schema conversion
# ---------------------------------------------------------------------------

def _is_field_spec(node) -> bool:
    """True when *node* is a field spec (a mapping whose ``type`` is a string).

    Distinguishes a field spec from a *bag* of field definitions. A bag that
    happens to contain a field literally named ``type`` (session-log's
    ``session_activities`` item shape does) has ``type`` mapping to a dict, not
    a string — so this check does not misclassify it.
    """
    return isinstance(node, dict) and isinstance(node.get("type"), str)


def _object_body(bag: dict) -> tuple[dict, list]:
    """Project a mapping of field-name -> (spec | nested bag) into an object body.

    Returns ``(properties, required)``. Only immediate children that are field
    specs marked ``required: true`` land in *required*; nested bags carry no
    ``required`` flag of their own. Declaration order is preserved (deterministic
    for a given source file) so the ``required`` array is stable across runs.
    """
    properties: dict = {}
    required: list = []
    for field_name, node in bag.items():
        properties[field_name] = _convert_node(node)
        if _is_field_spec(node) and node.get("required"):
            required.append(field_name)
    return properties, required


def _object_node(bag: dict) -> dict:
    """Build a JSON Schema object node from a bag of field definitions."""
    properties, required = _object_body(bag)
    node: dict = {"type": "object", "properties": properties}
    if required:
        node["required"] = required
    return node


def _convert_node(node):
    """Convert a top-level/nested node: a field spec, or a bag of field defs."""
    if _is_field_spec(node):
        return _convert_spec(node)
    if not isinstance(node, dict):
        raise ValueError(f"Expected a mapping node, got {type(node).__name__}: {node!r}")
    # A bag of field definitions (skill-map entry templates, inline section
    # maps, or a top-level `fields` block) projects to a JSON object.
    return _object_node(node)


def _convert_spec(spec: dict) -> dict:
    """Convert a single field spec (``type`` is a string) to a JSON Schema node."""
    field_type = spec["type"]
    if field_type == "map":
        children = spec.get("children")
        if children:
            node = _object_node(children)
        else:
            # Free-form map: arbitrary keys, unconstrained values.
            node = {"type": "object", "additionalProperties": True}
    elif field_type == "list":
        node = {"type": "array"}
        item_shape = spec.get("item_shape") or spec.get("item_schema")
        if item_shape:
            node["items"] = _object_node(item_shape)
    elif field_type in SCALAR_JSON_TYPES:
        node = {"type": SCALAR_JSON_TYPES[field_type]}
        if field_type == "date":
            node["format"] = "date"
    else:
        raise ValueError(f"Unknown schema type {field_type!r} in spec: {spec!r}")
    _attach_metadata(node, spec)
    return node


def _attach_metadata(node: dict, spec: dict) -> None:
    """Carry ``description``/``default``/``enum`` from *spec* onto *node*.

    An ``enum`` that admits ``null`` widens a scalar ``type`` to
    ``["<type>", "null"]`` so a nullable enum field is not self-contradictory.
    """
    if spec.get("description"):
        node["description"] = spec["description"]
    if "default" in spec:
        node["default"] = spec["default"]
    if "enum" in spec:
        enum = list(spec["enum"])
        node["enum"] = enum
        if None in enum and isinstance(node.get("type"), str):
            node["type"] = [node["type"], "null"]


def build_json_schema(name: str, schema_dict: dict, title: str,
                      id_base: str) -> dict:
    """Build the full JSON Schema document for one state schema.

    *schema_dict* is the parsed ``*.schema.yaml``. The root fields come from its
    ``fields:`` block, or — for skill-map, which has no wrapper — from the whole
    mapping.
    """
    root_bag = schema_dict.get("fields", schema_dict)
    properties, required = _object_body(root_bag)
    doc: dict = {
        "$schema": JSON_SCHEMA_DIALECT,
        "$id": f"{id_base}{name}.schema.json",
        "title": title,
        "type": "object",
        "properties": properties,
    }
    if required:
        doc["required"] = required
    return doc


# ---------------------------------------------------------------------------
# File-level export
# ---------------------------------------------------------------------------

def _schema_name(path: Path) -> str:
    """'schemas/skill-map.schema.yaml' -> 'skill-map'."""
    return path.name[: -len(SCHEMA_SUFFIX)]


def render_schema(path: Path, id_base: str) -> tuple[str, str]:
    """Render one ``*.schema.yaml`` file to ``(output_filename, json_text)``."""
    text = path.read_text(encoding="utf-8")
    schema_dict = yaml.safe_load(text)
    if not isinstance(schema_dict, dict):
        raise ValueError(f"Schema {path} did not parse to a mapping")
    name = _schema_name(path)
    title = _title_from_header(text) or _title_from_name(name)
    doc = build_json_schema(name, schema_dict, title, id_base)
    content = json.dumps(doc, indent=2, sort_keys=True) + "\n"
    return f"{name}.schema.json", content


def export_all(schemas_dir: Path = SCHEMAS_DIR, out_dir: Path | None = None,
               id_base: str = DEFAULT_ID_BASE,
               write: bool = True) -> list[tuple[Path, str]]:
    """Render every ``schemas/*.schema.yaml`` into *out_dir* (default ``json/``).

    Returns a list of ``(output_path, json_text)`` sorted by schema name. When
    *write* is False, nothing touches disk (used by ``--check``).
    """
    out_dir = out_dir if out_dir is not None else schemas_dir / "json"
    results: list[tuple[Path, str]] = []
    for path in sorted(schemas_dir.glob(f"*{SCHEMA_SUFFIX}")):
        out_name, content = render_schema(path, id_base)
        out_path = out_dir / out_name
        if write:
            atomic_write(out_path, content)
        results.append((out_path, content))
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _rel(path: Path) -> str:
    """Display *path* relative to the repo root when possible."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export schemas/*.schema.yaml to JSON Schema Draft 2020-12."
    )
    parser.add_argument("--schemas-dir", default=str(SCHEMAS_DIR),
                        help="Directory holding *.schema.yaml (default: schemas/)")
    parser.add_argument("--out-dir", default=None,
                        help="Output directory (default: <schemas-dir>/json)")
    parser.add_argument("--id-base", default=DEFAULT_ID_BASE,
                        help="Base URI for each schema's $id (default: %(default)s)")
    parser.add_argument("--check", action="store_true",
                        help="Verify committed JSON schemas are up to date; "
                             "exit 1 on drift without writing.")
    args = parser.parse_args()

    schemas_dir = Path(args.schemas_dir).resolve()
    out_dir = (Path(args.out_dir).resolve() if args.out_dir
               else schemas_dir / "json")
    id_base = args.id_base if args.id_base.endswith("/") else args.id_base + "/"

    if not schemas_dir.is_dir():
        print(red(f"Schemas directory not found: {schemas_dir}"))
        return 1

    results = export_all(schemas_dir, out_dir, id_base, write=not args.check)

    if not results:
        print(red(f"No {SCHEMA_SUFFIX} files found in {_rel(schemas_dir)}"))
        return 1

    if args.check:
        drift = []
        for out_path, content in results:
            existing = (out_path.read_text(encoding="utf-8")
                        if out_path.exists() else None)
            if existing != content:
                drift.append(out_path)
        if drift:
            print(red(f"JSON schemas are stale ({len(drift)} of {len(results)}):"))
            for out_path in drift:
                print(f"  {yellow(_rel(out_path))}")
            print(red("Run scripts/export-json-schemas.py to regenerate."))
            return 1
        print(green(f"All {len(results)} JSON schemas are up to date."))
        return 0

    print(green(f"Exported {len(results)} JSON schemas to {_rel(out_dir)}"))
    for out_path, _ in results:
        print(f"  {dim(_rel(out_path))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
