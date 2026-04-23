from dataclasses import dataclass


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