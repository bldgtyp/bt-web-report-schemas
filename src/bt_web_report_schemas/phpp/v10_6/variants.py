"""PHPP 10.6 Variants worksheet row map."""

from __future__ import annotations

import re

from bt_web_report_schemas.phpp.models import FieldRef, SectionMap, WorkbookSchema


def _field_id(label: str) -> str:
    value = label.strip().lower()
    value = value.replace("co2e", "co2e").replace("phius", "phius").replace("phi", "phi")
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value or "blank"


def _section(section_id: str, label: str, start_row: int, labels: list[str]) -> SectionMap:
    fields: list[FieldRef] = []
    seen: dict[str, int] = {}
    for offset, phpp_label in enumerate(labels):
        label_from_workbook = False
        base_id = _field_id(phpp_label)
        if section_id == "r_values" and phpp_label[:2].isdigit() and phpp_label.endswith("ud-"):
            base_id = f"assembly_{phpp_label[:2]}"
            label_from_workbook = True
        count = seen.get(base_id, 0)
        seen[base_id] = count + 1
        field_id = base_id if count == 0 else f"{base_id}_{count + 1}"
        fields.append(
            FieldRef(
                id=field_id,
                phpp_label=phpp_label,
                row=start_row + offset,
                section_id=section_id,
                section_label=label,
                label_from_workbook=label_from_workbook,
            )
        )
    return SectionMap(id=section_id, label=label, start_row=start_row, fields=tuple(fields))


