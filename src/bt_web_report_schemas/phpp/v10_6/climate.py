"""PHPP 10.6 Climate worksheet map."""

from bt_web_report_schemas.phpp.models import ClimateMonthlySchema

CLIMATE_MONTHLY = ClimateMonthlySchema(
    sheet="Climate",
    start_row=26,
    end_row=36,
    start_col="D",
    end_col="U",
)
