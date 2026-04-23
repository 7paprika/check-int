from pathlib import Path

import pytest
from PIL import Image

from check_int.adapters.pdf_loader import PageImage
from check_int.adapters.vision_detector import YoloVisionDetector


class _FakeBoxes:
    def __init__(self) -> None:
        self.xyxy = [[10, 20, 110, 120], [5, 6, 25, 26]]
        self.conf = [0.9, 0.2]
        self.cls = [0, 1]


class _FakeResult:
    def __init__(self) -> None:
        self.boxes = _FakeBoxes()
        self.names = {0: "spec_box", 1: "table"}


class _FakeModel:
    def __call__(self, image_path: str, verbose: bool = False):
        return [_FakeResult()]


def test_yolo_detector_converts_model_output_to_detected_regions(tmp_path) -> None:
    image_path = tmp_path / "page.png"
    Image.new("RGB", (200, 200), color="white").save(image_path)
    page = PageImage(page_no=1, source_path="sample.pdf", image_ref=str(image_path))

    detector = YoloVisionDetector(
        model_path="dummy.pt",
        crop_dir=tmp_path / "crops",
        confidence_threshold=0.5,
        model_factory=lambda path: _FakeModel(),
    )

    regions = detector.detect_regions(page)

    assert len(regions) == 1
    assert regions[0].label == "spec_box"
    assert regions[0].bbox == (10, 20, 110, 120)
    assert Path(regions[0].crop_ref).exists()


def test_yolo_detector_raises_when_model_path_missing(tmp_path) -> None:
    image_path = tmp_path / "page.png"
    Image.new("RGB", (100, 100), color="white").save(image_path)
    page = PageImage(page_no=1, source_path="sample.pdf", image_ref=str(image_path))

    detector = YoloVisionDetector(model_path=str(tmp_path / "missing.pt"), crop_dir=tmp_path / "crops")

    with pytest.raises(FileNotFoundError):
        detector.detect_regions(page)
