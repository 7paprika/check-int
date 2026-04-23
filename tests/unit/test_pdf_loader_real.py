from pathlib import Path

import fitz
import pytest

from check_int.adapters.pdf_loader import MuPdfLoader, PageImage


def _create_sample_pdf(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "P-901 SAMPLE PAGE 1")
    page2 = doc.new_page()
    page2.insert_text((72, 72), "P-902 SAMPLE PAGE 2")
    doc.save(path)
    doc.close()


def test_mupdf_loader_renders_real_pdf_to_page_images(tmp_path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    _create_sample_pdf(pdf_path)

    loader = MuPdfLoader(output_dir=tmp_path / "renders", dpi=144)

    pages = loader.load_pdf(str(pdf_path))

    assert len(pages) == 2
    assert all(isinstance(page, PageImage) for page in pages)
    assert pages[0].page_no == 1
    assert pages[1].page_no == 2
    assert Path(pages[0].image_ref).exists()
    assert Path(pages[1].image_ref).exists()
    assert pages[0].source_path == str(pdf_path)


def test_mupdf_loader_rejects_missing_pdf_path(tmp_path) -> None:
    loader = MuPdfLoader(output_dir=tmp_path / "renders")

    with pytest.raises(FileNotFoundError):
        loader.load_pdf(str(tmp_path / "missing.pdf"))
