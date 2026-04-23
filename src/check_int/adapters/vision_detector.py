from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image

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


class YoloVisionDetector:
    def __init__(
        self,
        *,
        model_path: str,
        crop_dir: str | Path,
        confidence_threshold: float = 0.25,
        model_factory: Callable[[str], object] | None = None,
    ) -> None:
        self.model_path = model_path
        self.crop_dir = Path(crop_dir)
        self.confidence_threshold = confidence_threshold
        self.model_factory = model_factory

    def detect_regions(self, page_image: PageImage) -> list[DetectedRegion]:
        if self.model_factory is None and not Path(self.model_path).exists():
            raise FileNotFoundError(self.model_path)

        model = self.model_factory(self.model_path) if self.model_factory else self._build_model()
        results = model(page_image.image_ref, verbose=False)
        boxes = results[0].boxes
        names = results[0].names

        self.crop_dir.mkdir(parents=True, exist_ok=True)
        image = Image.open(page_image.image_ref)
        regions: list[DetectedRegion] = []

        for index, (xyxy, conf, cls_idx) in enumerate(zip(boxes.xyxy, boxes.conf, boxes.cls), start=1):
            confidence = float(conf)
            if confidence < self.confidence_threshold:
                continue
            x1, y1, x2, y2 = [int(value) for value in xyxy]
            crop_path = self.crop_dir / f"page-{page_image.page_no:04d}-det-{index:03d}.png"
            image.crop((x1, y1, x2, y2)).save(crop_path)
            regions.append(
                DetectedRegion(
                    page_no=page_image.page_no,
                    label=names[int(cls_idx)],
                    bbox=(x1, y1, x2, y2),
                    crop_ref=str(crop_path),
                )
            )

        image.close()
        return regions

    def _build_model(self):
        from ultralytics import YOLO

        return YOLO(self.model_path)
