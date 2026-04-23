from check_int.domain.enums import ComparisonStatus, DocumentType
from check_int.domain.models import EquipmentRecord
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
    assert by_field["model"].status is ComparisonStatus.MISMATCH
    assert by_field["design_pressure"].status is ComparisonStatus.MISSING_TARGET
    assert by_field["operating_temperature"].status is ComparisonStatus.MISMATCH
    assert by_field["material"].status is ComparisonStatus.MISMATCH
    assert result.summary[ComparisonStatus.MATCHED] == 4
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
            operating_temperature="45 C",
            material="SS304",
        )
    ]
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
            operating_temperature="45 C",
            material="SS304",
        )
    ]

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


def test_compare_equipment_records_treats_different_tag_numbers_as_missing_related_documents() -> None:
    master = [make_record(DocumentType.EQ_LIST, "P-200", service="Water", material="SS316")]
    pid = [make_record(DocumentType.PID, "P-201", service="Water", material="SS316")]
    datasheet = [make_record(DocumentType.DATASHEET, "P-201", service="Water", material="SS316")]

    results = compare_equipment_records(master, pid, datasheet, fields=FIELDS)

    statuses = {item.field_name: item.status for item in results[0].comparisons}
    assert statuses["service"] is ComparisonStatus.MISSING_TARGET
    assert statuses["material"] is ComparisonStatus.MISSING_TARGET
