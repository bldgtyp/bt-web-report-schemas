"""Typed PHPP workbook row-map primitives."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldRef:
    """One report-relevant PHPP field."""

    id: str
    phpp_label: str
    row: int
    section_id: str
    section_label: str
    label_from_workbook: bool = False


@dataclass(frozen=True)
class SectionMap:
    """A contiguous PHPP section in a worksheet."""

    id: str
    label: str
    start_row: int
    fields: tuple[FieldRef, ...]

    @property
    def end_row(self) -> int:
        return max(field.row for field in self.fields)

    def field(self, field_id: str) -> FieldRef:
        for field in self.fields:
            if field.id == field_id:
                return field
        valid = ", ".join(field.id for field in self.fields)
        msg = f"Field '{field_id}' not found in section '{self.id}'. Valid fields: {valid}."
        raise KeyError(msg)


@dataclass(frozen=True)
class ClimateMonthlySchema:
    """Active monthly climate data block."""

    sheet: str
    start_row: int
    end_row: int
    start_col: str
    end_col: str


@dataclass(frozen=True)
class RoomVentilationSchema:
    """Additional Ventilation room table location and columns."""

    sheet: str
    header_col: str
    header_label: str
    entry_col: str
    first_entry_label: str
    last_col: str


@dataclass(frozen=True)
class EnvelopeAreasSchema:
    """Areas worksheet surfaces plus the U-values blocks that key them to Variants.

    Every Areas row names its assembly as ``<id>-<name>`` (``02ud-Cellar-Wall``)
    and its PHPP group as ``<number>-<label>`` (``9-``). The U-values sheet is a
    run of fixed-height assembly blocks; each block's id cell matches the Areas
    prefix, and the block's first layer name starts with the Variants key
    letter (``a-Cellar-Wall``) that selects a row in the Variants ENVELOPE
    section. That letter is the only link between an area and its R-value.
    """

    areas_sheet: str
    areas_first_row: int
    areas_last_row: int
    group_col: str
    area_col: str
    assembly_col: str
    u_values_sheet: str
    u_values_first_block_row: int
    u_values_block_height: int
    u_values_id_col: str
    u_values_name_col: str
    u_values_layer_col: str
    u_values_layer_first_offset: int
    u_values_layer_count: int
    ambient_groups: tuple[int, ...]
    ground_groups: tuple[int, ...]

    def exposure(self, group_number: int) -> str:
        """``A`` for ambient-air groups, ``B`` for ground groups, empty otherwise."""

        if group_number in self.ambient_groups:
            return "A"
        if group_number in self.ground_groups:
            return "B"
        return ""


@dataclass(frozen=True)
class WorkbookSchema:
    """Supported PHPP workbook schema."""

    version: str
    variant_sheet: str
    climate_sheet: str
    room_ventilation_sheet: str
    phpp_version_cell: str
    phpp_version_named_range: str
    variant_header_row: int
    variant_first_data_row: int
    variants: tuple[SectionMap, ...]
    climate_monthly: ClimateMonthlySchema
    room_ventilation: RoomVentilationSchema
    envelope_areas: EnvelopeAreasSchema

    def section(self, section_id: str) -> SectionMap:
        for section in self.variants:
            if section.id == section_id:
                return section
        valid = ", ".join(section.id for section in self.variants)
        msg = f"Section '{section_id}' not found for PHPP {self.version}. Valid sections: {valid}."
        raise KeyError(msg)

    def variant_fields(self) -> tuple[FieldRef, ...]:
        fields: list[FieldRef] = []
        for section in self.variants:
            for field in section.fields:
                fields.append(field)
        return tuple(fields)
