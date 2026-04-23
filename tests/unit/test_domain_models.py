from check_int.domain.enums import ComparisonStatus, DocumentType
from check_int.domain.models import (
    DocumentEvidence,
    EquipmentRecord,
    FieldComparisonResult,
    IntegrityCheckResult,
)
from check_int.domain.normalization import normalize_field_value


def test_document_type_and_comparison_status_values_are_defined() -> None:
    assert DocumentType.EQ_LIST.value == "eq_list"
    assert DocumentType.PID.value == "pid"
    assert DocumentType.DATASHEET.value == "datasheet"
    assert ComparisonStatus.MATCHED.value == "matched"
    assert ComparisonStatus.MISMATCH.value == "mismatch"


def test_document_evidence_and_equipment_record_store_core_metadata() -> None:
    evidence = DocumentEvidence(
        page_no=2,
        bbox=(10, 20, 100, 120),
        image_path="artifacts/pid/tag-p-101.png",
        raw_text="TAG: P-101",
        note="Detected from P&ID spec box",
    )

    record = EquipmentRecord(
        document_type=DocumentType.PID,
        tag_no="P-101",
        equipment_name="Feed Pump",
        service="Process Water",
        size='2"',
        rating="150#",
        material="SS316",
        design_pressure="10 bar",
        design_temperature="80 C",
        source_file="pid.pdf",
        page_no=2,
        evidence=[evidence],
    )

    assert record.document_type is DocumentType.PID
    assert record.tag_no == "P-101"
    assert record.evidence[0].raw_text == "TAG: P-101"
    assert record.page_no == 2


def test_field_comparison_result_keeps_values_and_evidence_references() -> None:
    pid_evidence = DocumentEvidence(page_no=1, raw_text="10 bar")
    datasheet_evidence = DocumentEvidence(page_no=4, raw_text="12 bar")

    result = FieldComparisonResult(
        field_name="design_pressure",
        master_value="10 bar",
        pid_value="10 bar",
        datasheet_value="12 bar",
        status=ComparisonStatus.MISMATCH,
        master_evidence=None,
        pid_evidence=pid_evidence,
        datasheet_evidence=datasheet_evidence,
    )

    assert result.field_name == "design_pressure"
    assert result.status is ComparisonStatus.MISMATCH
    assert result.pid_evidence is pid_evidence
    assert result.datasheet_evidence is datasheet_evidence


def test_integrity_check_result_groups_field_results_per_tag() -> None:
    field_result = FieldComparisonResult(
        field_name="service",
        master_value="Cooling Water",
        pid_value="Cooling Water",
        datasheet_value="Cooling Water",
        status=ComparisonStatus.MATCHED,
    )

    result = IntegrityCheckResult(
        tag_no="P-101",
        comparisons=[field_result],
        summary={
            ComparisonStatus.MATCHED: 1,
            ComparisonStatus.MISMATCH: 0,
        },
    )

    assert result.tag_no == "P-101"
    assert result.comparisons[0].field_name == "service"
    assert result.summary[ComparisonStatus.MATCHED] == 1


def test_normalize_field_value_trims_collapses_spaces_and_lowercases() -> None:
    assert normalize_field_value("  DESIGN   PRESSURE  ") == "design pressure"


def test_normalize_field_value_returns_none_for_blank_input() -> None:
    assert normalize_field_value("   ") is None
    assert normalize_field_value(None) is None
