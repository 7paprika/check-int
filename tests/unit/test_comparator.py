from check_int.domain.enums import ComparisonStatus, DocumentType
from check_int.domain.models import EquipmentRecord
from check_int.services.comparator import compare_equipment_records
from check_int.services.result_formatter import flatten_comparison_results


FIELDS = ["service", "design_pressure", "material"]


def make_record(document_type: DocumentType, tag_no: str, **fields: str | None) -> EquipmentRecord:
    return EquipmentRecord(
        document_type=document_type,
        tag_no=tag_no,
        equipment_name=fields.get("equipment_name"),
        service=fields.get("service"),
        size=fields.get("size"),
        rating=fields.get("rating"),
        material=fields.get("material"),
        design_pressure=fields.get("design_pressure"),
        design_temperature=fields.get("design_temperature"),
        source_file=f"{document_type.value}.pdf",
    )


def test_compare_equipment_records_marks_matched_mismatch_and_missing_states() -> None:
    master = [
        make_record(
            DocumentType.EQ_LIST,
            "P-101",
            service="Cooling Water",
            design_pressure="10 BAR",
            material="SS316",
        )
    ]
    pid = [
        make_record(
            DocumentType.PID,
            "P-101",
            service=" cooling   water ",
            design_pressure="10 bar",
            material="CS",
        )
    ]
    datasheet = [
        make_record(
            DocumentType.DATASHEET,
            "P-101",
            service="Cooling Water",
            design_pressure=None,
            material="SS316",
        )
    ]

    results = compare_equipment_records(master, pid, datasheet, fields=FIELDS)

    assert len(results) == 1
    result = results[0]
    assert result.tag_no == "P-101"

    by_field = {item.field_name: item for item in result.comparisons}
    assert by_field["service"].status is ComparisonStatus.MATCHED
    assert by_field["design_pressure"].status is ComparisonStatus.MISSING_TARGET
    assert by_field["material"].status is ComparisonStatus.MISMATCH
    assert result.summary[ComparisonStatus.MATCHED] == 1
    assert result.summary[ComparisonStatus.MISSING_TARGET] == 1
    assert result.summary[ComparisonStatus.MISMATCH] == 1


def test_compare_equipment_records_adds_master_rows_even_when_related_documents_are_missing() -> None:
    master = [
        make_record(
            DocumentType.EQ_LIST,
            "P-102",
            service="Nitrogen",
            design_pressure="5 bar",
            material="CS",
        )
    ]

    results = compare_equipment_records(master, [], [], fields=FIELDS)

    result = results[0]
    statuses = {item.field_name: item.status for item in result.comparisons}
    assert statuses == {
        "service": ComparisonStatus.MISSING_TARGET,
        "design_pressure": ComparisonStatus.MISSING_TARGET,
        "material": ComparisonStatus.MISSING_TARGET,
    }


def test_flatten_comparison_results_returns_rows_for_ui_tables() -> None:
    master = [
        make_record(
            DocumentType.EQ_LIST,
            "P-103",
            service="Air",
            design_pressure="6 bar",
            material="SS304",
        )
    ]
    pid = [
        make_record(
            DocumentType.PID,
            "P-103",
            service="Air",
            design_pressure="7 bar",
            material="SS304",
        )
    ]
    datasheet = [
        make_record(
            DocumentType.DATASHEET,
            "P-103",
            service="Air",
            design_pressure="6 bar",
            material="SS304",
        )
    ]

    rows = flatten_comparison_results(
        compare_equipment_records(master, pid, datasheet, fields=FIELDS)
    )

    assert rows[0]["tag_no"] == "P-103"
    assert rows[0]["field_name"] == "service"
    assert rows[1]["field_name"] == "design_pressure"
    assert rows[1]["status"] == "mismatch"
    assert rows[1]["master_value"] == "6 bar"
    assert rows[1]["pid_value"] == "7 bar"
    assert rows[1]["datasheet_value"] == "6 bar"
