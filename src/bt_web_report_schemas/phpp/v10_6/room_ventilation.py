"""PHPP 10.6 Additional Ventilation worksheet map."""

from bt_web_report_schemas.phpp.models import RoomVentilationSchema

ROOM_VENTILATION = RoomVentilationSchema(
    sheet="Addl vent",
    header_col="C",
    header_label="Room",
    entry_col="C",
    first_entry_label="1",
    last_col="Z",
)
