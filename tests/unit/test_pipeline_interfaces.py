from check_int.adapters.ocr_engine import StubOcrEngine
from check_int.adapters.pdf_loader import PageImage, StubPdfLoader
from check_int.adapters.structured_extractor import StubStructuredExtractor
from check_int.adapters.vision_detector import DetectedRegion, StubVisionDetector
from check_int.domain.enums import DocumentType
from check_int.services.pipeline import DocumentProcessingPipeline


def test_stub_pdf_loader_returns_page_images() -> None:
    loader = StubPdfLoader()

    pages = loader.load_pdf("pid_sample.pdf")

    assert pages == [
        PageImage(page_no=1, source_path="pid_sample.pdf", image_ref="pid_sample.pdf#page=1")
    ]


def test_document_processing_pipeline_runs_end_to_end_with_stub_adapters() -> None:
    loader = StubPdfLoader(
        pages=[PageImage(page_no=1, source_path="pid_sample.pdf", image_ref="page-1")]
    )
    detector = StubVisionDetector(
        regions=[
            DetectedRegion(
                page_no=1,
                label="spec_box",
                bbox=(0, 0, 100, 100),
                crop_ref="crop-1",
            )
        ]
    )
    ocr = StubOcrEngine(text_by_crop={"crop-1": "TAG=P-401;SERVICE=Cooling Water"})
    extractor = StubStructuredExtractor(
        structured_output={"tag_no": "P-401", "service": "Cooling Water"}
    )

    pipeline = DocumentProcessingPipeline(loader, detector, ocr, extractor)

    result = pipeline.process_document("pid_sample.pdf", document_type=DocumentType.PID)

    assert len(result.pages) == 1
    assert len(result.regions) == 1
    assert result.raw_texts == ["TAG=P-401;SERVICE=Cooling Water"]
    assert result.structured_rows == [
        {
            "tag_no": "P-401",
            "service": "Cooling Water",
            "page_no": 1,
            "bbox": (0, 0, 100, 100),
            "image_path": "crop-1",
            "raw_text": "TAG=P-401;SERVICE=Cooling Water",
            "region_label": "spec_box",
        }
    ]
