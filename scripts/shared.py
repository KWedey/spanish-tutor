"""Shared constants and helpers used across tutoring system scripts."""
import os
import re
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
# STATE_DIR defaults to <repo>/state but can be redirected via the
# TUTOR_STATE_DIR env var. This is the supported way to point validate-state.py
# (and other state-reading scripts) at a throwaway copy without touching live
# learner state — e.g. the corruption-stress harness in
# scripts/test-error-recovery.py runs the validator against a temp copy.
STATE_DIR = (Path(os.environ["TUTOR_STATE_DIR"]).resolve()
             if os.environ.get("TUTOR_STATE_DIR") else ROOT / "state")
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


def leading_header(text: str) -> str:
    """Return the top comment/blank-line block of a state/schedule YAML file (the
    ``# Schema:`` pointer header) so a read-modify-write preserves it instead of
    stripping it. Shared by every script that rewrites a state file in place
    (validate-state, check-session-log, recompute-metrics, update-fluency-tracking)."""
    out = []
    for ln in text.splitlines(keepends=True):
        if ln.lstrip().startswith("#") or not ln.strip():
            out.append(ln)
        else:
            break
    return "".join(out)


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


# ---------------------------------------------------------------------------
# StateStore — the portable storage seam (docs/engine-api.md)
# ---------------------------------------------------------------------------
#
# A session-log filename is <ISO-date>.yaml; list_sessions reports only files
# whose stem matches this pattern, so the sessions/archive/ subtree and any
# stray files under sessions/ are never mistaken for logs.

_SESSION_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class StateStore:
    """Filesystem-backed implementation of the engine-api StateStore interface.

    This is the storage *seam* the deterministic engine reads and writes state
    through — part of the host layer, not the engine kernel. The repo host is
    the filesystem: the five top-level documents live at
    ``<state_dir>/<doc>.yaml`` and per-day session logs at
    ``<state_dir>/sessions/<date>.yaml``. Every method is a thin wrapper over
    the module helpers already used throughout the scripts (:func:`load_yaml`,
    :func:`atomic_write`) — it adds no new persistence logic and changes no
    existing behavior.

    **Ports supply their own backend.** A web/mobile/cloud port re-implements
    these five methods against its own medium (SQLite, IndexedDB, a cloud KV
    store) and the engine keeps working unchanged, because nothing above this
    class assumes filesystem paths, a git checkout, or a working directory.
    The contract a port must preserve (docs/engine-api.md "StateStore
    interface")::

        load(doc_name)           -> dict | None   # None if absent
        save(doc_name, data)     -> None           # atomic write
        list_sessions()          -> list[str]       # session-log dates, sorted
        load_session(date)       -> dict | None
        save_session(date, data) -> None

    Args:
        state_dir: Root of the state tree. Defaults to the repo ``state/``
            (:data:`STATE_DIR`, itself redirectable via ``TUTOR_STATE_DIR``).
    """

    #: The five top-level state documents (docs/engine-api.md "State model").
    #: The per-day session log is the sixth document, reached through the
    #: session methods rather than by name.
    DOCS = (
        "learner-profile",
        "skill-map",
        "schedule",
        "resource-tracker",
        "system-health",
    )

    def __init__(self, state_dir: Path | str | None = None) -> None:
        self.state_dir = Path(state_dir) if state_dir is not None else STATE_DIR
        self.sessions_dir = self.state_dir / "sessions"

    # -- top-level documents -------------------------------------------------

    def _doc_path(self, doc_name: str) -> Path:
        return self.state_dir / f"{doc_name}.yaml"

    def load(self, doc_name: str) -> dict | None:
        """Return the parsed document, or None if the file is absent."""
        return load_yaml(self._doc_path(doc_name))

    def save(self, doc_name: str, data: dict) -> None:
        """Serialize *data* to ``<state_dir>/<doc_name>.yaml`` atomically."""
        self._write(self._doc_path(doc_name), data)

    # -- per-day session logs ------------------------------------------------

    def _session_path(self, session_date: str) -> Path:
        return self.sessions_dir / f"{session_date}.yaml"

    def list_sessions(self) -> list[str]:
        """Return session-log dates (ISO ``YYYY-MM-DD`` strings), sorted ascending.

        Only direct children of ``sessions/`` whose stem is a bare ISO date are
        reported — the ``archive/`` subtree and any stray files are ignored.
        Returns an empty list when the sessions directory does not exist yet.
        """
        if not self.sessions_dir.exists():
            return []
        return sorted(
            p.stem for p in self.sessions_dir.glob("*.yaml")
            if _SESSION_DATE_RE.match(p.stem)
        )

    def load_session(self, session_date: str) -> dict | None:
        """Return the session log for *session_date*, or None if absent."""
        return load_yaml(self._session_path(session_date))

    def save_session(self, session_date: str, data: dict) -> None:
        """Serialize the session log for *session_date* atomically."""
        self._write(self._session_path(session_date), data)

    # -- internal ------------------------------------------------------------

    @staticmethod
    def _write(path: Path, data: dict) -> None:
        """Atomically write *data* as YAML in the repo's serialization style."""
        atomic_write(
            path,
            yaml.dump(data, default_flow_style=False, allow_unicode=True,
                      sort_keys=False),
        )
