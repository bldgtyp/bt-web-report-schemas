"""Pydantic models for generated report-data manifests."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SourceWorkbook(BaseModel):
    """Fingerprint for the PHPP workbook used to generate report data."""

    model_config = ConfigDict(frozen=True)

    path: str
    sha256: str
    size_bytes: int


class VariantMeta(BaseModel):
    """One PHPP variant exposed to the report layer."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    order: int
    color: str = "auto"
    recommended: bool = False
    source_column: str | None = None


class Manifest(BaseModel):
    """Metadata written beside deterministic CSV report data."""

    schema_version: str = "1.0.0"
    phpp_version: str
    generated_at: datetime
    generator: str
    status: Literal["ok", "pending"] = "ok"
    variants: tuple[VariantMeta, ...] = Field(default_factory=tuple)
    recommended_variant_id: str | None = None
    source_workbook: SourceWorkbook | None = None
