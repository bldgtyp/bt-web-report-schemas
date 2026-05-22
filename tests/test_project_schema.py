"""Tests for the ``project.yaml`` Pydantic schema."""

from __future__ import annotations

from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from bt_web_report_schemas.project import (
    SCHEMA_VERSION,
    CertificationNarrative,
    ClimateNarrative,
    Co2Narrative,
    EnergyCodeNarrative,
    ErvNarrative,
    MechanicalNarrative,
    Narrative,
    Project,
    WindowsNarrative,
)


def _minimum_required_payload() -> dict[str, Any]:
    """Return a dict that passes validation with only required top-level keys.

    Narrative is omitted so we exercise the default-factory path.
    """

    return {
        "schema_version": SCHEMA_VERSION,
        "slug": "proj-0000-example",
        "project_title": "Example Passive House Report",
        "client_name": "Example Client",
        "building_name": "Example Residence",
        "phase": "Design Analysis",
        "report_date": "2026-05-19",
        "prepared_by": "BLDGTYP",
        "contact_email": "info@bldgtyp.com",
        "target_standard": "Passive House",
        "certification_program": "Design analysis only",
        "certification_path": "Not submitted",
        "building": {
            "address": "123 Example Street",
            "city": "Brooklyn",
            "state": "NY",
            "climate_zone": "ASHRAE 4A",
            "building_type": "single-family residential",
        },
        "source_files": {
            "phpp_path": "",
            "cad_files_received_date": "June 6, 2025",
            "data_dir": "data",
            "assets_dir": "public/assets",
        },
        "publishing": {
            "production_url": "https://project-0000.bldgtyp.com",
            "cloudflare_pages_project": "bt-proj-0000-example-report",
        },
    }


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_minimum_required_payload_validates() -> None:
    project = Project.model_validate(_minimum_required_payload())
    assert project.slug == "proj-0000-example"
    assert project.target_standard == "Passive House"
    assert project.narrative == Narrative()  # default factory used


def test_narrative_defaults_to_empty_subsections() -> None:
    project = Project.model_validate(_minimum_required_payload())
    assert project.narrative.certification == CertificationNarrative()
    assert project.narrative.climate == ClimateNarrative()
    assert project.narrative.energy_code == EnergyCodeNarrative()
    assert project.narrative.co2 == Co2Narrative()
    assert project.narrative.windows == WindowsNarrative()
    assert project.narrative.mechanical == MechanicalNarrative()
    assert project.narrative.mechanical.erv == ErvNarrative()
    assert project.narrative.user_defined == {}


def test_target_standard_accepts_arbitrary_string() -> None:
    payload = _minimum_required_payload()
    payload["target_standard"] = "ASHRAE 90.1 design study"
    project = Project.model_validate(payload)
    assert project.target_standard == "ASHRAE 90.1 design study"


def test_full_narrative_round_trip_through_yaml() -> None:
    payload = _minimum_required_payload()
    payload["narrative"] = {
        "certification": {
            "target": "EnerPHit by Component",
            "ph_ach_limit": "0.8",
            "enph_hd_limit": "7.92",
            "enph_uw_limit": "0.151",
            "phius_hd_limit": "7.3",
        },
        "climate": {
            "weather_station_name": "New_York_J_F_Kennedy_IntL_Ar :: 744860 :: TMY3",
            "state_name": "New York",
            "state_name_abbreviation": "NY",
            "ashrae_location_name": "Zone 4(A)",
            "ashrae_design_temps": "4.8°F (-15.1°C)",
        },
        "energy_code": {
            "name": "NYC Energy Code 2025",
            "zone": "Zone 4(A)",
            "ach_limit": "3.0",
        },
        "co2": {
            "subregion_name": "NYC eGrid (2020)",
            "occupancy": "4",
            "target_tons": "4",
        },
        "windows": {"ph_window_u_value": "0.18", "ph_window_r_value": "5.7"},
        "mechanical": {
            "erv": {
                "manufacturer_name": "Zehnder America",
                "type_name": "Zehnder America ComfoAir Q600-ERV",
                "link": "https://zehnderamerica.com/products/ventilator/comfoair-q/",
            }
        },
    }
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    parsed = yaml.safe_load(text)
    project = Project.model_validate(parsed)
    assert project.narrative.certification.target == "EnerPHit by Component"
    assert project.narrative.climate.state_name_abbreviation == "NY"
    assert project.narrative.energy_code.ach_limit == "3.0"
    assert project.narrative.mechanical.erv.manufacturer_name == "Zehnder America"


def test_narrative_partial_fill_is_allowed() -> None:
    """Partial narrative (just a few fields) must validate — projects fill in over time."""

    payload = _minimum_required_payload()
    payload["narrative"] = {"climate": {"state_name": "New York"}}
    project = Project.model_validate(payload)
    assert project.narrative.climate.state_name == "New York"
    assert project.narrative.climate.weather_station_name is None
    assert project.narrative.certification.target is None


def test_narrative_user_defined_accepts_project_specific_string_values() -> None:
    payload = _minimum_required_payload()
    payload["narrative"] = {
        "user_defined": {
            "cad_received_date": "May 1, 2026",
            "architect_label": "Yun Architects",
            "empty_placeholder": None,
        }
    }

    project = Project.model_validate(payload)

    assert project.narrative.user_defined == {
        "cad_received_date": "May 1, 2026",
        "architect_label": "Yun Architects",
        "empty_placeholder": None,
    }


