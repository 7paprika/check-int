from PIL import Image
from openpyxl import load_workbook

from check_int.services.excel_exporter import export_comparison_rows_to_excel


def test_export_comparison_rows_to_excel_embeds_evidence_images(tmp_path) -> None:
    output_path = tmp_path / "integrity-report.xlsx"
    evidence_path = tmp_path / "pid-evidence.png"
    Image.new("RGB", (30, 30), color="green").save(evidence_path)

    rows = [
        {
            "tag_no": "P-1601",
            "field_name": "material",
            "status": "mismatch",
            "master_value": "SS316",
            "pid_value": "CS",
            "datasheet_value": "SS316",
            "pid_image_path": str(evidence_path),
            "datasheet_image_path": str(evidence_path),
        }
    ]

    export_comparison_rows_to_excel(rows, output_path, embed_images=True)

    workbook = load_workbook(output_path)
    sheet = workbook["Integrity Report"]
    assert sheet["H1"].value == "P&ID Evidence"
    assert sheet["I1"].value == "Datasheet Evidence"
    assert sheet.column_dimensions["H"].width >= 12
    assert sheet.row_dimensions[2].height >= 40
    assert len(sheet._images) == 2
