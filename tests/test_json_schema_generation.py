"""Drift tests for the generated JSON Schemas.

These fail if someone updates the Pydantic models without regenerating
``schemas/*.schema.json``. To fix: ``uv run gen-json-schemas`` and commit
the diff.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bt_web_report_schemas.gen_json_schemas import GENERATED_SCHEMAS, SCHEMAS_DIR, render_schema_json


@pytest.mark.parametrize(("model", "filename"), GENERATED_SCHEMAS)
def test_generated_schema_matches_on_disk(model: type, filename: str) -> None:
    on_disk = (SCHEMAS_DIR / filename).read_text(encoding="utf-8")
    expected = render_schema_json(model)
    assert on_disk == expected, f"{filename} is stale. Run `uv run gen-json-schemas` and commit the diff."


def test_every_schemas_file_is_declared() -> None:
    expected_files = {filename for _, filename in GENERATED_SCHEMAS}
    on_disk_files = {p.name for p in SCHEMAS_DIR.glob("*.schema.json")}
    assert on_disk_files == expected_files, (
        "schemas/ contains files that are not produced by GENERATED_SCHEMAS, "
        "or expected files are missing. Both directions matter so we never "
        "leave a stale schema file in the package."
    )


def test_project_schema_top_level_required_fields() -> None:
    """Spot-check that the Project schema exposes the required top-level keys."""

    from bt_web_report_schemas.gen_json_schemas import schema_dict
    from bt_web_report_schemas.project import Project

    schema = schema_dict(Project)
    required = set(schema["required"])
    assert {"schema_version", "slug", "project_title", "target_standard", "building"} <= required


def test_project_schema_includes_narrative_block() -> None:
    from bt_web_report_schemas.gen_json_schemas import schema_dict
    from bt_web_report_schemas.project import Project

    schema = schema_dict(Project)
    assert "Narrative" in schema["$defs"]
    narrative_props = schema["$defs"]["Narrative"]["properties"]
    assert {"certification", "climate", "energy_code", "co2", "windows", "mechanical", "user_defined"} <= set(
        narrative_props
    )
    assert narrative_props["user_defined"]["additionalProperties"]["anyOf"] == [
        {"type": "string"},
        {"type": "null"},
    ]


def test_project_schema_includes_optional_custom_pages() -> None:
    from bt_web_report_schemas.gen_json_schemas import schema_dict
    from bt_web_report_schemas.project import Project

    schema = schema_dict(Project)
    custom_pages = schema["properties"]["custom_pages"]

    assert "custom_pages" not in schema["required"]
    assert custom_pages["maxItems"] == 2
    assert custom_pages["items"] == {"$ref": "#/$defs/CustomPage"}
