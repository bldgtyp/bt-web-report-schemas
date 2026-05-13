"""PHPP workbook schema lookup."""

from __future__ import annotations

from bt_web_report_schemas.phpp.models import WorkbookSchema
from bt_web_report_schemas.phpp.v10_6 import SCHEMA as V10_6_SCHEMA

_SCHEMAS: dict[str, WorkbookSchema] = {
    V10_6_SCHEMA.version: V10_6_SCHEMA,
}


def normalize_phpp_version(version: str) -> str:
    """Normalize PHPP version strings from workbook cells and CLI input."""

    value = str(version).strip().lower()
    if value.startswith("v"):
        value = value[1:]
    if value.startswith("phpp "):
        value = value[5:]
    return value


def get_schema(version: str) -> WorkbookSchema:
    """Return the supported PHPP schema for a version or raise a clear error."""

    normalized = normalize_phpp_version(version)
    try:
        return _SCHEMAS[normalized]
    except KeyError as exc:
        supported = ", ".join(sorted(_SCHEMAS))
        msg = f"Unsupported PHPP version '{version}'. Supported versions: {supported}."
        raise ValueError(msg) from exc


def supported_versions() -> tuple[str, ...]:
    """Return supported PHPP versions in sorted order."""

    return tuple(sorted(_SCHEMAS))
