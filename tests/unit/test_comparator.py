from check_int.domain.enums import ComparisonStatus, DocumentType
from check_int.domain.models import DocumentEvidence, EquipmentRecord
from check_int.services.comparator import compare_equipment_records
from check_int.services.result_formatter import flatten_comparison_results


FIELDS = [
    "service",
    "material",
    "capacity",
    "size",
    "model",
    "design_temperature",
    "design_pressure",
    "operating_pressure",
    "operating_temperature",
]


def make_record(document_type: DocumentType, tag_no: str, **fields: str | None) -> EquipmentRecord:
    return EquipmentRecord(
        document_type=document_type,
        tag_no=tag_no,
        equipment_name=fields.get("equipment_name"),
        service=fields.get("service"),
        capacity=fields.get("capacity"),
        size=fields.get("size"),
        model=fields.get("model"),
        rating=fields.get("rating"),
        material=fields.get("material"),
        design_pressure=fields.get("design_pressure"),
        design_temperature=fields.get("design_temperature"),
        operating_pressure=fields.get("operating_pressure"),
        operating_temperature=fields.get("operating_temperature"),
        source_file=f"{document_type.value}.pdf",
    )


def test_compare_equipment_records_marks_expanded_field_states() -> None:
    master = [
        make_record(
            DocumentType.EQ_LIST,
            "P-101",
            service="Cooling Water",
            capacity="100 m3/h",
            size='2"',
            model="PMP-100",
            design_temperature="120 C",
            design_pressure="10 BAR",
            operating_pressure="8 bar",
            operating_temperature="90 C",
            material="SS316",
        )
    ]
    pid = [
        make_record(
            DocumentType.PID,
            "P-101",
            service=" cooling   water ",
            capacity="100 m3/h",
            size='2"',
            model="PMP-100A",
            design_temperature="120 C",
            design_pressure="10 bar",
            operating_pressure="8 bar",
            operating_temperature="95 C",
            material="CS",
        )
    ]
    datasheet = [
        make_record(
            DocumentType.DATASHEET,
            "P-101",
            service="Cooling Water",
            capacity="100 m3/h",
            size='2"',
            model="PMP-100",
            design_temperature="120 C",
            design_pressure=None,
            operating_pressure="8 bar",
            operating_temperature="90 C",
            material="SS316",
        )
    ]

    results = compare_equipment_records(master, pid, datasheet, fields=FIELDS)

    assert len(results) == 1
    result = results[0]
    assert result.tag_no == "P-101"

    by_field = {item.field_name: item for item in result.comparisons}
    assert by_field["service"].status is ComparisonStatus.MATCHED
    assert by_field["capacity"].status is ComparisonStatus.MATCHED
    assert by_field["size"].status is ComparisonStatus.MATCHED
    assert by_field["design_temperature"].status is ComparisonStatus.MATCHED
    assert by_field["operating_pressure"].status is ComparisonStatus.MATCHED
    assert by_field["model"].status is ComparisonStatus.MISMATCH
    assert by_field["design_pressure"].status is ComparisonStatus.MISSING_TARGET
    assert by_field["operating_temperature"].status is ComparisonStatus.MISMATCH
    assert by_field["material"].status is ComparisonStatus.MISMATCH
    assert result.summary[ComparisonStatus.MATCHED] == 5
    assert result.summary[ComparisonStatus.MISSING_TARGET] == 1
    assert result.summary[ComparisonStatus.MISMATCH] == 3


def test_compare_equipment_records_adds_master_rows_even_when_related_documents_are_missing() -> None:
    master = [
        make_record(
            DocumentType.EQ_LIST,
            "P-102",
            service="Nitrogen",
            capacity="50 m3/h",
            size='1"',
            model="N2-50",
            design_temperature="80 C",
            design_pressure="5 bar",
            operating_pressure="4 bar",
            operating_temperature="55 C",
            material="CS",
        )
    ]

    results = compare_equipment_records(master, [], [], fields=FIELDS)

    result = results[0]
    statuses = {item.field_name: item.status for item in result.comparisons}
    assert statuses == {
        "service": ComparisonStatus.MISSING_TARGET,
        "material": ComparisonStatus.MISSING_TARGET,
        "capacity": ComparisonStatus.MISSING_TARGET,
        "size": ComparisonStatus.MISSING_TARGET,
        "model": ComparisonStatus.MISSING_TARGET,
        "design_temperature": ComparisonStatus.MISSING_TARGET,
        "design_pressure": ComparisonStatus.MISSING_TARGET,
        "operating_pressure": ComparisonStatus.MISSING_TARGET,
        "operating_temperature": ComparisonStatus.MISSING_TARGET,
    }


