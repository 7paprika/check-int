from check_int.domain.enums import DocumentType
from check_int.services.datasheet_parser import parse_datasheet_rows
from check_int.services.pid_parser import parse_pid_rows


def test_parse_pid_rows_maps_stub_rows_into_equipment_records() -> None:
    rows = [
        {
            "tag_no": "P-301",
            "equipment_name": "Transfer Pump",
            "service": "Product",
            "design_pressure": "8 bar",
            "material": "SS304",
            "page_no": 1,
            "bbox": (10, 20, 110, 120),
            "image_path": "/tmp/pid-crop.png",
            "raw_text": "TAG=P-301\nMATERIAL=SS304",
            "confidence": 0.91,
        }
    ]

    records = parse_pid_rows(rows, source_file="pid_stub.json")

    assert len(records) == 1
    assert records[0].document_type is DocumentType.PID
    assert records[0].tag_no == "P-301"
    assert records[0].source_file == "pid_stub.json"
    assert records[0].evidence[0].page_no == 1
    assert records[0].evidence[0].bbox == (10, 20, 110, 120)
    assert records[0].evidence[0].image_path == "/tmp/pid-crop.png"
    assert records[0].evidence[0].raw_text == "TAG=P-301\nMATERIAL=SS304"
    assert records[0].evidence[0].confidence == 0.91


def test_parse_datasheet_rows_maps_stub_rows_into_equipment_records() -> None:
    rows = [
        {
            "tag_no": "P-301",
            "equipment_name": "Transfer Pump",
            "service": "Product",
            "design_pressure": "8 bar",
            "material": "SS304",
            "page_no": 4,
        }
    ]

    records = parse_datasheet_rows(rows, source_file="datasheet_stub.json")

    assert len(records) == 1
    assert records[0].document_type is DocumentType.DATASHEET
    assert records[0].page_no == 4
    assert records[0].equipment_name == "Transfer Pump"
