import pytest
from PIL import Image

from check_int.adapters.ocr_engine import PaddleOcrEngine
from check_int.adapters.vision_detector import DetectedRegion


class _FakePaddleOcr:
    def __init__(self, use_angle_cls: bool = True, lang: str = "en", use_gpu: bool = False):
        self.config = {
            "use_angle_cls": use_angle_cls,
            "lang": lang,
            "use_gpu": use_gpu,
        }

    def ocr(self, image_path: str, cls: bool = True):
        return [
            [
                [[[0, 0], [1, 0], [1, 1], [0, 1]], ("P-1101", 0.99)],
                [[[0, 0], [1, 0], [1, 1], [0, 1]], ("10 BAR", 0.98)],
            ]
        ]


def test_paddle_ocr_engine_extracts_joined_text(tmp_path) -> None:
    crop_path = tmp_path / "crop.png"
    Image.new("RGB", (100, 50), color="white").save(crop_path)
    region = DetectedRegion(page_no=1, label="spec_box", bbox=(0, 0, 100, 50), crop_ref=str(crop_path))

    engine = PaddleOcrEngine(engine_factory=_FakePaddleOcr)

    text = engine.extract_text(region)

    assert text == "P-1101\n10 BAR"


def test_paddle_ocr_engine_rejects_missing_crop_file(tmp_path) -> None:
    region = DetectedRegion(page_no=1, label="spec_box", bbox=(0, 0, 100, 50), crop_ref=str(tmp_path / "missing.png"))
    engine = PaddleOcrEngine(engine_factory=_FakePaddleOcr)

    with pytest.raises(FileNotFoundError):
        engine.extract_text(region)
