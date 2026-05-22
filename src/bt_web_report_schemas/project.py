"""Pydantic models for ``project.yaml`` — the per-project metadata file.

Constraints are expressed via ``Field(pattern=..., min_length=...)`` so they
flow into the generated JSON Schema and are enforced identically by Pydantic
(server side) and by ajv (browser / Node side). Don't add ``field_validator``
methods here unless the rule genuinely can't be expressed in JSON Schema —
they would create silent drift between the two enforcement paths.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "0.2.0"

# Regex patterns are the single source of truth for both validators. Keep
# anchored so they behave identically under JSON-Schema (unanchored search)
# and Python ``re.search``.
SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
EMAIL_PATTERN = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
HTTPS_URL_PATTERN = r"^https://\S+$"
REPO_RELATIVE_PATH_PATTERN = r"^[^~/].*"  # must not start with ~ or /
NON_BLANK_PATTERN = r"\S"  # must contain at least one non-whitespace char


def _required_str(**extra: object) -> object:
    """Required string: non-empty and not pure whitespace."""

    return Field(min_length=1, pattern=NON_BLANK_PATTERN, **extra)  # type: ignore[arg-type]


class Building(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    address: str = _required_str()  # type: ignore[assignment]
    city: str = _required_str()  # type: ignore[assignment]
    state: str = _required_str()  # type: ignore[assignment]
    climate_zone: str = _required_str()  # type: ignore[assignment]
    building_type: str = _required_str()  # type: ignore[assignment]


class SourceFiles(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", title="Source Files")

    phpp_path: str = ""  # may be empty before the PHPP exists
    cad_files_received_date: str | None = None
    data_dir: str = Field(pattern=REPO_RELATIVE_PATH_PATTERN)
    assets_dir: str = Field(pattern=REPO_RELATIVE_PATH_PATTERN)


class Publishing(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    production_url: str = Field(pattern=HTTPS_URL_PATTERN)
    cloudflare_pages_project: str = _required_str()  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Narrative block — every field is an optional string. Values flow into prose
# via the <Var k="..." /> shortcode and are NOT used for any calculation, so we
# do not coerce numbers/URLs here. Authors are responsible for the rendered
# string exactly as it should appear.
# ---------------------------------------------------------------------------


class CertificationNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", title="Certification")

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
    model_config = ConfigDict(frozen=True, extra="forbid", title="Climate")

    weather_station_name: str | None = None
    weather_station_url: str | None = None
    state_name: str | None = None
    state_name_abbreviation: str | None = None
    ashrae_location_name: str | None = None  # was ASHRAE_location_name in Hugo
    ashrae_design_temps: str | None = None  # was ASHRAE_design_temps


class EnergyCodeNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", title="Energy code")

    name: str | None = None
    zone: str | None = None
    link: str | None = None
    code_base_url: str | None = None
    code_airtightness_url: str | None = None
    u_val_link: str | None = None
    ach_link: str | None = None
    ach_limit: str | None = None
    window_min_u_value: str | None = None


class Co2Narrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", title="CO2")

    subregion_name: str | None = None
    occupancy: str | None = None
    target_tons: str | None = None


class WindowsNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", title="Windows")

    ph_window_u_value: str | None = None
    ph_window_r_value: str | None = None


class ErvNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", title="ERV")

    manufacturer_name: str | None = None
    type_name: str | None = None
    link: str | None = None


class MechanicalNarrative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", title="Mechanical")

    erv: ErvNarrative = Field(default_factory=ErvNarrative)


class Narrative(BaseModel):
    """Hand-typed prose-facing values, grouped to mirror the report sections.

    Every field is optional so a freshly-scaffolded project validates before
    the user has filled anything in. Missing keys render as a visible
    placeholder in dev preview and fail the build in production.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    certification: CertificationNarrative = Field(
        default_factory=CertificationNarrative
    )
    climate: ClimateNarrative = Field(default_factory=ClimateNarrative)
    energy_code: EnergyCodeNarrative = Field(default_factory=EnergyCodeNarrative)
    co2: Co2Narrative = Field(default_factory=Co2Narrative)
    windows: WindowsNarrative = Field(default_factory=WindowsNarrative)
    mechanical: MechanicalNarrative = Field(default_factory=MechanicalNarrative)
    user_defined: dict[str, str | None] = Field(
        default_factory=dict,
        title="User-defined",
        description=(
            "Project-specific prose variables. Put ad hoc values here and reference them as "
            "narrative.user_defined.<name> from the <Var> shortcode."
        ),
    )


# ---------------------------------------------------------------------------
# Top-level project.yaml
# ---------------------------------------------------------------------------


class Project(BaseModel):
    """Schema for ``project.yaml`` at the root of a per-project report repo."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["0.2.0"]
    slug: str = Field(pattern=SLUG_PATTERN)
    project_title: str = _required_str()  # type: ignore[assignment]
    client_name: str = _required_str()  # type: ignore[assignment]
    building_name: str = _required_str()  # type: ignore[assignment]
    phase: str = _required_str()  # type: ignore[assignment]
    report_date: str = _required_str()  # type: ignore[assignment]
    prepared_by: str = _required_str()  # type: ignore[assignment]
    contact_email: str = Field(pattern=EMAIL_PATTERN)
    target_standard: str = _required_str()  # type: ignore[assignment]  # free-form: "Passive House", anything
    certification_program: str = _required_str()  # type: ignore[assignment]
    certification_path: str = _required_str()  # type: ignore[assignment]
    recommended_variant_id: str | None = None
    building: Building
    source_files: SourceFiles
    publishing: Publishing
    narrative: Narrative = Field(default_factory=Narrative)