# ---------------------------------------------------------------------------
# Validator failures — one test per rule, covering both top-level and nested
# ---------------------------------------------------------------------------


def test_schema_version_must_match_constant() -> None:
    payload = _minimum_required_payload()
    payload["schema_version"] = "0.1.0"
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    # Literal["0.2.0"] produces an "Input should be '0.2.0'" error.
    assert SCHEMA_VERSION in str(excinfo.value)
    assert "schema_version" in str(excinfo.value)


@pytest.mark.parametrize(
    "bad_slug",
    [
        "Proj-0000",  # uppercase
        "proj_0000",  # underscore
        "proj 0000",  # space
        "proj--0000",  # double hyphen
        "-proj-0000",  # leading hyphen
        "proj-0000-",  # trailing hyphen
        "",  # empty (also blank-required)
    ],
)
def test_slug_must_be_kebab_case(bad_slug: str) -> None:
    payload = _minimum_required_payload()
    payload["slug"] = bad_slug
    with pytest.raises(ValidationError):
        Project.model_validate(payload)


@pytest.mark.parametrize(
    "bad_email",
    [
        "not-an-email",
        "missing@domain",
        "@bldgtyp.com",
        "ed@.com",
        "ed @bldgtyp.com",
    ],
)
def test_contact_email_must_be_well_formed(bad_email: str) -> None:
    payload = _minimum_required_payload()
    payload["contact_email"] = bad_email
    with pytest.raises(ValidationError):
        Project.model_validate(payload)


def test_publishing_url_must_be_https() -> None:
    payload = _minimum_required_payload()
    payload["publishing"]["production_url"] = "http://project-0000.bldgtyp.com"
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    assert "production_url" in str(excinfo.value)


def test_publishing_url_must_be_well_formed() -> None:
    payload = _minimum_required_payload()
    payload["publishing"]["production_url"] = "not a url"
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    assert "production_url" in str(excinfo.value)


@pytest.mark.parametrize("bad_dir", ["~/data", "/absolute/data", "/var/tmp/assets"])
def test_source_files_dirs_must_be_repo_relative(bad_dir: str) -> None:
    payload = _minimum_required_payload()
    payload["source_files"]["data_dir"] = bad_dir
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    assert "data_dir" in str(excinfo.value)


def test_source_files_cad_files_received_date_can_be_omitted() -> None:
    payload = _minimum_required_payload()
    del payload["source_files"]["cad_files_received_date"]
    project = Project.model_validate(payload)
    assert project.source_files.cad_files_received_date is None


@pytest.mark.parametrize(
    "blank_field",
    [
        "project_title",
        "client_name",
        "building_name",
        "phase",
        "report_date",
        "prepared_by",
        "target_standard",
        "certification_program",
        "certification_path",
    ],
)
def test_required_top_level_strings_reject_blank(blank_field: str) -> None:
    """Whitespace-only values must fail (\\S pattern), as must empty strings."""

    payload = _minimum_required_payload()
    payload[blank_field] = "   "
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    assert blank_field in str(excinfo.value)


@pytest.mark.parametrize(
    "blank_field",
    [
        "project_title",
        "client_name",
        "building_name",
        "phase",
        "report_date",
        "prepared_by",
        "target_standard",
        "certification_program",
        "certification_path",
    ],
)
def test_required_top_level_strings_reject_empty(blank_field: str) -> None:
    payload = _minimum_required_payload()
    payload[blank_field] = ""
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    assert blank_field in str(excinfo.value)


def test_required_top_level_strings_cannot_be_missing() -> None:
    payload = _minimum_required_payload()
    del payload["client_name"]
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    assert "client_name" in str(excinfo.value)


def test_extra_top_level_keys_are_rejected() -> None:
    payload = _minimum_required_payload()
    payload["typo_field"] = "oops"
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    assert "typo_field" in str(excinfo.value)


def test_extra_narrative_keys_are_rejected() -> None:
    """Typos in narrative section names must fail loudly — they would silently
    drop values otherwise, defeating the point of <Var> autocompletion."""

    payload = _minimum_required_payload()
    payload["narrative"] = {
        "certification": {
            "target": "EnerPHit",
            "ph_ach_limt": "0.8",  # typo: should be ph_ach_limit
        }
    }
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    assert "ph_ach_limt" in str(excinfo.value)


def test_extra_narrative_section_is_rejected() -> None:
    """Typos in section names (e.g. ``mechancial``) must also fail."""

    payload = _minimum_required_payload()
    payload["narrative"] = {"mechancial": {"erv": {}}}  # typo: mechanical
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    assert "mechancial" in str(excinfo.value)


def test_building_block_requires_all_subfields() -> None:
    payload = _minimum_required_payload()
    del payload["building"]["climate_zone"]
    with pytest.raises(ValidationError) as excinfo:
        Project.model_validate(payload)
    assert "climate_zone" in str(excinfo.value)


def test_project_is_frozen() -> None:
    """Frozen models prevent accidental mutation; the schema is read-only state."""

    project = Project.model_validate(_minimum_required_payload())
    with pytest.raises(ValidationError):
        project.slug = "different-slug"  # type: ignore[misc]
