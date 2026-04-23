import pandas as pd

from check_int.domain.enums import DocumentType
from check_int.services.eq_list_parser import parse_eq_list
from check_int.services.record_mapper import map_structured_row_to_equipment_record


COMMON_FIELDS = {
    "tag_no": "P-201",
    "equipment_name": "Booster Pump",
    "service": "Cooling Water",
    "capacity": "120 m3/h",
    "size": '3"',
    "model": "BP-120",
    "rating": "150#",
    "material": "SS316",
    "design_pressure": "12 bar",
    "design_temperature": "90 C",
    "operating_temperature": "75 C",
    "page_no": 3,
}


def test_map_structured_row_to_equipment_record_creates_common_domain_object() -> None:
    record = map_structured_row_to_equipment_record(
        COMMON_FIELDS,
        document_type=DocumentType.PID,
        source_file="pid_sample.pdf",
    )

    assert record.document_type is DocumentType.PID
    assert record.tag_no == "P-201"
    assert record.equipment_name == "Booster Pump"
    assert record.design_pressure == "12 bar"
    assert record.capacity == "120 m3/h"
    assert record.model == "BP-120"
    assert record.operating_temperature == "75 C"
    assert record.source_file == "pid_sample.pdf"
    assert record.page_no == 3


def test_parse_eq_list_reads_excel_and_returns_equipment_records(tmp_path) -> None:
    excel_path = tmp_path / "eq_list.xlsx"
    frame = pd.DataFrame(
        [
            {
                "tag_no": "P-201",
                "equipment_name": "Booster Pump",
                "service": "Cooling Water",
                "size": '3"',
                "rating": "150#",
                "material": "SS316",
                "design_pressure": "12 bar",
                "design_temperature": "90 C",
            },
            {
                "tag_no": "E-101",
                "equipment_name": "Heat Exchanger",
                "service": "Hot Oil",
                "size": '6"',
                "rating": "300#",
                "material": "CS",
                "design_pressure": "20 bar",
                "design_temperature": "180 C",
            },
        ]
    )
    frame.to_excel(excel_path, index=False)

    records = parse_eq_list(excel_path)

    assert [record.tag_no for record in records] == ["P-201", "E-101"]
    assert all(record.document_type is DocumentType.EQ_LIST for record in records)
    assert records[1].equipment_name == "Heat Exchanger"
