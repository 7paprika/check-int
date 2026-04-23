from dataclasses import dataclass

from check_int.adapters.pdf_loader import PageImage


@dataclass(slots=True, eq=True)
class DetectedRegion:
    page_no: int
    label: str
    bbox: tuple[int, int, int, int]
    crop_ref: str


class StubVisionDetector:
    def __init__(self, regions: list[DetectedRegion] | None = None) -> None:
        self._regions = regions or []

    def detect_regions(self, page_image: PageImage) -> list[DetectedRegion]:
        if self._regions:
            return self._regions
        return [
            DetectedRegion(
                page_no=page_image.page_no,
                label="full_page",
                bbox=(0, 0, 100, 100),
                crop_ref=page_image.image_ref,
            )
        ]