def test_flatten_comparison_results_returns_rows_for_ui_tables() -> None:
    master = [
        make_record(
            DocumentType.EQ_LIST,
            "P-103",
            service="Air",
            capacity="30 m3/h",
            size='1"',
            model="AIR-30",
            design_temperature="60 C",
            design_pressure="6 bar",
            operating_pressure="5 bar",
            operating_temperature="45 C",
            material="SS304",
        )
    ]
    pid = [
        make_record(
            DocumentType.PID,
            "P-103",
            service="Air",
            capacity="30 m3/h",
            size='1"',
            model="AIR-30",
            design_temperature="60 C",
            design_pressure="7 bar",
            operating_pressure="5 bar",
            operating_temperature="45 C",
            material="SS304",
        )
    ]
    pid[0].evidence.append(
        DocumentEvidence(
            page_no=2,
            bbox=(1, 2, 30, 40),
            image_path="pid-crop.png",
            raw_text="DESIGN PRESSURE=7 bar",
        )
    )
    datasheet = [
        make_record(
            DocumentType.DATASHEET,
            "P-103",
            service="Air",
            capacity="30 m3/h",
            size='1"',
            model="AIR-30",
            design_temperature="60 C",
            design_pressure="6 bar",
            operating_pressure="5 bar",
            operating_temperature="45 C",
            material="SS304",
        )
    ]
    datasheet[0].evidence.append(
        DocumentEvidence(
            page_no=5,
            bbox=(5, 6, 70, 80),
            image_path="datasheet-crop.png",
            raw_text="DESIGN PRESSURE=6 bar",
        )
    )

    rows = flatten_comparison_results(
        compare_equipment_records(master, pid, datasheet, fields=FIELDS)
    )

    assert rows[0]["tag_no"] == "P-103"
    assert rows[0]["field_name"] == "service"
    pressure_row = next(row for row in rows if row["field_name"] == "design_pressure")
    assert pressure_row["status"] == "mismatch"
    assert pressure_row["master_value"] == "6 bar"
    assert pressure_row["pid_value"] == "7 bar"
    assert pressure_row["datasheet_value"] == "6 bar"
    assert pressure_row["pid_image_path"] == "pid-crop.png"
    assert pressure_row["pid_page_no"] == 2
    assert pressure_row["pid_bbox"] == (1, 2, 30, 40)
    assert pressure_row["pid_raw_text"] == "DESIGN PRESSURE=7 bar"
    assert pressure_row["datasheet_image_path"] == "datasheet-crop.png"
    assert pressure_row["datasheet_page_no"] == 5
    assert pressure_row["datasheet_bbox"] == (5, 6, 70, 80)
    assert pressure_row["datasheet_raw_text"] == "DESIGN PRESSURE=6 bar"


def test_compare_equipment_records_reports_target_only_tags_as_missing_source() -> None:
    results = compare_equipment_records(
        [make_record(DocumentType.EQ_LIST, "P-300", service="Water")],
        [make_record(DocumentType.PID, "P-301", service="Steam")],
        [make_record(DocumentType.DATASHEET, "P-301", service="Steam")],
        fields=FIELDS,
    )

    extra = next(result for result in results if result.tag_no == "P-301")
    assert len(extra.comparisons) == 1
    comparison = extra.comparisons[0]
    assert comparison.field_name == "tag_no"
    assert comparison.status is ComparisonStatus.MISSING_SOURCE
    assert comparison.master_value is None
    assert comparison.pid_value == "P-301"
    assert comparison.datasheet_value == "P-301"


def test_compare_equipment_records_reports_duplicate_target_tags() -> None:
    results = compare_equipment_records(
        [make_record(DocumentType.EQ_LIST, "P-400", service="Water")],
        [
            make_record(DocumentType.PID, "P-400", service="Water"),
            make_record(DocumentType.PID, "P-400", service="Steam"),
        ],
        [make_record(DocumentType.DATASHEET, "P-400", service="Water")],
        fields=FIELDS,
    )

    duplicate_row = next(
        comparison for comparison in results[0].comparisons if comparison.field_name == "tag_no"
    )
    assert duplicate_row.status is ComparisonStatus.DUPLICATE_TAG
    assert duplicate_row.pid_value == "P-400 x2"


def test_compare_equipment_records_treats_different_tag_numbers_as_missing_related_documents() -> None:
    master = [make_record(DocumentType.EQ_LIST, "P-200", service="Water", material="SS316")]
    pid = [make_record(DocumentType.PID, "P-201", service="Water", material="SS316")]
    datasheet = [make_record(DocumentType.DATASHEET, "P-201", service="Water", material="SS316")]

    results = compare_equipment_records(master, pid, datasheet, fields=FIELDS)

    statuses = {item.field_name: item.status for item in results[0].comparisons}
    assert statuses["service"] is ComparisonStatus.MISSING_TARGET
    assert statuses["material"] is ComparisonStatus.MISSING_TARGET
