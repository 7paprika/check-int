from check_int.domain.models import IntegrityCheckResult


def flatten_comparison_results(results: list[IntegrityCheckResult]) -> list[dict[str, str | None]]:
    rows: list[dict[str, str | None]] = []

    for result in results:
        for comparison in result.comparisons:
            rows.append(
                {
                    "tag_no": result.tag_no,
                    "field_name": comparison.field_name,
                    "status": comparison.status.value,
                    "master_value": comparison.master_value,
                    "pid_value": comparison.pid_value,
                    "datasheet_value": comparison.datasheet_value,
                    "pid_image_path": comparison.pid_evidence.image_path if comparison.pid_evidence else None,
                    "datasheet_image_path": (
                        comparison.datasheet_evidence.image_path if comparison.datasheet_evidence else None
                    ),
                }
            )

    return rows