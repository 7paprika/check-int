from pathlib import Path

from check_int.adapters.ocr_engine import PaddleOcrEngine
from check_int.adapters.pdf_loader import MuPdfLoader
from check_int.adapters.structured_extractor import HybridStructuredExtractor
from check_int.adapters.vision_detector import StubVisionDetector
from check_int.config import AppConfig
from check_int.domain.enums import DocumentType
from check_int.services.comparator import compare_equipment_records
from check_int.services.datasheet_parser import parse_datasheet_rows
from check_int.services.eq_list_parser import parse_eq_list
from check_int.services.pid_parser import parse_pid_rows
from check_int.services.pipeline import DocumentProcessingPipeline
from check_int.services.result_formatter import flatten_comparison_results


DEFAULT_COMPARE_FIELDS = [
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

    @classmethod
    def from_adapter_factories(
        cls,
        *,
        pid_pipeline_factory,
        datasheet_pipeline_factory,
        compare_fields: list[str] | None = None,
    ):
        return cls(
            pid_pipeline=pid_pipeline_factory(),
            datasheet_pipeline=datasheet_pipeline_factory(),
            compare_fields=compare_fields,
        )

    @staticmethod
    def build_pipeline(*, loader, detector, ocr_engine, structured_extractor) -> DocumentProcessingPipeline:
        return DocumentProcessingPipeline(loader, detector, ocr_engine, structured_extractor)

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


def build_default_use_case(config: AppConfig) -> IntegrityCheckUseCase:
    pid_pipeline = _build_local_pdf_pipeline(config, document_cache_name="pid")
    datasheet_pipeline = _build_local_pdf_pipeline(config, document_cache_name="datasheet")
    return IntegrityCheckUseCase(pid_pipeline=pid_pipeline, datasheet_pipeline=datasheet_pipeline)


def _build_local_pdf_pipeline(config: AppConfig, *, document_cache_name: str) -> DocumentProcessingPipeline:
    cache_dir = config.artifacts_dir / document_cache_name
    return DocumentProcessingPipeline(
        loader=MuPdfLoader(output_dir=cache_dir / "pages"),
        detector=StubVisionDetector(),
        ocr_engine=PaddleOcrEngine(),
        structured_extractor=HybridStructuredExtractor(),
    )
