"""Tests for scripts/export-json-schemas.py — the JSON Schema export.

The exporter projects the bespoke ``schemas/*.schema.yaml`` dialect into JSON
Schema Draft 2020-12 (``schemas/json/*.schema.json``) so a port target can
validate state and generate types. These tests assert structural fidelity of
the projection; they deliberately do NOT depend on a ``jsonschema`` library —
the exporter only writes schema documents, so well-formedness is checked with
plain structural assertions.

scripts/ is placed on sys.path by tests/conftest.py — no per-file bootstrap.
"""
import importlib
import json
import subprocess
import sys

import pytest
import yaml

export_mod = importlib.import_module("export-json-schemas")

SCHEMA_SUFFIX = export_mod.SCHEMA_SUFFIX
DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"

SCHEMA_PATHS = sorted(export_mod.SCHEMAS_DIR.glob(f"*{SCHEMA_SUFFIX}"))
SCHEMA_NAMES = [export_mod._schema_name(p) for p in SCHEMA_PATHS]
COMMITTED_JSON_DIR = export_mod.SCHEMAS_DIR / "json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _yaml_top_bag(schema_dict: dict) -> dict:
    """The mapping of top-level fields, honoring both dialect conventions.

    Five schemas wrap their fields in ``fields:``; skill-map's top-level keys
    ARE the fields. This mirrors the exporter's own root selection but is
    re-derived independently here so the assertions are not tautological.
    """
    return schema_dict.get("fields", schema_dict)


def _expected_required(top_bag: dict) -> set:
    return {
        name for name, node in top_bag.items()
        if isinstance(node, dict) and isinstance(node.get("type"), str)
        and node.get("required")
    }


def _load_committed(name: str) -> dict:
    return json.loads((COMMITTED_JSON_DIR / f"{name}.schema.json").read_text())


# ---------------------------------------------------------------------------
# Discovery sanity
# ---------------------------------------------------------------------------

def test_all_six_state_schemas_discovered():
    """Exactly the six state documents are exported (engine-api.md state model)."""
    assert set(SCHEMA_NAMES) == {
        "learner-profile", "resource-tracker", "schedule",
        "session-log", "skill-map", "system-health",
    }


# ---------------------------------------------------------------------------
# (a) exporter runs clean and outputs parse as JSON
# ---------------------------------------------------------------------------

def test_export_runs_clean_and_outputs_parse_as_json(tmp_path):
    """export_all writes one parseable JSON object per schema."""
    results = export_mod.export_all(out_dir=tmp_path)
    assert len(results) == len(SCHEMA_PATHS)
    for out_path, content in results:
        assert out_path.exists()
        parsed = json.loads(out_path.read_text())  # raises on malformed JSON
        assert isinstance(parsed, dict)
        # In-memory content and on-disk bytes agree.
        assert out_path.read_text() == content


def test_cli_check_passes_on_committed_artifacts():
    """`export-json-schemas.py --check` exits 0 — committed artifacts are current
    and the CLI itself runs clean end to end."""
    script = export_mod.SCHEMAS_DIR.parent / "scripts" / "export-json-schemas.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--check"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_committed_json_files_exist_and_parse():
    for name in SCHEMA_NAMES:
        parsed = _load_committed(name)
        assert isinstance(parsed, dict)


# ---------------------------------------------------------------------------
# (b) every YAML top-level field appears; required lists match required:true
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", SCHEMA_PATHS, ids=SCHEMA_NAMES)
def test_top_level_fields_and_required_round_trip(path):
    schema_dict = yaml.safe_load(path.read_text())
    top_bag = _yaml_top_bag(schema_dict)
    name = export_mod._schema_name(path)
    doc = _load_committed(name)

    # Every YAML top-level field is present as a JSON property (exactly).
    assert set(doc["properties"].keys()) == set(top_bag.keys())

    # required[] matches exactly the fields marked required: true.
    assert set(doc.get("required", [])) == _expected_required(top_bag)


def test_root_is_object_with_properties():
    for name in SCHEMA_NAMES:
        doc = _load_committed(name)
        assert doc["type"] == "object"
        assert isinstance(doc["properties"], dict)
        assert doc["properties"]  # non-empty


# ---------------------------------------------------------------------------
# (c) enums survive the trip
# ---------------------------------------------------------------------------

