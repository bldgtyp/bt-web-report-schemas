from bt_web_report_schemas.phpp import get_schema, supported_versions


def test_supported_versions_include_vandam_fixture_version() -> None:
    assert supported_versions() == ("10.6",)


def test_v10_6_variants_rows_match_legacy_map() -> None:
    schema = get_schema("10.6")

    geometry = schema.section("geometry")
    assert geometry.start_row == 315
    assert geometry.field("tfa").row == 316
    assert geometry.field("building_envelope_area").row == 319

    assert schema.section("certification_limits").field("heat_demand_limit").row == 363
    assert schema.section("certification_results").field("heat_demand").row == 459
    assert schema.section("primary_energy_renewable").field("solar_pv").row == 535


def test_variant_field_ids_are_unique() -> None:
    schema = get_schema("10.6")

    fields = schema.variant_fields()

    assert len(fields) == len({(field.section_id, field.id) for field in fields})


def test_r_value_assembly_slots_are_dynamic_labels() -> None:
    schema = get_schema("10.6")
    r_values = schema.section("r_values")

    assert r_values.field("assembly_01").row == 480
    assert r_values.field("assembly_10").row == 489
    assert r_values.field("assembly_01").label_from_workbook is True
    assert r_values.field("gt_a").label_from_workbook is False


def test_v10_6_climate_and_room_ventilation_maps() -> None:
    schema = get_schema("10.6")

    assert schema.climate_monthly.sheet == "Climate"
    assert schema.climate_monthly.start_row == 26
    assert schema.climate_monthly.end_row == 36
    assert schema.climate_monthly.start_col == "D"
    assert schema.climate_monthly.end_col == "U"

    assert schema.room_ventilation.sheet == "Addl vent"
    assert schema.room_ventilation.header_col == "C"
    assert schema.room_ventilation.header_label == "Room"
    assert schema.room_ventilation.last_col == "Z"


def test_unknown_schema_version_fails_loudly() -> None:
    try:
        get_schema("10.7")
    except ValueError as exc:
        assert "Unsupported PHPP version '10.7'" in str(exc)
        assert "10.6" in str(exc)
    else:
        raise AssertionError("Expected unsupported PHPP version to fail")
