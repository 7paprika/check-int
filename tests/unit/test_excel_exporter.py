from openpyxl import load_workbook

from check_int.services.excel_exporter import export_comparison_rows_to_excel


def test_export_comparison_rows_to_excel_writes_rows_and_highlights_mismatch(tmp_path) -> None:
    output_path = tmp_path / "integrity-report.xlsx"
    rows = [
        {
            "tag_no": "P-601",
            "field_name": "service",
            "status": "matched",
            "master_value": "Cooling Water",
            "pid_value": "Cooling Water",
            "datasheet_value": "Cooling Water",
        },
        {
            "tag_no": "P-601",
            "field_name": "material",
            "status": "mismatch",
            "master_value": "SS316",
            "pid_value": "CS",
            "datasheet_value": "SS316",
        },
    ]

    export_comparison_rows_to_excel(rows, output_path)

    workbook = load_workbook(output_path)
    sheet = workbook["Integrity Report"]

    assert sheet["A2"].value == "P-601"
    assert sheet["B3"].value == "material"
    assert sheet["C3"].value == "mismatch"
    assert sheet["E3"].value == "CS"
    assert sheet["F3"].value == "SS316"
    assert sheet["E3"].fill.fill_type == "solid"
    assert sheet["E3"].fill.fgColor.rgb.endswith("FFF1B3")
