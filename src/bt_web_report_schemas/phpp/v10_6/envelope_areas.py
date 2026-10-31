"""PHPP 10.6 Areas / U-values map for per-assembly envelope areas."""

from bt_web_report_schemas.phpp.models import EnvelopeAreasSchema

# Group numbers follow the Heating worksheet temperature zones: 8 (wall,
# ambient), 10 (roof) and 12 (exposed / attached zone) lose heat to ambient
# air (Gt-A); 9 (wall, ground) and 11 (floor slab) lose heat to the ground
# (Gt-B). Other groups (windows, doors, 18 towards neighbour) carry no exposure.
ENVELOPE_AREAS = EnvelopeAreasSchema(
    areas_sheet="Areas",
    areas_first_row=41,
    areas_last_row=540,
    group_col="M",
    area_col="Z",
    assembly_col="AA",
    u_values_sheet="U-values",
    u_values_first_block_row=8,
    u_values_block_height=21,
    u_values_id_col="Q",
    u_values_name_col="L",
    u_values_layer_col="E",
    u_values_layer_first_offset=5,
    u_values_layer_count=8,
    ambient_groups=(8, 10, 12),
    ground_groups=(9, 11),
)
