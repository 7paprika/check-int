from check_int.adapters.vision_detector import DetectedRegion


class StubOcrEngine:
    def __init__(self, text_by_crop: dict[str, str] | None = None) -> None:
        self._text_by_crop = text_by_crop or {}

    def extract_text(self, region: DetectedRegion) -> str:
        return self._text_by_crop.get(region.crop_ref, f"OCR:{region.crop_ref}")