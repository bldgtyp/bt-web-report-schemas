"""Pydantic models for ``project.yaml`` — the per-project metadata file."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCHEMA_VERSION = "0.2.0"

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class Building(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    address: str
    city: str
    state: str
    climate_zone: str
    building_type: str


class SourceFiles(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    phpp_path: str = ""
    data_dir: str
    assets_dir: str

    @field_validator("data_dir", "assets_dir")
    @classmethod
    def _must_be_repo_relative(cls, value: str) -> str:
        if value.startswith("~") or value.startswith("/"):
            raise ValueError("must be repo-relative, not machine-specific")
        return value


class Publishing(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    production_url: str
    cloudflare_pages_project: str

    @field_validator("production_url")
    @classmethod
    def _must_be_https(cls, value: str) -> str:
        try:
            parsed = urlparse(value)
        except Exception as exc:
            raise ValueError("must be a valid URL") from exc
        if parsed.scheme != "https":
            raise ValueError("must use https")
        if not parsed.netloc:
            raise ValueError("must be a valid URL")
        return value


# ---------------------------------------------------------------------------
# Narrative block — every field is an optional string. Values flow into prose
# via the <Var k="..." /> shortcode and are NOT used for any calculation, so we
# do not coerce numbers/URLs here. Authors are responsible for the rendered
# string exactly as it should appear.
# ---------------------------------------------------------------------------


class CertificationNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    target: str | None = None  # e.g. "EnerPHit by Component"

    # Climate-specific limits — hand-entered from PHI / Phius tools.
    ph_ach_limit: str | None = None
    phi_lcd_limit: str | None = None
    enph_hd_limit: str | None = None
    enph_per_limit: str | None = None
    enph_bg_limit: str | None = None
    enph_ag_ext_limit: str | None = None
    enph_ag_int_limit: str | None = None
    enph_uw_limit: str | None = None
    phius_hd_limit: str | None = None
    phius_cd_limit: str | None = None
    phius_hl_limit: str | None = None
    phius_cl_limit: str | None = None
    phius_nse_limit: str | None = None
    phius_cfm50_limit: str | None = None


class ClimateNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    weather_station_name: str | None = None
    weather_station_url: str | None = None
    state_name: str | None = None
    state_name_abbreviation: str | None = None
    ashrae_location_name: str | None = None  # was ASHRAE_location_name in Hugo
    ashrae_design_temps: str | None = None  # was ASHRAE_design_temps


class EnergyCodeNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str | None = None
    zone: str | None = None
    link: str | None = None
    u_val_link: str | None = None
    ach_link: str | None = None
    ach_limit: str | None = None
    window_min_u_value: str | None = None


class Co2Narrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    subregion_name: str | None = None
    occupancy: str | None = None
    target_tons: str | None = None


class WindowsNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    ph_window_u_value: str | None = None
    ph_window_r_value: str | None = None


class ErvNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    manufacturer_name: str | None = None
    type_name: str | None = None
    link: str | None = None


class MechanicalNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    erv: ErvNarrative = Field(default_factory=ErvNarrative)


class Narrative(BaseModel):
    """Hand-typed prose-facing values, grouped to mirror the report sections.

    Every field is optional so a freshly-scaffolded project validates before
    the user has filled anything in. Missing keys render as a visible
    placeholder in dev preview and fail the build in production.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    certification: CertificationNarrative = Field(default_factory=CertificationNarrative)
    climate: ClimateNarrative = Field(default_factory=ClimateNarrative)
    energy_code: EnergyCodeNarrative = Field(default_factory=EnergyCodeNarrative)
    co2: Co2Narrative = Field(default_factory=Co2Narrative)
    windows: WindowsNarrative = Field(default_factory=WindowsNarrative)
    mechanical: MechanicalNarrative = Field(default_factory=MechanicalNarrative)


# ---------------------------------------------------------------------------
# Top-level project.yaml
# ---------------------------------------------------------------------------


class Project(BaseModel):
    """Schema for ``project.yaml`` at the root of a per-project report repo."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str
    slug: str
    project_title: str
    client_name: str
    building_name: str
    phase: str
    report_date: str
    prepared_by: str
    contact_email: str
    target_standard: str  # free-form: "Passive House", "EnerPHit", anything
    certification_program: str
    certification_path: str
    building: Building
    source_files: SourceFiles
    publishing: Publishing
    narrative: Narrative = Field(default_factory=Narrative)

    @field_validator("schema_version")
    @classmethod
    def _schema_version_pinned(cls, value: str) -> str:
        if value != SCHEMA_VERSION:
            raise ValueError(f'must be "{SCHEMA_VERSION}"')
        return value

    @field_validator("slug")
    @classmethod
    def _slug_kebab(cls, value: str) -> str:
        if not _SLUG_PATTERN.match(value):
            raise ValueError("must be lowercase kebab-case, using only a-z, 0-9, and single hyphens")
        return value

    @field_validator("contact_email")
    @classmethod
    def _contact_email_format(cls, value: str) -> str:
        if not _EMAIL_PATTERN.match(value):
            raise ValueError("must be a valid email address")
        return value

    @model_validator(mode="before")
    @classmethod
    def _strip_top_level_blanks(cls, value: Any) -> Any:
        """Required top-level strings must be non-empty after trim."""

        if not isinstance(value, dict):
            return value
        required = (
            "schema_version",
            "slug",
            "project_title",
            "client_name",
            "building_name",
            "phase",
            "report_date",
            "prepared_by",
            "contact_email",
            "target_standard",
            "certification_program",
            "certification_path",
        )
        errors: list[str] = []
        for key in required:
            field_value = value.get(key)
            if isinstance(field_value, str) and field_value.strip() == "":
                errors.append(f"{key} is required")
        if errors:
            raise ValueError("; ".join(errors))
        return value
