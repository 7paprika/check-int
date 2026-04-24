from check_int.domain.models import DocumentEvidence, IntegrityCheckResult


def _evidence_row(prefix: str, evidence: DocumentEvidence | None) -> dict[str, object | None]:
    return {
        f"{prefix}_image_path": evidence.image_path if evidence else None,
        f"{prefix}_page_no": evidence.page_no if evidence else None,
        f"{prefix}_bbox": evidence.bbox if evidence else None,
        f"{prefix}_raw_text": evidence.raw_text if evidence else None,
        f"{prefix}_confidence": evidence.confidence if evidence else None,
    }


def flatten_comparison_results(results: list[IntegrityCheckResult]) -> list[dict[str, object | None]]:
    rows: list[dict[str, object | None]] = []

    for result in results:
        for comparison in result.comparisons:
            row = {
                "tag_no": result.tag_no,
                "field_name": comparison.field_name,
                "status": comparison.status.value,
                "master_value": comparison.master_value,
                "pid_value": comparison.pid_value,
                "datasheet_value": comparison.datasheet_value,
            }
            row.update(_evidence_row("master", comparison.master_evidence))
            row.update(_evidence_row("pid", comparison.pid_evidence))
            row.update(_evidence_row("datasheet", comparison.datasheet_evidence))
            rows.append(row)

    return rows