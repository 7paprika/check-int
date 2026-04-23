from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenPyxlImage
from openpyxl.styles import PatternFill


HIGHLIGHT_FILL = PatternFill(fill_type="solid", fgColor="FFF1B3")
HEADERS = ["tag_no", "field_name", "status", "master_value", "pid_value", "datasheet_value"]


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
        sheet.append([row.get(header) for header in HEADERS])
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
