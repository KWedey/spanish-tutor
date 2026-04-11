"""Shared constants and helpers used across tutoring system scripts."""
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
# YAML helpers
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict:
    """Load a YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_schema(schema_name: str) -> dict:
    """Load a schema file from the schemas/ directory.

    Args:
        schema_name: Base name without extension, e.g. 'system-health'

    Returns:
        Parsed schema dict.
    """
    path = SCHEMAS_DIR / f"{schema_name}.schema.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    return load_yaml(path)


def get_required_fields(schema: dict) -> list[str]:
    """Extract top-level required field names from a schema's 'fields' section.

    Returns a list of field names where required=true.
    """
    fields = schema.get("fields", {})
    return [name for name, spec in fields.items()
            if isinstance(spec, dict) and spec.get("required")]


def get_field_default(spec: dict):
    """Return the default value for a schema field spec.

    Handles type coercion for null defaults represented as strings.
    """
    default = spec.get("default")
    if default is None:
        return None
    field_type = spec.get("type", "string")
    if field_type == "list" and default is None:
        return []
    if field_type == "map" and default is None:
        return {}
    return default
