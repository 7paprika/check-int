from pathlib import Path

from check_int.domain.enums import DocumentType
from check_int.services.comparator import compare_equipment_records
from check_int.services.datasheet_parser import parse_datasheet_rows
from check_int.services.eq_list_parser import parse_eq_list
from check_int.services.pid_parser import parse_pid_rows
from check_int.services.result_formatter import flatten_comparison_results


DEFAULT_COMPARE_FIELDS = [
    "service",
    "design_pressure",
    "material",
]


class IntegrityCheckUseCase:
    def __init__(
        self,
        *,
        pid_pipeline,
        datasheet_pipeline,
        compare_fields: list[str] | None = None,
    ) -> None:
        self.pid_pipeline = pid_pipeline
        self.datasheet_pipeline = datasheet_pipeline
        self.compare_fields = compare_fields or DEFAULT_COMPARE_FIELDS

    def run(
        self,
        *,
        eq_list_path: str | Path,
        pid_path: str | Path,
        datasheet_path: str | Path,
    ) -> list[dict[str, str | None]]:
        master_records = parse_eq_list(eq_list_path)

        pid_processed = self.pid_pipeline.process_document(
            str(pid_path),
            document_type=DocumentType.PID,
        )
        datasheet_processed = self.datasheet_pipeline.process_document(
            str(datasheet_path),
            document_type=DocumentType.DATASHEET,
        )

        pid_records = parse_pid_rows(pid_processed.structured_rows, source_file=Path(pid_path).name)
        datasheet_records = parse_datasheet_rows(
            datasheet_processed.structured_rows,
            source_file=Path(datasheet_path).name,
        )

        return flatten_comparison_results(
            compare_equipment_records(
                master_records,
                pid_records,
                datasheet_records,
                fields=self.compare_fields,
            )
        )