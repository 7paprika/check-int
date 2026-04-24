from collections import Counter, defaultdict

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
    pid_by_tag = _group_by_tag(pid_records)
    datasheet_by_tag = _group_by_tag(datasheet_records)
    master_tags = {record.tag_no for record in master_records}

    results: list[IntegrityCheckResult] = []

    for master in master_records:
        pid_matches = pid_by_tag.get(master.tag_no, [])
        datasheet_matches = datasheet_by_tag.get(master.tag_no, [])
        pid_record = pid_matches[0] if pid_matches else None
        datasheet_record = datasheet_matches[0] if datasheet_matches else None

        comparisons: list[FieldComparisonResult] = []
        counts: Counter[ComparisonStatus] = Counter()

        duplicate_comparison = _build_duplicate_comparison(master, pid_matches, datasheet_matches)
        if duplicate_comparison is not None:
            comparisons.append(duplicate_comparison)
            counts[ComparisonStatus.DUPLICATE_TAG] += 1

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

    results.extend(_build_target_only_results(pid_by_tag, datasheet_by_tag, master_tags))
    return results


def _group_by_tag(records: list[EquipmentRecord]) -> dict[str, list[EquipmentRecord]]:
    grouped: dict[str, list[EquipmentRecord]] = defaultdict(list)
    for record in records:
        grouped[record.tag_no].append(record)
    return dict(grouped)


def _build_duplicate_comparison(
    master: EquipmentRecord,
    pid_matches: list[EquipmentRecord],
    datasheet_matches: list[EquipmentRecord],
) -> FieldComparisonResult | None:
    if len(pid_matches) <= 1 and len(datasheet_matches) <= 1:
        return None
    return FieldComparisonResult(
        field_name="tag_no",
        master_value=master.tag_no,
        pid_value=_tag_count_label(master.tag_no, pid_matches),
        datasheet_value=_tag_count_label(master.tag_no, datasheet_matches),
        status=ComparisonStatus.DUPLICATE_TAG,
        master_evidence=master.evidence[0] if master.evidence else None,
        pid_evidence=pid_matches[0].evidence[0] if pid_matches and pid_matches[0].evidence else None,
        datasheet_evidence=(
            datasheet_matches[0].evidence[0]
            if datasheet_matches and datasheet_matches[0].evidence
            else None
        ),
    )


def _tag_count_label(tag_no: str, matches: list[EquipmentRecord]) -> str | None:
    if not matches:
        return None
    if len(matches) == 1:
        return tag_no
    return f"{tag_no} x{len(matches)}"


def _build_target_only_results(
    pid_by_tag: dict[str, list[EquipmentRecord]],
    datasheet_by_tag: dict[str, list[EquipmentRecord]],
    master_tags: set[str],
) -> list[IntegrityCheckResult]:
    target_tags = set(pid_by_tag) | set(datasheet_by_tag)
    extra_tags = sorted(target_tags - master_tags)
    results: list[IntegrityCheckResult] = []
    for tag_no in extra_tags:
        pid_record = pid_by_tag.get(tag_no, [None])[0]
        datasheet_record = datasheet_by_tag.get(tag_no, [None])[0]
        comparison = FieldComparisonResult(
            field_name="tag_no",
            master_value=None,
            pid_value=tag_no if pid_record else None,
            datasheet_value=tag_no if datasheet_record else None,
            status=ComparisonStatus.MISSING_SOURCE,
            pid_evidence=pid_record.evidence[0] if pid_record and pid_record.evidence else None,
            datasheet_evidence=(
                datasheet_record.evidence[0]
                if datasheet_record and datasheet_record.evidence
                else None
            ),
        )
        results.append(
            IntegrityCheckResult(
                tag_no=tag_no,
                comparisons=[comparison],
                summary={ComparisonStatus.MISSING_SOURCE: 1},
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
