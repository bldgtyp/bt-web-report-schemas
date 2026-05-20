"""Generate JSON Schemas from the Pydantic models.

Run as ``uv run gen-json-schemas`` (entry point declared in
``pyproject.toml``). Writes deterministic JSON files under ``schemas/`` at
the package root so JS consumers (Astro, the Manager UI) can import the
schema without invoking Python.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from bt_web_report_schemas import __version__
from bt_web_report_schemas.manifest import Manifest
from bt_web_report_schemas.project import Project

# src/bt_web_report_schemas/gen_json_schemas.py -> repo root for this package
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = PACKAGE_ROOT / "schemas"

GENERATED_COMMENT = (
    "Generated from Pydantic models in bt_web_report_schemas. "
    "DO NOT EDIT BY HAND. Regenerate with `uv run gen-json-schemas`."
)


def schema_dict(model: type[BaseModel]) -> dict[str, Any]:
    """Return the model's JSON Schema with a generator note attached."""

    schema = model.model_json_schema()
    schema["$comment"] = GENERATED_COMMENT
    schema["x-bt-web-report-schemas-version"] = __version__
    return schema


def render_schema_json(model: type[BaseModel]) -> str:
    """Serialize the model's JSON Schema to a deterministic JSON string."""

    return json.dumps(schema_dict(model), indent=2, sort_keys=True) + "\n"


def write_schema(model: type[BaseModel], filename: str) -> Path:
    """Write the model's JSON Schema to ``schemas/<filename>``."""

    SCHEMAS_DIR.mkdir(exist_ok=True)
    out_path = SCHEMAS_DIR / filename
    out_path.write_text(render_schema_json(model), encoding="utf-8")
    return out_path


GENERATED_SCHEMAS: tuple[tuple[type[BaseModel], str], ...] = (
    (Project, "project.schema.json"),
    (Manifest, "manifest.schema.json"),
)


def main() -> None:
    for model, filename in GENERATED_SCHEMAS:
        out_path = write_schema(model, filename)
        print(f"wrote {out_path.relative_to(PACKAGE_ROOT)} (schemas v{__version__})")


if __name__ == "__main__":
    main()
