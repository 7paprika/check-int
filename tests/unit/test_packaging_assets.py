from pathlib import Path


def test_packaging_spec_and_windows_smoke_doc_exist() -> None:
    assert Path("packaging/check_int.spec").exists()
    assert Path("docs/windows-smoke-test.md").exists()


def test_windows_packaging_docs_distinguish_linux_elf_from_windows_exe() -> None:
    smoke_doc = Path("docs/windows-smoke-test.md").read_text(encoding="utf-8")
    deployment_doc = Path("docs/offline-deployment-notes.md").read_text(encoding="utf-8")

    assert "Linux" in smoke_doc
    assert "ELF" in smoke_doc
    assert "Windows native" in smoke_doc
    assert "모델 포함 빌드" in deployment_doc
    assert "모델 미포함 빌드" in deployment_doc
