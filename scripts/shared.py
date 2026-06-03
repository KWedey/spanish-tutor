"""Shared constants and helpers used across tutoring system scripts."""
import os
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML required. Install with: pip install pyyaml")

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
CURRICULUM_DIR = ROOT / "curriculum"
VAULT_DIR = ROOT / "vault"
SCHEMAS_DIR = ROOT / "schemas"

# ---------------------------------------------------------------------------
# Directory mappings (curriculum phase/tier to filesystem)
# ---------------------------------------------------------------------------

PHASE_DIRS = {
    "A": "A-foundation",
    "B": "B-conversational",
    "C": "C-intermediate",
    "D": "D-advanced",
}

TIER_DIRS = {
    "1": "tier1-survival",
    "2": "tier2-daily-life",
    "3": "tier3-social",
    "4": "tier4-abstract",
}

# ---------------------------------------------------------------------------
# Terminal color helpers (ANSI; no-op when stdout is not a TTY)
# ---------------------------------------------------------------------------
#
# isatty is snapshotted at import time, matching the per-script blocks these
# replace. Scripts import only the colors they use.

_COLOR_ENABLED = sys.stdout.isatty()


def _ansi(code: str):
    return lambda t: f"\033[{code}m{t}\033[0m" if _COLOR_ENABLED else t


green = _ansi("32")
yellow = _ansi("33")
red = _ansi("31")
dim = _ansi("2")
bold = _ansi("1")


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict | None:
    """Load a YAML file and return its contents as a dict.

    Returns None if the file does not exist or contains invalid YAML.
    Returns {} for empty files or files containing only ``null``.
    """
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if data is not None else {}
    except yaml.YAMLError:
        return None


def load_yaml_strict(path: Path) -> dict:
    """Load a YAML file for a *write-back* path, failing loudly on corruption.

    Unlike :func:`load_yaml` — which collapses both a missing file and a
    corrupt file to ``None`` and lets ``load_yaml(p) or {}`` callers silently
    re-serialize a corrupt state file as ``{}`` (data loss) — this loader
    distinguishes the cases so a read-modify-write never erases unparseable
    state:

    * missing file → ``FileNotFoundError`` (a write-back read presupposes the
      file exists; absence is a real error, not "empty state")
    * corrupt YAML → ``yaml.YAMLError`` annotated with the offending path
    * empty file / ``null`` → ``{}`` (a valid, distinct-from-corrupt state)
    * otherwise → the parsed mapping

    Use this on any path that is loaded, mutated, and written back. Leave
    :func:`load_yaml` for read-only callers that tolerate missing/corrupt.
    """
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        # Annotate with the path while preserving the concrete subclass
        # (ScannerError/ParserError/...) so a caller that catches a specific
        # YAMLError subtype still matches.
        e.args = (f"Corrupt YAML in {path}: {e}",) + e.args[1:]
        raise
    return data if data is not None else {}


def atomic_write(path: Path, content: str) -> None:
    """Write *content* to *path* atomically.

    Writes to a temporary file in the same directory and then renames it to
    the target path.  On POSIX systems ``os.rename`` is atomic, so readers
    will never see a half-written file.
    """
    path = Path(path)
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.rename(tmp, path)
    except BaseException:
        # Clean up the temp file on any failure
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_schema(schema_name: str) -> dict:
    """Load a schema file from the schemas/ directory.

    Args:
        schema_name: Base name without extension, e.g. 'system-health'

    Returns:
        Parsed schema dict.

    Raises:
        FileNotFoundError: If the schema file does not exist.
        ValueError: If the schema file contains invalid YAML.
    """
    path = SCHEMAS_DIR / f"{schema_name}.schema.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    data = load_yaml(path)
    if data is None:
        raise ValueError(f"Schema file contains invalid YAML: {path}")
    return data


def get_required_fields(schema: dict) -> list[str]:
    """Extract top-level required field names from a schema's 'fields' section.

    Returns a list of field names where required=true.
    """
    fields = schema.get("fields", {})
    return [name for name, spec in fields.items()
            if isinstance(spec, dict) and spec.get("required")]


def get_field_default(spec: dict):
    """Return the schema field's declared default, or None if it has none."""
    return spec.get("default")


def yaml_value(value) -> str:
    """Format a single Python value for inline YAML output.

    Handles None, bool, int, float, str (with quoting for YAML-special
    characters), and lists (inline format). Used by both vault generation
    and template generation scripts.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Quote strings that might be misinterpreted by YAML parsers
        if value in ("true", "false", "null", "yes", "no", "") or \
           any(c in value for c in (":", "#", "[", "]", "{", "}", ",")):
            return f'"{value}"'
        return value
    if isinstance(value, list):
        if not value:
            return "[]"
        items = ", ".join(f'"{v}"' if isinstance(v, str) else yaml_value(v) for v in value)
        return f"[{items}]"
    if isinstance(value, dict):
        # Serialize nested dicts using PyYAML's inline flow style to produce
        # valid single-line YAML (e.g. {key: val, nested: {a: 1}}).
        return yaml.dump(value, default_flow_style=True, allow_unicode=True).strip()
    return str(value)
