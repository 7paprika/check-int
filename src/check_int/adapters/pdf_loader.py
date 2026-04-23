from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass(slots=True, eq=True)
class PageImage:
    page_no: int
    source_path: str
    image_ref: str


class StubPdfLoader:
    def __init__(self, pages: list[PageImage] | None = None) -> None:
        self._pages = pages

    def load_pdf(self, path: str) -> list[PageImage]:
        if self._pages is not None:
            return self._pages
        return [PageImage(page_no=1, source_path=path, image_ref=f"{path}#page=1")]


class MuPdfLoader:
    def __init__(self, *, output_dir: str | Path, dpi: int = 144) -> None:
        self.output_dir = Path(output_dir)
        self.dpi = dpi

    def load_pdf(self, path: str) -> list[PageImage]:
        pdf_path = Path(path)
        if not pdf_path.exists():
            raise FileNotFoundError(path)

        render_dir = self.output_dir / pdf_path.stem
        render_dir.mkdir(parents=True, exist_ok=True)

        pages: list[PageImage] = []
        document = fitz.open(pdf_path)
        try:
            matrix = fitz.Matrix(self.dpi / 72, self.dpi / 72)
            for index, page in enumerate(document, start=1):
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                image_path = render_dir / f"page-{index:04d}.png"
                pixmap.save(image_path)
                pages.append(
                    PageImage(
                        page_no=index,
                        source_path=str(pdf_path),
                        image_ref=str(image_path),
                    )
                )
        finally:
            document.close()

        return pages