def test_session_type_enum_survives():
    """session_type carries all 13 router-persistable values (schema is oracle)."""
    sl_yaml = yaml.safe_load((export_mod.SCHEMAS_DIR / "session-log.schema.yaml").read_text())
    expected = sl_yaml["fields"]["session_type"]["enum"]
    doc = _load_committed("session-log")
    assert doc["properties"]["session_type"]["enum"] == expected
    # Spot-check a couple of the values explicitly.
    assert "standard" in expected and "placement-validation" in expected


def test_skill_map_status_enum_survives():
    """The grammar-entry status enum round-trips into the exported schema."""
    sm_yaml = yaml.safe_load((export_mod.SCHEMAS_DIR / "skill-map.schema.yaml").read_text())
    expected = sm_yaml["grammar_entry_template"]["status"]["enum"]
    doc = _load_committed("skill-map")
    status_node = doc["properties"]["grammar_entry_template"]["properties"]["status"]
    assert status_node["enum"] == expected
    assert set(expected) == {
        "unseen", "introduced", "practicing", "acquired", "automatic", "regressed",
    }


def test_nullable_enum_widens_type():
    """An enum that admits null widens the scalar type to [type, "null"] so the
    exported schema is not internally contradictory."""
    doc = _load_committed("skill-map")
    error_trend = doc["properties"]["grammar_entry_template"]["properties"]["error_trend"]
    assert None in error_trend["enum"]
    assert error_trend["type"] == ["string", "null"]


# ---------------------------------------------------------------------------
# (d) regeneration is idempotent
# ---------------------------------------------------------------------------

def test_regeneration_is_idempotent():
    """Rendering each schema twice yields byte-identical output, and that output
    matches the committed artifact."""
    for path in SCHEMA_PATHS:
        out_name, first = export_mod.render_schema(path, export_mod.DEFAULT_ID_BASE)
        _, second = export_mod.render_schema(path, export_mod.DEFAULT_ID_BASE)
        assert first == second
        committed = (COMMITTED_JSON_DIR / out_name).read_text()
        assert committed == first, f"{out_name} committed artifact is stale"


# ---------------------------------------------------------------------------
# (e) each file declares Draft 2020-12
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_declares_draft_2020_12(name):
    doc = _load_committed(name)
    assert doc["$schema"] == DRAFT_2020_12


@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_has_id_and_title(name):
    doc = _load_committed(name)
    assert doc["$id"].endswith(f"{name}.schema.json")
    assert isinstance(doc["title"], str) and doc["title"]


# ---------------------------------------------------------------------------
# Dialect-construct fidelity (item_shape, free-form map, children)
# ---------------------------------------------------------------------------

def test_list_item_shape_becomes_array_of_objects():
    """resource-tracker `resources` (list + item_shape) -> array of objects with
    the item shape's required fields."""
    doc = _load_committed("resource-tracker")
    resources = doc["properties"]["resources"]
    assert resources["type"] == "array"
    items = resources["items"]
    assert items["type"] == "object"
    assert set(items["required"]) == {"name", "type"}
    assert "name" in items["properties"] and "type" in items["properties"]


def test_free_form_map_becomes_additional_properties():
    """session-log `assessment.vocabulary_observation` (map, no children) ->
    object with additionalProperties true."""
    doc = _load_committed("session-log")
    node = doc["properties"]["assessment"]["properties"]["vocabulary_observation"]
    assert node["type"] == "object"
    assert node.get("additionalProperties") is True
    assert "properties" not in node


def test_map_with_children_becomes_object_with_properties():
    """resource-tracker `input_summary` (map + children) -> object with props."""
    doc = _load_committed("resource-tracker")
    node = doc["properties"]["input_summary"]
    assert node["type"] == "object"
    assert set(node["properties"].keys()) == {
        "total_listening_hours", "total_reading_hours",
        "current_listening_level", "current_reading_level",
    }


def test_scalar_type_mapping():
    """int/float/bool/string map to integer/number/boolean/string."""
    doc = _load_committed("system-health")
    props = doc["properties"]
    assert props["schema_version"]["type"] == "integer"
    assert props["reteach_rate_30d"]["type"] == "number"


# ---------------------------------------------------------------------------
# id-base is configurable (port rebranding)
# ---------------------------------------------------------------------------

def test_id_base_is_configurable(tmp_path):
    results = export_mod.export_all(out_dir=tmp_path, id_base="urn:example:")
    for out_path, _ in results:
        doc = json.loads(out_path.read_text())
        assert doc["$id"].startswith("urn:example:")
        assert doc["$id"].endswith(".schema.json")
