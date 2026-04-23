from pathlib import Path
from typing import Callable

from check_int.adapters.vision_detector import DetectedRegion


class StubOcrEngine:
    def __init__(self, text_by_crop: dict[str, str] | None = None) -> None:
        self._text_by_crop = text_by_crop or {}

    def extract_text(self, region: DetectedRegion) -> str:
        return self._text_by_crop.get(region.crop_ref, f"OCR:{region.crop_ref}")


class PaddleOcrEngine:
    def __init__(
        self,
        *,
        language: str = "en",
        use_gpu: bool = False,
        engine_factory: Callable[..., object] | None = None,
    ) -> None:
        self.language = language
        self.use_gpu = use_gpu
        self.engine_factory = engine_factory
        self._engine = None

    def extract_text(self, region: DetectedRegion) -> str:
        image_path = Path(region.crop_ref)
        if not image_path.exists():
            raise FileNotFoundError(region.crop_ref)

        engine = self._get_engine()
        result = engine.ocr(str(image_path), cls=True)
        lines: list[str] = []
        for block in result or []:
            for item in block or []:
                if len(item) >= 2:
                    text = item[1][0]
                    if text:
                        lines.append(str(text))
        return "\n".join(lines)

    def _get_engine(self):
        if self._engine is None:
            factory = self.engine_factory or self._build_engine
            self._engine = factory(use_angle_cls=True, lang=self.language, use_gpu=self.use_gpu)
        return self._engine

    def _build_engine(self, **kwargs):
        from paddleocr import PaddleOCR

        return PaddleOCR(**kwargs)
