from dataclasses import dataclass, field

from check_int.adapters.pdf_loader import PageImage
from check_int.adapters.vision_detector import DetectedRegion
from check_int.domain.enums import DocumentType


@dataclass(slots=True)
class DocumentProcessingResult:
    pages: list[PageImage] = field(default_factory=list)
    regions: list[DetectedRegion] = field(default_factory=list)
    raw_texts: list[str] = field(default_factory=list)
    structured_rows: list[dict[str, str]] = field(default_factory=list)


class DocumentProcessingPipeline:
    def __init__(self, loader, detector, ocr_engine, structured_extractor) -> None:
        self.loader = loader
        self.detector = detector
        self.ocr_engine = ocr_engine
        self.structured_extractor = structured_extractor

    def process_document(
        self,
        path: str,
        *,
        document_type: DocumentType,
    ) -> DocumentProcessingResult:
        pages = self.loader.load_pdf(path)
        result = DocumentProcessingResult(pages=pages)

        for page in pages:
            regions = self.detector.detect_regions(page)
            result.regions.extend(regions)
            for region in regions:
                raw_text = self.ocr_engine.extract_text(region)
                result.raw_texts.append(raw_text)
                structured_row = self.structured_extractor.to_structured_fields(raw_text, document_type)
                structured_row.update(
                    {
                        "page_no": region.page_no,
                        "bbox": region.bbox,
                        "image_path": region.crop_ref,
                        "raw_text": raw_text,
                        "region_label": region.label,
                    }
                )
                result.structured_rows.append(structured_row)

        return result