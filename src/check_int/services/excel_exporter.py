from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenPyxlImage
from openpyxl.styles import PatternFill


HIGHLIGHT_FILL = PatternFill(fill_type="solid", fgColor="FFF1B3")
HEADERS = ["Tag No", "Field", "Status", "Master", "P&ID", "Datasheet"]

FIELD_LABELS = {
    "tag_no": "Tag No",
    "service": "Service",
    "material": "Material",
    "capacity": "Capacity",
    "size": "Size",
    "model": "Model",
    "design_temperature": "Design Temperature",
    "design_pressure": "Design Pressure",
    "operating_pressure": "Operating Pressure",
    "operating_temperature": "Operating Temperature",
}

STATUS_LABELS = {
    "matched": "Matched",
    "mismatch": "Mismatch",
    "missing_target": "Missing Target",
    "missing_source": "Missing Source",
    "unreviewed": "Unreviewed",
}


def export_comparison_rows_to_excel(
    rows: list[dict[str, str | None]],
    output_path: str | Path,
    *,
    embed_images: bool = False,
) -> Path:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Integrity Report"
    sheet.append(HEADERS)

    for row in rows:
        sheet.append(
            [
                row.get("tag_no"),
                FIELD_LABELS.get(row.get("field_name") or "", row.get("field_name") or ""),
                STATUS_LABELS.get(row.get("status") or "", row.get("status") or ""),
                row.get("master_value"),
                row.get("pid_value"),
                row.get("datasheet_value"),
            ]
        )
        current_row = sheet.max_row
        if row.get("status") == "mismatch":
            for column_index in range(4, 7):
                sheet.cell(row=current_row, column=column_index).fill = HIGHLIGHT_FILL
        if embed_images:
            _embed_row_images(sheet, row, current_row)

    output = Path(output_path)
    workbook.save(output)
    return output


def _embed_row_images(sheet, row: dict[str, str | None], current_row: int) -> None:
    pid_image_path = row.get("pid_image_path")
    datasheet_image_path = row.get("datasheet_image_path")

    if pid_image_path and Path(pid_image_path).exists():
        pid_image = OpenPyxlImage(pid_image_path)
        pid_image.width = 40
        pid_image.height = 40
        sheet.add_image(pid_image, f"H{current_row}")

    if datasheet_image_path and Path(datasheet_image_path).exists():
        datasheet_image = OpenPyxlImage(datasheet_image_path)
        datasheet_image.width = 40
        datasheet_image.height = 40
        sheet.add_image(datasheet_image, f"I{current_row}")
