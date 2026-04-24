import os


def test_qt_platform_defaults_to_offscreen_for_headless_tests() -> None:
    assert os.environ.get("QT_QPA_PLATFORM") == "offscreen"
