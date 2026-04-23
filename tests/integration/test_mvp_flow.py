import pandas as pd

from check_int.adapters.pdf_loader import PageImage
from check_int.adapters.vision_detector import DetectedRegion
from check_int.domain.enums import DocumentType
from check_int.services.pipeline import DocumentProcessingResult
from check_int.app.use_cases import IntegrityCheckUseCase


class FakePipeline:
    def __init__(self, structured_rows: list[dict[str, str]]) -> None:
        self.structured_rows = structured_rows

    def process_document(self, path: str, *, document_type: DocumentType) -> DocumentProcessingResult:
        return DocumentProcessingResult(
            pages=[PageImage(page_no=1, source_path=path, image_ref=f"{path}#page=1")],
            regions=[
                DetectedRegion(
                    page_no=1,
                    label="spec_box",
                    bbox=(0, 0, 100, 100),
                    crop_ref=f"{path}#crop",
                )
            ],
            raw_texts=[f"RAW:{document_type.value}"],
            structured_rows=self.structured_rows,
        )


def test_integrity_check_use_case_runs_end_to_end(tmp_path) -> None:
    eq_list_path = tmp_path / "eq_list.xlsx"
    pd.DataFrame(
        [
            {
                "tag_no": "P-501",
                "equipment_name": "Circulation Pump",
                "service": "Cooling Water",
                "material": "SS316",
                "design_pressure": "10 bar",
            }
        ]
    ).to_excel(eq_list_path, index=False)

    pid_pipeline = FakePipeline(
        [
            {
                "tag_no": "P-501",
                "equipment_name": "Circulation Pump",
                "service": "Cooling Water",
                "material": "CS",
                "design_pressure": "10 bar",
            }
        ]
    )
    datasheet_pipeline = FakePipeline(
        [
            {
                "tag_no": "P-501",
                "equipment_name": "Circulation Pump",
                "service": "Cooling Water",
                "material": "SS316",
                "design_pressure": "10 bar",
            }
        ]
    )

    use_case = IntegrityCheckUseCase(
        pid_pipeline=pid_pipeline,
        datasheet_pipeline=datasheet_pipeline,
    )

    rows = use_case.run(
        eq_list_path=eq_list_path,
        pid_path="pid_sample.pdf",
        datasheet_path="datasheet_sample.pdf",
    )

    assert len(rows) >= 3
    material_rows = [row for row in rows if row["field_name"] == "material"]
    assert material_rows[0]["tag_no"] == "P-501"
    assert material_rows[0]["status"] == "mismatch"
    assert material_rows[0]["pid_value"] == "CS"
    assert material_rows[0]["datasheet_value"] == "SS316"
