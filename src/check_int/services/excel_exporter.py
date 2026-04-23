from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import PatternFill


HIGHLIGHT_FILL = PatternFill(fill_type="solid", fgColor="FFF1B3")
HEADERS = ["tag_no", "field_name", "status", "master_value", "pid_value", "datasheet_value"]


def export_comparison_rows_to_excel(
    rows: list[dict[str, str | None]],
    output_path: str | Path,
) -> Path:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Integrity Report"
    sheet.append(HEADERS)

    for row in rows:
        sheet.append([row.get(header) for header in HEADERS])
        current_row = sheet.max_row
        if row.get("status") == "mismatch":
            for column_index in range(4, 7):
                sheet.cell(row=current_row, column=column_index).fill = HIGHLIGHT_FILL

    output = Path(output_path)
    workbook.save(output)
    return output