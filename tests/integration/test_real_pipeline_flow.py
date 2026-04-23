from pathlib import Path

import pandas as pd

from check_int.adapters.ocr_engine import StubOcrEngine
from check_int.adapters.pdf_loader import PageImage, StubPdfLoader
from check_int.adapters.structured_extractor import StubStructuredExtractor
from check_int.adapters.vision_detector import DetectedRegion, StubVisionDetector
from check_int.app.use_cases import IntegrityCheckUseCase


def test_integrity_check_use_case_builds_realistic_pipeline_from_adapter_factories(tmp_path) -> None:
    eq_list_path = tmp_path / "eq_list.xlsx"
    pd.DataFrame(
        [
            {
                "tag_no": "P-1301",
                "service": "Cooling Water",
                "material": "SS316",
                "design_pressure": "10 bar",
            }
        ]
    ).to_excel(eq_list_path, index=False)

    page_path = tmp_path / "page.png"
    page_path.write_bytes(b"fake-image")

    def pipeline_factory(document_type):
        structured = {
            "tag_no": "P-1301",
            "service": "Cooling Water",
            "material": "CS" if document_type.value == "pid" else "SS316",
            "design_pressure": "10 bar",
        }
        return IntegrityCheckUseCase.build_pipeline(
            loader=StubPdfLoader([PageImage(page_no=1, source_path="sample.pdf", image_ref=str(page_path))]),
            detector=StubVisionDetector(
                [DetectedRegion(page_no=1, label="spec_box", bbox=(0, 0, 10, 10), crop_ref=str(page_path))]
            ),
            ocr_engine=StubOcrEngine({str(page_path): "stub text"}),
            structured_extractor=StubStructuredExtractor(structured),
        )

    use_case = IntegrityCheckUseCase.from_adapter_factories(
        pid_pipeline_factory=lambda: pipeline_factory(document_type=type("DT", (), {"value": "pid"})()),
        datasheet_pipeline_factory=lambda: pipeline_factory(document_type=type("DT", (), {"value": "datasheet"})()),
    )

    rows = use_case.run(
        eq_list_path=Path(eq_list_path),
        pid_path=Path("pid.pdf"),
        datasheet_path=Path("datasheet.pdf"),
    )

    mismatch_rows = [row for row in rows if row["field_name"] == "material"]
    assert mismatch_rows[0]["status"] == "mismatch"
    assert mismatch_rows[0]["pid_value"] == "CS"