_SECTION_LABELS: tuple[tuple[str, str, list[str]], ...] = (
    (
        "geometry",
        "Geometry",
        [
            "GEOMETRY",
            "TFA",
            "VV",
            "Vn50",
            "Building Envelope Area",
            "Gross Volume",
            "Window Area (North)",
            "Window Area (East)",
            "Window Area (South)",
            "Window Area (West)",
            "Window Area (Horiz)",
            " ",
        ],
    ),
    (
        "envelope",
        "Envelope",
        [
            "ENVELOPE",
            "Floor BG",
            "Wall BG",
            "Party Wall",
            "Wall AG",
            "Roof",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "Thermal Bridge Allowance (% increase)",
            "Volumetric Air Leakage Rate (n50)",
            "Envelope Air Leakage Rate (q50)",
            "Window U-value",
            "Window SHGC",
            " ",
        ],
    ),
    (
        "systems",
        "Systems",
        [
            "SYSTEMS",
            "Ventilation System",
            "Ventilation Unit HR Efficiency",
            "Ventilation Unit ER Efficiency",
            "System HR Efficiency",
            "Cold Air Duct Length (ea)",
            "Cold Air Duct Insulation Thickness",
            "Heating System",
            "Cooling System",
            "DHW System",
            " ",
            " ",
            " ",
        ],
    ),
    (
        "certification_limits",
        "Certification Limits",
        [
            "CERTIFICATION LIMITS",
            "Heat Demand Limit",
            "Sensible Cooling Demand Limit",
            "Latent Cooling Demand Limit",
            "Total Cooling Demand Limit",
            "Peak Heat Load Limit",
            "Peak Cooling Load Limit",
            "PE Limit",
            "PER Limit",
            "PHIUS Net Source Energy Limit",
            " ",
            " ",
            " ",
        ],
    ),
    (
        "heating_demand",
        "Heating Demand",
        [
            "HEAT DEMAND",
            "Walls (AG)",
            "Walls (BG)",
            "Roofs",
            "Floor Slabs",
            " ",
            " ",
            " ",
            "Windows",
            "Exterior door",
            "Thermal Bridges",
            "TB (Perimeter)",
            "TB (BG)",
            "Ventilation",
            "Heating Demand",
            "North",
            "East",
            "South",
            "West",
            "Horizontal",
            "Sum opaque areas",
            "Internal Gains",
            " ",
        ],
    ),
    (
        "cooling_demand",
        "Cooling Demand",
        [
            "COOLING DEMAND",
            "Cooling Demand",
            "Walls (AG)",
            "Walls (BG)",
            "Roofs",
            "Floor Slabs",
            " ",
            " ",
            " ",
            "Windows",
            "Exterior door",
            "Thermal Bridges",
            "TB (Perimeter)",
            "TB (BG)",
            "Ventilation (Basic)",
            "Ventilation (Addn'l)",
            "North",
            "East",
            "South",
            "West",
            "Horizontal",
            "Sum opaque areas",
            "Internal Gains",
            " ",
        ],
    ),
    (
        "site_energy",
        "Site Energy",
        [
            "SITE ENERGY",
            "Heating",
            "Cooling",
            "DHW",
            "Dishwashing",
            "Clothes Washing",
            "Clothes Drying",
            "Refrigerator",
            "Cooking",
            "PHI Lighting",
            "PHI Consumer Elec.",
            "PHI Small Appliances",
            "Phius Int. Lighting",
            "Phius Ext. Lighting",
            "Phius MEL",
            "Aux Elec",
            "Solar PV",
            " ",
        ],
    ),
    (
        "primary_energy",
        "Primary Energy",
        [
            "PRIMARY ENERGY",
            "Heating",
            "Cooling",
            "DHW",
            "Dishwashing",
            "Clothes Washing",
            "Clothes Drying",
            "Refrigerator",
            "Cooking",
            "PHI Lighting",
            "PHI Consumer Elec.",
            "PHI Small Appliances",
            "Phius Int. Lighting",
            "Phius Ext. Lighting",
            "Phius MEL",
            "Aux Elec",
            "Solar PV",
            " ",
        ],
    ),
    (
        "certification_results",
        "Certification Results",
        [
            "CERTIFICATION RESULTS",
            "Heat Demand",
            "Sensible Cooling Demand",
            "Latent Cooling Demand",
            "Total Cooling Demand",
            "Peak Heat Load",
            "Peak Cooling Load ",
            "PE Demand",
            "PER Demand",
            " ",
            " ",
        ],
    ),
    (
        "airtightness",
        "Airtightness",
        [
            "AIRTIGHTNESS",
            "nV,system",
            "hHR",
            "Wind protection coefficient, e",
            "Wind protection coefficient, f",
            "Vn50",
            "VV",
            "Gt",
            " ",
            " ",
        ],
    ),
    (
        "r_values",
        "R-Values",
        [
            "R-VALUES",
            "01ud-",
            "02ud-",
            "03ud-",
            "04ud-",
            "05ud-",
            "06ud-",
            "07ud-",
            "08ud-",
            "09ud-",
            "10ud-",
            "Gt-A",
            "Gt-B",
        ],
    ),
    (
        "certification_compliant",
        "Certification Compliant",
        ["CERTIFICATION COMPLIANT", "Certification Compliant?", " ", " "],
    ),
    (
        "peak_loads",
        "Peak Loads",
        [
            "PEAK LOADS",
            "Peak Heat Load",
            "Peak Sensible Cooling Load",
            "Peak Latent Cooling Load",
            " ",
        ],
    ),
    (
        "co2e",
        "CO2e",
        [
            "CO2E",
            "Heating",
            "Cooling",
            "DHW",
            "Dishwashing",
            "Clothes Washing",
            "Clothes Drying",
            "Refrigerator",
            "Cooking",
            "PHI Lighting",
            "PHI Consumer Elec.",
            "PHI Small Appliances",
            "Phius Int. Lighting",
            "Phius Ext. Lighting",
            "Phius MEL",
            "Aux Elec",
            "IPCC Limit",
            " ",
        ],
    ),
    (
        "primary_energy_renewable",
        "Primary Energy Renewable",
        [
            "PER",
            "Heating",
            "Cooling",
            "DHW",
            "Dishwashing",
            "Clothes Washing",
            "Clothes Drying",
            "Refrigerator",
            "Cooking",
            "PHI Lighting",
            "PHI Consumer Elec.",
            "PHI Small Appliances",
            "Phius Int. Lighting",
            "Phius Ext. Lighting",
            "Phius MEL",
            "Aux Elec",
            "Solar PV",
            " ",
        ],
    ),
)


def _build_sections() -> tuple[SectionMap, ...]:
    sections: list[SectionMap] = []
    start_row = 315
    for section_id, label, field_labels in _SECTION_LABELS:
        section = _section(section_id, label, start_row, field_labels)
        sections.append(section)
        start_row = section.end_row + 1
    return tuple(sections)


SCHEMA = WorkbookSchema(
    version="10.6",
    variant_sheet="Variants",
    climate_sheet="Climate",
    room_ventilation_sheet="Addl vent",
    phpp_version_cell="Data!B5",
    phpp_version_named_range="PHPP_Version",
    variant_header_row=2,
    variant_first_data_row=315,
    variants=_build_sections(),
)
