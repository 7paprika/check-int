from pathlib import Path


def test_packaging_spec_and_windows_smoke_doc_exist() -> None:
    assert Path("packaging/check_int.spec").exists()
    assert Path("docs/windows-smoke-test.md").exists()
