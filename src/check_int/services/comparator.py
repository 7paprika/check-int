from collections import Counter

from check_int.domain.enums import ComparisonStatus
from check_int.domain.models import EquipmentRecord, FieldComparisonResult, IntegrityCheckResult
from check_int.domain.normalization import normalize_field_value


def compare_equipment_records(
    master_records: list[EquipmentRecord],
    pid_records: list[EquipmentRecord],
    datasheet_records: list[EquipmentRecord],
    *,
    fields: list[str],
) -> list[IntegrityCheckResult]:
    pid_by_tag = {record.tag_no: record for record in pid_records}
    datasheet_by_tag = {record.tag_no: record for record in datasheet_records}

    results: list[IntegrityCheckResult] = []

    for master in master_records:
        pid_record = pid_by_tag.get(master.tag_no)
        datasheet_record = datasheet_by_tag.get(master.tag_no)

        comparisons: list[FieldComparisonResult] = []
        counts: Counter[ComparisonStatus] = Counter()

        for field_name in fields:
            master_value = getattr(master, field_name)
            pid_value = getattr(pid_record, field_name) if pid_record else None
            datasheet_value = getattr(datasheet_record, field_name) if datasheet_record else None

            status = _determine_status(master_value, pid_value, datasheet_value)
            counts[status] += 1
            comparisons.append(
                FieldComparisonResult(
                    field_name=field_name,
                    master_value=master_value,
                    pid_value=pid_value,
                    datasheet_value=datasheet_value,
                    status=status,
                    master_evidence=master.evidence[0] if master.evidence else None,
                    pid_evidence=pid_record.evidence[0] if pid_record and pid_record.evidence else None,
                    datasheet_evidence=(
                        datasheet_record.evidence[0]
                        if datasheet_record and datasheet_record.evidence
                        else None
                    ),
                )
            )

        results.append(
            IntegrityCheckResult(
                tag_no=master.tag_no,
                comparisons=comparisons,
                summary=dict(counts),
            )
        )

    return results


def _determine_status(
    master_value: str | None,
    pid_value: str | None,
    datasheet_value: str | None,
) -> ComparisonStatus:
    normalized_master = normalize_field_value(master_value)
    normalized_pid = normalize_field_value(pid_value)
    normalized_datasheet = normalize_field_value(datasheet_value)

    if normalized_pid is None and normalized_datasheet is None:
        return ComparisonStatus.MISSING_TARGET
    if normalized_master is None:
        return ComparisonStatus.MISSING_SOURCE
    if normalized_pid is None or normalized_datasheet is None:
        return ComparisonStatus.MISSING_TARGET
    if normalized_master == normalized_pid == normalized_datasheet:
        return ComparisonStatus.MATCHED
    return ComparisonStatus.MISMATCH